# orchestration.py
"""
Top-level pattern/session tracing + pause-before-next + message injection.
Now with:
- Stable record IDs
- Server-Sent Events (SSE) push updates (no flicker)
- Preact-based keyed UI (via ui/monitor.html + ui/monitor.js)
- Light theme only

Behavior (pause-before-next):
- Click "Pause" -> the *next* top-level @pattern call blocks at entry.
- While blocked, you can Inject messages to any agent (always appended to end).
- Click "Resume" -> queued injections are drained into agent params, 'before' is snapshotted,
  pattern runs, 'after' is snapshotted, record marked done.

HTTP endpoints:
  GET  /              -> ui/monitor.html (bundled next to this file)
  GET  /static/*      -> files under ui/
  GET  /records       -> initial state {records, paused}
  GET  /events        -> SSE stream of events: record-start, record-finish, paused
  POST /pause         -> {}
  POST /resume        -> {}
  POST /inject        -> {"agent_id","text"} -> {}
"""

import inspect
import copy
import json
import threading
from collections import defaultdict
from contextvars import ContextVar
from contextlib import contextmanager
from functools import wraps
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import mimetypes
import os
from typing import Optional
import queue
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from .message import MessageList

# ---- session state ----
_current_session = ContextVar("current_session", default=None)
# Thread-local storage for batch metadata to avoid race conditions
_batch_metadata = ContextVar("batch_metadata", default=None)
# Thread-local call depth to track nested patterns without race conditions
_call_depth = ContextVar("call_depth", default=0)


class Session:
    """Holds top-level pattern records, control plane, and an SSE broadcaster."""
    def __init__(self, max_workers=10):  # @@@development: Default 10 workers is conservative for I/O-bound LLM calls. Could scale to 50-200 for better parallelism since threads mostly wait on API responses. Consider dynamic scaling based on workload type.
        # Each record: {
        #   id: int,
        #   pattern: str,
        #   status: "running"|"done",
        #   inputs: dict,
        #   agents: {param_name: {id, before, after|None}},
        #   result: any | None
        # }
        self.records = []
        # Removed self.depth - now using thread-local _call_depth
        self._lock = threading.RLock()

        # Pause-before-next + inbox (agent_id -> [text, ...])
        self.pause_event = threading.Event()
        self.inbox = defaultdict(list)

        # SSE broadcaster: list of per-client queues
        self._clients = []
        self._next_id = 1
        
        # Batch execution support
        self._batch_queue = []
        self._batching = False
        self._batch_results = []
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._batch_counter = 0  # Track batch groups
        self._current_batch_id = None  # Current batch being executed

    # ---- SSE broadcaster helpers ----
    def _publish(self, event: dict):
        """Broadcast a dict event to all connected SSE clients."""
        with self._lock:
            clients = list(self._clients)
        for q in clients:
            try:
                q.put_nowait(event)
            except queue.Full:
                # drop if a client is too slow
                pass

    def add_client(self, maxsize: int = 100) -> queue.Queue:
        q = queue.Queue(maxsize=maxsize)
        with self._lock:
            self._clients.append(q)
        return q

    def remove_client(self, q: queue.Queue):
        with self._lock:
            if q in self._clients:
                self._clients.remove(q)

    # ---- recording ----
    def _next_rec_id(self) -> int:
        with self._lock:
            rid = self._next_id
            self._next_id += 1
            return rid

    def begin_record(self, rec: dict) -> int:
        """Append a running record and publish record-start."""
        if "id" not in rec or rec["id"] is None:
            rec["id"] = self._next_rec_id()
        with self._lock:
            self.records.append(rec)
            idx = len(self.records) - 1
        # Publish 'record-start' with light coercion (ensure JSON-compat)
        self._publish({"type": "record-start", "record": _coerce_record_jsonable(rec)})
        return idx

    def finish_record(self, idx: int, after_map: dict, result):
        """Update with final messages and result, mark done, publish record-finish."""
        with self._lock:
            if 0 <= idx < len(self.records):
                rec = self.records[idx]
                # Update with latest full messages for each agent
                for name, meta in rec.get("agents", {}).items():
                    meta["messages"] = after_map.get(name, [])
                rec["result"] = result
                rec["status"] = "done"
                out = _coerce_record_jsonable(rec)
        # publish outside lock
        self._publish({"type": "record-finish", "record": out})

    def snapshot_records(self):
        # deep copy for safe serving
        with self._lock:
            return copy.deepcopy(self.records)

    # ---- control plane ----
    def request_pause(self):
        self.pause_event.set()
        self._publish({"type": "paused", "value": True})

    def clear_pause(self):
        self.pause_event.clear()
        self._publish({"type": "paused", "value": False})

    def is_paused(self) -> bool:
        return self.pause_event.is_set()

    def summon_agents(self, *agents):
        """Register agents to make them immediately visible in the UI for injection."""
        # Create a special initialization record
        agent_map = {}
        for i, agent in enumerate(agents):
            aid = getattr(agent, "id", None)
            if aid:  # Only include agents with IDs
                # Get current messages - same as in the pattern wrapper
                messages = agent.messages.normalize_for_display() if hasattr(agent.messages, 'normalize_for_display') else agent.messages
                agent_map[f"agent_{i}"] = {
                    "id": aid,
                    "messages": messages
                }
        
        if agent_map:
            rec = {
                "pattern": "summon_agents",
                "status": "done",
                "inputs": {},
                "agents": agent_map,
                "result": f"Summoned {len(agent_map)} agent(s)"
            }
            self.begin_record(rec)
            # No need to call finish_record since we set status="done"
            
    def inject(self, agent_id: str, text: str):
        # Always append to end (no position support by design)
        if not text:
            return
        with self._lock:
            self.inbox[agent_id or "unnamed"].append(text)
        # optional: could publish an 'injected' event with counts

    def drain_into(self, agent) -> int:
        """Append queued injections (if any) to the end of agent.messages. Returns count drained."""
        aid = getattr(agent, "id", None)
        if aid is None:
            return 0  # Don't drain into agents without IDs
        with self._lock:
            pending = self.inbox.get(aid, [])
            self.inbox[aid] = []
        drained = 0
        for text in pending:
            if hasattr(agent, "add_user_message"):
                agent.add_user_message(text, position="end")  # force append
            else:
                agent.messages.append({"role": "user", "content": text})
            drained += 1
        return drained

    def wait_gate(self, agents: dict):
        """Pause-before-next gate. Blocks while paused, then drains injections BEFORE 'before' snapshot."""
        while self.is_paused():
            time.sleep(0.05)
        for ag in agents.values():
            self.drain_into(ag)

    def __str__(self):
        lines = []
        for rec in self.records:
            lines.append(f"------------- {rec['pattern']} ({rec.get('status','?')}) -------------")
            for param_name, meta in rec["agents"].items():
                agent_id = meta.get("id") or "unnamed"
                lines.append(f"{param_name}: {agent_id}")
            lines.append("")  # blank line between blocks
        named_ids = {
            meta["id"]
            for rec in self.records
            for meta in rec["agents"].values()
            if meta.get("id")
        }
        lines.append("------------- statistics -------------")
        lines.append(f"number of named agents: {len(named_ids)}")
        lines.append(f"number of patterns executed: {len(self.records)}")
        return "\n".join(lines)
    
    def execute_batch(self):
        """Execute all queued patterns in parallel and return results."""
        if not self._batch_queue:
            return []
        
        # Assign batch ID for this group
        batch_id = self._batch_counter
        self._batch_counter += 1
        
        # Publish batch-start event
        self._publish({
            "type": "batch-start",
            "batch_id": batch_id,
            "size": len(self._batch_queue)
        })
        
        # Submit all patterns to thread pool with batch tracking
        futures = []
        
        # Create execution function factory to avoid closure issues
        def create_executor(batch_id, batch_idx, batch_size):
            """Create an executor function with captured batch metadata"""
            def execute_with_batch_context(f, a, k, session_obj):
                # Set the session context for this thread
                token = _current_session.set(session_obj)
                # Set batch metadata in thread-local storage
                metadata_token = _batch_metadata.set({
                    'batch_id': batch_id,
                    'batch_index': batch_idx,
                    'batch_size': batch_size
                })
                try:
                    result = f(*a, **k)
                    return result
                finally:
                    _batch_metadata.reset(metadata_token)
                    _current_session.reset(token)
            return execute_with_batch_context
        
        for i, (func, args, kwargs) in enumerate(self._batch_queue):
            # Create a unique executor for this pattern with its specific batch metadata
            executor = create_executor(batch_id, i, len(self._batch_queue))
            
            future = self._executor.submit(
                executor,
                func, args, kwargs,
                self  # Pass the session object
            )
            futures.append((future, func.__name__))
        
        # Clear the queue
        self._batch_queue = []
        
        # Collect results as they complete
        results = []
        for future, name in futures:
            try:
                result = future.result(timeout=300)  # 5 minute timeout
                results.append(result)
            except Exception as e:
                print(f"Pattern {name} failed in batch execution: {e}")
                results.append(None)
        
        # Don't send batch-complete event here - let the UI determine
        # batch completion based on all individual pattern completions
        # This avoids the race condition where batch shows "done" but
        # some patterns are still "running"
        
        return results


@contextmanager
def session(max_workers=10):  # @@@development: Inherits conservative default. For API-heavy workloads, consider max_workers=50-100
    """with session() as s: ...  s.records has snapshots for top-level patterns only."""
    s = Session(max_workers=max_workers)
    token = _current_session.set(s)
    try:
        yield s
    finally:
        _current_session.reset(token)


@contextmanager
def batch():
    """Batch patterns for parallel execution.
    
    Usage:
        with batch():
            analyze(agent1, file1)  # Queued
            analyze(agent2, file2)  # Queued
            analyze(agent3, file3)  # Queued
        # All execute in parallel here
    """
    s = _current_session.get()
    if not s:
        raise RuntimeError("batch() requires an active session context")
    
    # Start batching mode
    old_batching = s._batching
    s._batching = True
    
    try:
        yield
    finally:
        # Execute all queued patterns in parallel
        results = s.execute_batch()
        s._batch_results = results
        s._batching = old_batching


# ---- helpers ----
def _is_agent(x):
    # Minimal duck-typing: anything with a 'messages' attribute counts as an agent.
    return hasattr(x, "messages")

def _split_agents_and_inputs(bound_arguments):
    """Split parameters into agents and non-agent inputs.
    
    Handles single agents, lists of agents, and dicts of agents.
    
    Returns:
        agents: dict of {name: agent} where name can be "param", "param[0]", or "param[key]"
        inputs: dict of non-agent parameters
    """
    agents = {}
    inputs = {}
    
    for param_name, value in bound_arguments.items():
        if _is_agent(value):
            # Single agent
            agents[param_name] = value
            
        elif isinstance(value, list):
            # Check if it's a list containing agents
            has_agents = False
            for i, item in enumerate(value):
                if _is_agent(item):
                    agents[f"{param_name}[{i}]"] = item
                    has_agents = True
            
            # If no agents found, it's a regular input
            if not has_agents:
                inputs[param_name] = value
                    
        elif isinstance(value, dict):
            # Check if it's a dict containing agent values
            has_agents = False
            for key, item in value.items():
                if _is_agent(item):
                    agents[f"{param_name}[{key}]"] = item
                    has_agents = True
            
            # If no agents found, it's a regular input
            if not has_agents:
                inputs[param_name] = value
        else:
            # Regular non-agent parameter
            inputs[param_name] = value
    
    return agents, inputs


def _coerce_jsonable(x):
    try:
        json.dumps(x)
        return x
    except TypeError:
        return repr(x)


def _coerce_record_jsonable(rec: dict) -> dict:
    """Deep-ish coercion to keep SSE payloads JSON serializable."""
    out = copy.deepcopy(rec)
    if "inputs" in out:
        out["inputs"] = {
            k: (v if isinstance(v, (str, int, float, bool, list, dict, type(None))) else repr(v))
            for k, v in out["inputs"].items()
        }
    if "result" in out:
        out["result"] = _coerce_jsonable(out["result"])
    return out


def pattern(func):
    """Decorator: tracks pattern execution in session context if available, otherwise runs normally."""
    @wraps(func)
    def wrapper(*args, _from_batch=False, **kwargs):
        s: Session = _current_session.get()
        
        # Check if we're in batch mode and not being called from batch execution
        if s and s._batching and not _from_batch:
            # Queue this pattern wrapper for batch execution with _from_batch flag
            kwargs_with_flag = kwargs.copy()
            kwargs_with_flag['_from_batch'] = True
            s._batch_queue.append((wrapper, args, kwargs_with_flag))
            # Return placeholder indicating pattern was batched
            return f"<Batched: {func.__name__}>"
        
        # If no session context, just run the function normally
        if s is None:
            return func(*args, **kwargs)
        
        # Session context exists - do tracking
        current_depth = _call_depth.get()
        is_top_level = (current_depth == 0)
        _call_depth.set(current_depth + 1)
        rec_idx = None
        try:
            if not is_top_level:
                return func(*args, **kwargs)

            # Extract batch metadata from thread-local storage
            metadata = _batch_metadata.get()
            if metadata:
                batch_id = metadata.get('batch_id')
                batch_index = metadata.get('batch_index')
                batch_size = metadata.get('batch_size')
            else:
                batch_id = None
                batch_index = None
                batch_size = None
            
            # Remove _from_batch from kwargs before binding (it's not a func parameter)
            kwargs_for_func = {k: v for k, v in kwargs.items() if k != '_from_batch'}
            
            # Bind args to names so we can split agent vs non-agent params.
            bound = inspect.signature(func).bind_partial(*args, **kwargs_for_func)
            bound.apply_defaults()
            
            # Split into agents (including from lists/dicts) and regular inputs
            agents, inputs = _split_agents_and_inputs(bound.arguments)

            # Pause gate then drain queued injections
            s.wait_gate(agents)

            # Always capture full messages (not diffs) - but only for agents with IDs
            snap_messages = {
                name: ag.messages.normalize_for_display() if hasattr(ag.messages, 'normalize_for_display') else ag.messages 
                for name, ag in agents.items() 
                if getattr(ag, "id", None) is not None  # Only track agents with explicit IDs
            }

            # Publish a "running" record immediately (and store it)
            running_rec = {
                "id": None,  # assigned in begin_record
                "pattern": func.__name__,
                "status": "running",
                "inputs": inputs,
                "agents": {
                    name: {
                        "id": getattr(ag, "id", None),
                        "messages": snap_messages.get(name, []),  # Empty if not tracked
                    } for name, ag in agents.items()
                    if getattr(ag, "id", None) is not None  # Only include agents with IDs
                },
                "result": None,
                "batch_id": batch_id,  # Add batch tracking
                "batch_index": batch_index,
                "batch_size": batch_size,
            }
            rec_idx = s.begin_record(running_rec)

            try:
                # Execute pattern (with _from_batch removed from kwargs)
                result = func(*args, **kwargs_for_func)

                # Capture full messages after execution - only for agents with IDs
                snap_after = {
                    name: ag.messages.normalize_for_display() if hasattr(ag.messages, 'normalize_for_display') else ag.messages 
                    for name, ag in agents.items()
                    if getattr(ag, "id", None) is not None
                }
                s.finish_record(rec_idx, snap_after, result)

                return result
            except Exception as e:
                # Pattern failed - still need to finish the record - only for agents with IDs
                snap_after = {
                    name: ag.messages.normalize_for_display() if hasattr(ag.messages, 'normalize_for_display') else ag.messages 
                    for name, ag in agents.items()
                    if getattr(ag, "id", None) is not None
                }
                s.finish_record(rec_idx, snap_after, f"Error: {str(e)}")
                raise  # Re-raise so batch execution can handle it
        finally:
            _call_depth.set(current_depth)  # Restore previous depth
    return wrapper


# ---- HTTP server (serves packaged UI + SSE) ----

def serve_session(s: Session, host: str = "127.0.0.1", port: int = 8765):
    """
    Start a tiny HTTP server to display current session records and accept controls.
    Serves a bundled light-theme UI from ./ui/ next to this file.
    Returns (server, thread).
    """
    session_ref = s  # capture in closure

    PKG_DIR = os.path.dirname(__file__)
    STATIC_DIR = os.path.join(PKG_DIR, "ui")
    UI_FILE = os.path.join(STATIC_DIR, "monitor.html")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # silence access logs
            return
        
        def handle(self):
            """Override to silence Windows socket errors during normal disconnects"""
            try:
                super().handle()
            except (ConnectionResetError, ConnectionAbortedError, OSError) as e:
                # These are normal on Windows when browser closes/refreshes
                import sys
                if sys.platform == "win32" and hasattr(e, 'winerror'):
                    if e.winerror in [10053, 10054]:
                        pass  # Silently ignore expected Windows socket errors
                    else:
                        raise
                else:
                    raise

        def _send_bytes(self, status: int, ctype: str, data: bytes):
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(data)

        def _send_json(self, obj):
            body = json.dumps(obj).encode("utf-8")
            self._send_bytes(200, "application/json; charset=utf-8", body)

        def do_GET(self):
            # UI index
            if self.path in ("/", "/index.html"):
                if os.path.exists(UI_FILE):
                    with open(UI_FILE, "rb") as f:
                        self._send_bytes(200, "text/html; charset=utf-8", f.read())
                else:
                    self._send_bytes(
                        200,
                        "text/html; charset=utf-8",
                        b"<!doctype html><body style='background:#f8fafc;color:#111;font-family:sans-serif;margin:20px'><h1>Top-level Pattern Calls</h1><p>Missing ui/monitor.html</p></body>",
                    )
                return

            # Static assets
            if self.path.startswith("/static/"):
                rel = self.path[len("/static/"):]
                safe_rel = os.path.normpath(rel).replace("\\", "/")
                if safe_rel.startswith(".."):
                    self.send_response(403); self.end_headers(); return
                fp = os.path.join(STATIC_DIR, safe_rel)
                if os.path.isfile(fp):
                    ctype, _ = mimetypes.guess_type(fp)
                    ctype = ctype or "application/octet-stream"
                    with open(fp, "rb") as f:
                        self._send_bytes(200, ctype, f.read())
                else:
                    self.send_response(404); self.end_headers()
                return

            # Initial data
            if self.path == "/records":
                data = session_ref.snapshot_records()
                # Coerce JSONability
                data = [_coerce_record_jsonable(r) for r in data]
                self._send_json({"records": data, "paused": session_ref.is_paused()})
                return

            # SSE stream
            if self.path == "/events":
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.end_headers()

                q = session_ref.add_client()
                # send initial paused state event
                try:
                    init_evt = {"type": "paused", "value": session_ref.is_paused()}
                    self.wfile.write(b"data: " + json.dumps(init_evt).encode("utf-8") + b"\n\n")
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError) as e:
                    # Client disconnected during initial setup
                    session_ref.remove_client(q)
                    return
                except Exception as e:
                    print(f"SSE: Error sending initial event: {e}")
                    session_ref.remove_client(q)
                    return

                try:
                    while True:
                        try:
                            evt = q.get(timeout=15.0)
                            payload = json.dumps(evt).encode("utf-8")
                            self.wfile.write(b"data: " + payload + b"\n\n")
                            self.wfile.flush()
                        except queue.Empty:
                            # keep-alive comment
                            try:
                                self.wfile.write(b": keep-alive\n\n")
                                self.wfile.flush()
                            except (BrokenPipeError, ConnectionResetError, OSError) as e:
                                # Client disconnected - normal on Windows
                                import sys
                                if sys.platform == "win32" and hasattr(e, 'winerror'):
                                    if e.winerror in [10053, 10054]:
                                        pass  # Expected on Windows, don't print
                                break
                            except Exception as e:
                                print(f"SSE: Error sending keep-alive: {e}")
                                break
                except (BrokenPipeError, ConnectionResetError, OSError) as e:
                    # Normal client disconnection
                    import sys
                    if sys.platform == "win32" and hasattr(e, 'winerror'):
                        if e.winerror not in [10053, 10054]:
                            print(f"SSE: Unexpected Windows error {e.winerror}: {e}")
                    pass
                except Exception as e:
                    print(f"SSE: Unexpected error in event loop: {e}")
                finally:
                    session_ref.remove_client(q)
                return

            self.send_response(404); self.end_headers()

        def do_POST(self):
            def read_json():
                n = int(self.headers.get("Content-Length", "0") or "0")
                raw = self.rfile.read(n) if n else b""
                try:
                    return json.loads(raw.decode("utf-8")) if raw else {}
                except Exception:
                    return {}

            if self.path == "/pause":
                session_ref.request_pause()
                self._send_json({})
                return

            if self.path == "/resume":
                session_ref.clear_pause()
                self._send_json({})
                return

            if self.path == "/inject":
                payload = read_json()
                agent_id = payload.get("agent_id") or "unnamed"
                text = payload.get("text") or ""
                session_ref.inject(agent_id, text)
                self._send_json({})
                return

            self.send_response(404); self.end_headers()

    server = ThreadingHTTPServer((host, port), Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server, t

