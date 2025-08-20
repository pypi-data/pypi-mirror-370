#!/usr/bin/env python3
"""
Session Registry: Define sessions as triggerable functions with automatic UI generation.

This module provides:
- @session_def decorator to define reusable sessions
- SessionRegistry to manage and serve sessions via web UI
- Automatic form generation from function parameters
- Real-time monitoring of running sessions
"""

import inspect
import json
import threading
import uuid
import os
import time
from functools import wraps
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from contextlib import contextmanager

from .orchestration import session, serve_session, pattern, batch, _current_session
from .polyagent import PolyAgent


# Global registry instance (created when first session is defined)
_global_registry = None


class SessionRegistry:
    """Manages all registered sessions and serves control panel UI."""
    
    def __init__(self):
        self.registered_sessions = {}
        self.running_sessions = {}
        self.session_counter = 0
        self._lock = threading.RLock()
        self._session_threads = {}  # Track threads for cancellation
        self._base_monitoring_port = 8766  # Base port for monitoring
        
    def _get_free_port(self):
        """Get a free port for monitoring server."""
        with self._lock:
            # Find first free port starting from base
            used_ports = {info.get("monitoring_port") for info in self.running_sessions.values() 
                         if info.get("monitoring_port")}
            
            port = self._base_monitoring_port
            while port in used_ports:
                port += 1
                if port > self._base_monitoring_port + 100:  # Limit search range
                    port = self._base_monitoring_port
                    break
            return port
    
    def register(self, session_func):
        """Register a session function (called by @session_def decorator)."""
        with self._lock:
            session_id = session_func._session_id
            self.registered_sessions[session_id] = {
                "func": session_func,
                "name": session_func._session_name,
                "description": session_func._session_description,
                "params": session_func._session_params,
                "category": session_func._session_category,
            }
            print(f"[SessionRegistry] Registered session: {session_func._session_name}")
    
    def trigger_session(self, session_id: str, params: Dict[str, Any]) -> str:
        """Trigger a session execution with given parameters."""
        if session_id not in self.registered_sessions:
            raise ValueError(f"Unknown session: {session_id}")
        
        session_info = self.registered_sessions[session_id]
        func = session_info["func"]
        
        # Generate unique execution ID
        exec_id = f"{session_id}-{uuid.uuid4().hex[:8]}"
        
        # Execute in background thread
        thread = threading.Thread(
            target=self._run_session,
            args=(func, params, exec_id),
            daemon=True,
            name=f"session-{exec_id}"
        )
        
        # Store thread reference for cancellation
        with self._lock:
            self._session_threads[exec_id] = thread
        
        thread.start()
        
        return exec_id
    
    def _run_session(self, func: Callable, params: Dict[str, Any], exec_id: str):
        """Execute session function with automatic context and logging."""
        print(f"[SessionRegistry] Starting session execution: {exec_id}")
        
        # Create session context with higher worker count for triggered sessions
        with session(max_workers=30) as s:
            # ALWAYS start real-time monitoring for each session
            port = self._get_free_port()
            
            # Start monitoring server and store references
            server, server_thread = serve_session(s, port=port)
            
            # Store reference for monitoring
            with self._lock:
                self.running_sessions[exec_id] = {
                    "session": s,
                    "start_time": time.time(),
                    "status": "running",
                    "params": params,
                    "monitoring_port": port,  # Store port for UI
                    "monitoring_server": server,  # Store server to shutdown later
                    "monitoring_thread": server_thread
                }
            print(f"\n{'='*60}")
            print(f"🔴 REAL-TIME MONITORING: http://localhost:{port}")
            print(f"Session ID: {exec_id}")
            print(f"{'='*60}\n")
            
            try:
                # Execute the session function
                result = func(**params)
                
                # Mark as completed
                with self._lock:
                    self.running_sessions[exec_id]["status"] = "completed"
                    self.running_sessions[exec_id]["result"] = result
                    self.running_sessions[exec_id]["end_time"] = time.time()
                    self.running_sessions[exec_id]["records"] = s.snapshot_records()  # Save final records
                
                print(f"\n{'='*60}")
                print(f"✅ Session completed: {exec_id}")
                print(f"📊 Pattern executions: {len(s.records)}")
                print(f"🔴 Monitoring was at: http://localhost:{port}")
                print(f"{'='*60}\n")
                
            except Exception as e:
                # Mark as failed
                with self._lock:
                    self.running_sessions[exec_id]["status"] = "failed"
                    self.running_sessions[exec_id]["error"] = str(e)
                    self.running_sessions[exec_id]["end_time"] = time.time()
                
                print(f"[SessionRegistry] Session failed: {exec_id} - {e}")
                raise
    
    def stop_session(self, exec_id: str) -> bool:
        """Stop a session (running or completed) and clean up resources."""
        with self._lock:
            if exec_id not in self.running_sessions:
                return False
            
            session_info = self.running_sessions[exec_id]
            
            # For completed sessions, just clean up
            if session_info["status"] == "completed":
                # Shutdown monitoring server
                if "monitoring_server" in session_info:
                    try:
                        server = session_info["monitoring_server"]
                        server.shutdown()  # Stop accepting requests
                        server.server_close()  # Close the socket - THIS is what frees the port!
                        print(f"[SessionRegistry] Shutdown monitoring server for completed session: {exec_id}")
                    except Exception as e:
                        print(f"[SessionRegistry] Error shutting down monitoring server: {e}")
                
                # Mark as stopped to free port
                session_info["status"] = "stopped"
                session_info["monitoring_port"] = None
                # Clean up from tracking
                del self.running_sessions[exec_id]
                if exec_id in self._session_threads:
                    del self._session_threads[exec_id]
                return True
            
            # For running sessions, cancel them
            elif session_info["status"] == "running":
                return self.cancel_session(exec_id)
            
            return False
    
    def cancel_session(self, exec_id: str) -> bool:
        """Force cancel a running session by killing its thread."""
        import ctypes
        
        with self._lock:
            if exec_id not in self.running_sessions:
                return False
            
            session_info = self.running_sessions[exec_id]
            if session_info["status"] != "running":
                return False
            
            # Mark as cancelled
            session_info["status"] = "cancelled"
            session_info["end_time"] = time.time()
            session_info["error"] = "Session was cancelled by user"
            
            # Shutdown monitoring server first
            if "monitoring_server" in session_info:
                try:
                    server = session_info["monitoring_server"]
                    server.shutdown()  # Stop accepting requests
                    server.server_close()  # Close the socket - THIS is what frees the port!
                    print(f"[SessionRegistry] Shutdown monitoring server for session: {exec_id}")
                except Exception as e:
                    print(f"[SessionRegistry] Error shutting down monitoring server: {e}")
            
            # Get the thread
            thread = self._session_threads.get(exec_id)
            
        if thread and thread.is_alive():
            print(f"[SessionRegistry] Force cancelling session: {exec_id}")
            
            # Force kill the thread using ctypes
            try:
                # Get thread ID - use ident which is available in all Python 3.x
                thread_id = thread.ident
                
                if not thread_id:
                    print(f"[SessionRegistry] Could not get thread ID")
                    return False
                
                # Force terminate thread
                print(f"[SessionRegistry] Attempting to kill thread with ID: {thread_id}")
                
                # Try to inject SystemExit exception
                res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(thread_id),
                    ctypes.py_object(KeyboardInterrupt)  # Use KeyboardInterrupt instead of SystemExit
                )
                
                if res == 0:
                    print(f"[SessionRegistry] Thread {thread_id} not found")
                    return False
                elif res > 1:
                    # If it returns a number greater than 1, we're in trouble
                    ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), None)
                    print(f"[SessionRegistry] Failed to kill thread cleanly")
                    return False
                else:
                    print(f"[SessionRegistry] Successfully cancelled session thread: {exec_id}")
                    
                    # Clean up thread reference and session tracking
                    with self._lock:
                        if exec_id in self._session_threads:
                            del self._session_threads[exec_id]
                        # Remove from running_sessions to free the port
                        if exec_id in self.running_sessions:
                            del self.running_sessions[exec_id]
                    
                    return True
                        
            except Exception as e:
                print(f"[SessionRegistry] Error killing thread: {e}")
                return False
        
        return False
    
    def get_session_status(self, exec_id: str) -> Dict[str, Any]:
        """Get status of a running or completed session."""
        with self._lock:
            if exec_id in self.running_sessions:
                info = self.running_sessions[exec_id]
                session_obj = info["session"]
                
                return {
                    "exec_id": exec_id,
                    "status": info["status"],
                    "params": info["params"],
                    "start_time": info["start_time"],
                    "end_time": info.get("end_time"),
                    "result": info.get("result"),
                    "error": info.get("error"),
                    "records": session_obj.snapshot_records() if session_obj else []
                }
        return None
    
    def serve_control_panel(self, host: str = "127.0.0.1", port: int = 8765):
        """Start web server for session control panel."""
        registry_ref = self
        
        class ControlPanelHandler(BaseHTTPRequestHandler):
            def log_message(self, fmt, *args):
                # Silence logs
                return
            
            def _send_json(self, obj):
                body = json.dumps(obj).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(body)
            
            def do_GET(self):
                if self.path == "/":
                    # Serve main control panel UI
                    html = self._generate_control_panel_html()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(html.encode())
                    
                elif self.path == "/api/sessions":
                    # Return all registered sessions
                    sessions = []
                    for sid, info in registry_ref.registered_sessions.items():
                        sessions.append({
                            "id": sid,
                            "name": info["name"],
                            "description": info["description"],
                            "category": info["category"],
                            "params": [
                                {"name": k, "type": v.__name__ if hasattr(v, '__name__') else str(v)}
                                for k, v in info["params"].items()
                            ]
                        })
                    self._send_json({"sessions": sessions})
                    
                elif self.path == "/api/running":
                    # Return all running sessions
                    running = []
                    with registry_ref._lock:
                        for exec_id, info in registry_ref.running_sessions.items():
                            running.append({
                                "exec_id": exec_id,
                                "status": info["status"],
                                "start_time": info["start_time"],
                                "params": info["params"],
                                "monitoring_port": info.get("monitoring_port")
                            })
                    self._send_json({"running": running})
                    
                elif self.path.startswith("/api/status/"):
                    # Get specific session status
                    exec_id = self.path.split("/")[-1]
                    status = registry_ref.get_session_status(exec_id)
                    if status:
                        self._send_json(status)
                    else:
                        self.send_response(404)
                        self.end_headers()
                        
                elif self.path.startswith("/session/"):
                    # Serve detailed session view
                    exec_id = self.path.split("/")[-1]
                    html = self._generate_session_detail_html(exec_id)
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(html.encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_POST(self):
                if self.path == "/api/trigger":
                    # Trigger a session
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length)
                    data = json.loads(body.decode("utf-8"))
                    
                    session_id = data["session_id"]
                    params = data["params"]
                    
                    try:
                        exec_id = registry_ref.trigger_session(session_id, params)
                        self._send_json({"success": True, "exec_id": exec_id})
                    except Exception as e:
                        self._send_json({"success": False, "error": str(e)})
                        
                elif self.path == "/api/stop":
                    # Stop a session (running or completed)
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length)
                    data = json.loads(body.decode("utf-8"))
                    
                    exec_id = data["exec_id"]
                    
                    success = registry_ref.stop_session(exec_id)
                    self._send_json({"success": success})
                    
                elif self.path == "/api/cancel":
                    # Cancel a running session (backward compatibility)
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length)
                    data = json.loads(body.decode("utf-8"))
                    
                    exec_id = data["exec_id"]
                    
                    success = registry_ref.cancel_session(exec_id)
                    self._send_json({"success": success})
                    
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_OPTIONS(self):
                # Handle CORS preflight
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()
            
            def _generate_session_detail_html(self, exec_id):
                """Generate HTML for detailed session view."""
                status = registry_ref.get_session_status(exec_id)
                if not status:
                    return "<h1>Session not found</h1>"
                
                return f'''<!DOCTYPE html>
<html>
<head>
    <title>Session Details: {exec_id}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 14px;
        }}
        .status-running {{ background: #fef3c7; color: #92400e; }}
        .status-completed {{ background: #d1fae5; color: #065f46; }}
        .status-failed {{ background: #fee2e2; color: #991b1b; }}
        .info-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .pattern-record {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #2563eb;
        }}
        .pattern-record.done {{
            border-left-color: #10b981;
        }}
        .agent-messages {{
            background: #f8fafc;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            font-family: monospace;
            font-size: 12px;
            max-height: 200px;
            overflow-y: auto;
        }}
        pre {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <h1>Session: {exec_id}</h1>
    
    <div class="info-card">
        <h2>Status: <span class="status-badge status-{status['status']}">{status['status']}</span></h2>
        <p><strong>Started:</strong> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(status['start_time']))}</p>
        {"<p><strong>Ended:</strong> " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(status['end_time'])) + "</p>" if status.get('end_time') else ""}
        <p><strong>Parameters:</strong></p>
        <pre>{json.dumps(status['params'], indent=2)}</pre>
        {"<p><strong>Result:</strong></p><pre>" + json.dumps(status.get('result'), indent=2) + "</pre>" if status.get('result') else ""}
        {"<p><strong>Error:</strong> " + status.get('error') + "</p>" if status.get('error') else ""}
    </div>
    
    <div class="info-card">
        <h2>Pattern Executions ({len(status['records'])})</h2>
        <div id="records-container"></div>
    </div>
    
    <script>
        const records = {json.dumps(status['records'])};
        
        function renderRecords() {{
            const container = document.getElementById('records-container');
            let html = '';
            
            records.forEach((record, idx) => {{
                html += `
                    <div class="pattern-record ${{record.status}}">
                        <h3>[${{idx + 1}}] ${{record.pattern}} - ${{record.status}}</h3>
                        <p><strong>Inputs:</strong> ${{JSON.stringify(record.inputs)}}</p>
                `;
                
                // Show agent messages if available
                if (record.agents && Object.keys(record.agents).length > 0) {{
                    html += '<p><strong>Agents:</strong></p>';
                    for (const [name, agent] of Object.entries(record.agents)) {{
                        html += `<div style="margin-left: 20px;">`;
                        html += `<strong>${{name}}</strong> (ID: ${{agent.id || 'unnamed'}})<br>`;
                        if (agent.messages && agent.messages.length > 0) {{
                            html += `<div class="agent-messages">`;
                            html += `Messages: ${{agent.messages.length}} total<br>`;
                            // Show last message preview
                            const lastMsg = agent.messages[agent.messages.length - 1];
                            if (lastMsg) {{
                                const preview = JSON.stringify(lastMsg).substring(0, 200);
                                html += `Last: ${{preview}}...`;
                            }}
                            html += `</div>`;
                        }}
                        html += `</div>`;
                    }}
                }}
                
                if (record.result) {{
                    html += `<p><strong>Result:</strong> ${{JSON.stringify(record.result).substring(0, 500)}}</p>`;
                }}
                
                html += '</div>';
            }});
            
            container.innerHTML = html || '<p>No pattern executions recorded</p>';
        }}
        
        renderRecords();
        
        // Auto-refresh if still running
        if ('{status['status']}' === 'running') {{
            setInterval(() => {{
                fetch('/api/status/{exec_id}')
                    .then(r => r.json())
                    .then(data => {{
                        if (data.status !== 'running') {{
                            location.reload();
                        }}
                    }});
            }}, 2000);
        }}
    </script>
</body>
</html>'''
            
            def _generate_control_panel_html(self):
                """Generate the control panel HTML."""
                return '''<!DOCTYPE html>
<html>
<head>
    <title>PolyCLI Session Control</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
            font-size: 13px;
            height: 100vh;
            overflow: hidden;
        }
        .app-header {
            background: white;
            border-bottom: 1px solid #e2e8f0;
            padding: 10px 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .app-header h1 {
            margin: 0;
            font-size: 18px;
            color: #1e293b;
        }
        .app-container {
            display: flex;
            height: calc(100vh - 50px);
        }
        .sidebar {
            width: 200px;
            background: white;
            border-right: 1px solid #e2e8f0;
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
        }
        .sidebar-header {
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
            font-weight: 600;
            color: #475569;
            font-size: 12px;
            text-transform: uppercase;
        }
        .session-list {
            list-style: none;
            padding: 0;
            margin: 0;
            overflow-y: auto;
            flex: 1;
        }
        .session-item {
            padding: 8px 12px;
            cursor: pointer;
            transition: all 0.15s;
            font-size: 12px;
            border-bottom: 1px solid #f1f5f9;
        }
        .session-item:hover {
            background: #f8fafc;
        }
        .session-item.active {
            background: #eff6ff;
            border-left: 3px solid #2563eb;
            padding-left: 9px;
        }
        .session-name {
            display: block;
            font-weight: 500;
            color: #1e293b;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .session-meta {
            font-size: 10px;
            color: #94a3b8;
            margin-top: 2px;
        }
        .param-input {
            margin: 5px 0;
        }
        .param-input label {
            display: inline-block;
            font-weight: 500;
            margin-bottom: 2px;
            font-size: 11px;
            color: #4b5563;
        }
        .param-input input {
            width: 100%;
            padding: 4px 6px;
            border: 1px solid #ddd;
            border-radius: 3px;
            font-size: 12px;
        }
        button {
            background: #2563eb;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            width: 100%;
        }
        button:hover {
            background: #1d4ed8;
        }
        button:disabled {
            background: #94a3b8;
            cursor: not-allowed;
        }
        .main-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: white;
        }
        .tabs {
            display: flex;
            border-bottom: 2px solid #e2e8f0;
            background: #f8fafc;
        }
        .tab {
            padding: 12px 24px;
            cursor: pointer;
            font-weight: 500;
            color: #64748b;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
            transition: all 0.2s;
        }
        .tab:hover {
            color: #475569;
        }
        .tab.active {
            color: #2563eb;
            border-bottom-color: #2563eb;
            background: white;
        }
        .tab-content {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        .tab-panel {
            display: none;
            height: 100%;
        }
        .tab-panel.active {
            display: block;
        }
        .monitoring-iframe {
            width: 100%;
            height: 100%;
            border: none;
            background: white;
        }
        .no-monitoring {
            text-align: center;
            padding: 40px;
            color: #94a3b8;
        }
        .sessions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
        }
        .running-item {
            padding: 12px;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-size: 12px;
            transition: all 0.2s;
        }
        .running-item:hover {
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .running-item strong {
            font-size: 12px;
            color: #1e293b;
        }
        .status-running { 
            border-color: #f59e0b;
            background: #fffbeb;
        }
        .status-completed { 
            border-color: #10b981;
            background: #f0fdf4;
        }
        .status-failed { 
            border-color: #ef4444;
            background: #fef2f2;
        }
        .status-cancelled { 
            border-color: #6b7280;
            background: #f9fafb;
        }
        .category-header {
            font-size: 13px;
            font-weight: 600;
            color: #64748b;
            margin: 10px 0 5px 0;
            padding: 3px 0;
            border-bottom: 1px solid #e2e8f0;
        }
        .monitor-link {
            display: inline-block;
            color: #dc2626;
            font-weight: bold;
            text-decoration: none;
            margin-top: 4px;
            font-size: 11px;
        }
        .monitor-link:hover {
            text-decoration: underline;
        }
        .cancel-btn {
            background: #ef4444;
            padding: 4px 8px;
            margin-top: 4px;
            font-size: 11px;
        }
        .popup-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.1);
            z-index: 999;
        }
        .popup {
            position: absolute;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            min-width: 250px;
            max-width: 350px;
            z-index: 1000;
        }
        .popup h4 {
            margin: 0 0 8px 0;
            font-size: 14px;
            color: #1e293b;
        }
        .popup-description {
            font-size: 11px;
            color: #64748b;
            margin-bottom: 10px;
            line-height: 1.4;
        }
        .popup-close {
            position: absolute;
            top: 8px;
            right: 8px;
            background: none;
            border: none;
            font-size: 16px;
            color: #94a3b8;
            cursor: pointer;
            padding: 0;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .popup-close:hover {
            color: #475569;
        }
        @media (max-width: 768px) {
            .main-container {
                grid-template-columns: 1fr;
            }
            .running-sessions {
                position: static;
            }
        }
    </style>
</head>
<body>
    <div class="app-header">
        <h1>🎮 PolyCLI Session Control</h1>
    </div>
    
    <div class="app-container">
        <aside class="sidebar">
            <div class="sidebar-header">
                Sessions
            </div>
            <ul id="sessions-container" class="session-list"></ul>
        </aside>
        
        <main class="main-area">
            <div class="tabs">
                <div class="tab active" onclick="switchTab('sessions')">
                    Active Sessions
                </div>
                <div class="tab" onclick="switchTab('monitoring')">
                    Monitoring
                </div>
            </div>
            
            <div class="tab-content">
                <div id="sessions-panel" class="tab-panel active">
                    <div id="running-container"></div>
                </div>
                
                <div id="monitoring-panel" class="tab-panel">
                    <iframe id="monitoring-frame" class="monitoring-iframe"></iframe>
                </div>
            </div>
        </main>
    </div>
    
    <div id="popup-overlay" class="popup-overlay" onclick="closePopup()"></div>
    <div id="popup" class="popup" style="display:none;">
        <button class="popup-close" onclick="closePopup()">×</button>
        <div id="popup-content"></div>
    </div>
    
    <script>
        let sessions = [];
        let runningPollingInterval;
        
        async function loadSessions() {
            const response = await fetch('/api/sessions');
            const data = await response.json();
            sessions = data.sessions;
            renderSessions();
        }
        
        function renderSessions() {
            const container = document.getElementById('sessions-container');
            
            // Group sessions by category
            const categories = {};
            sessions.forEach(session => {
                const cat = session.category || 'Uncategorized';
                if (!categories[cat]) categories[cat] = [];
                categories[cat].push(session);
            });
            
            let html = '';
            for (const [category, catSessions] of Object.entries(categories)) {
                html += `<li style="padding:8px 12px;font-weight:600;color:#94a3b8;font-size:10px;text-transform:uppercase;background:#f8fafc;">${category}</li>`;
                
                catSessions.forEach(session => {
                    html += `
                        <li class="session-item" 
                            onclick="showPopup('${session.id}', event)" 
                            title="${session.description}">
                            <span class="session-name">${session.name}</span>
                            <span class="session-meta">${session.params.length} params</span>
                        </li>
                    `;
                });
            }
            
            container.innerHTML = html;
        }
        
        function switchTab(tab) {
            // Update tab active states
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            
            // Update panel visibility
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            document.getElementById(tab + '-panel').classList.add('active');
        }
        
        function showPopup(sessionId, event) {
            const session = sessions.find(s => s.id === sessionId);
            if (!session) return;
            
            // Mark active item
            document.querySelectorAll('.session-item').forEach(el => el.classList.remove('active'));
            event.currentTarget.classList.add('active');
            
            // Build popup content
            let html = `
                <h4>${session.name}</h4>
                ${session.description ? `<p class="popup-description">${session.description}</p>` : ''}
                <form onsubmit="triggerSessionFromPopup(event, '${session.id}')">
            `;
            
            session.params.forEach(param => {
                const inputType = param.type === 'int' ? 'number' : 'text';
                html += `
                    <div class="param-input">
                        <label>${param.name} <span style="color:#94a3b8">(${param.type})</span></label>
                        <input name="${param.name}" type="${inputType}" required />
                    </div>
                `;
            });
            
            html += `
                <button type="submit" style="margin-top:8px">▶ Run Session</button>
            </form>`;
            
            // Update popup content
            document.getElementById('popup-content').innerHTML = html;
            
            // Position popup next to clicked item
            const popup = document.getElementById('popup');
            const rect = event.currentTarget.getBoundingClientRect();
            
            popup.style.display = 'block';
            popup.style.left = rect.right + 10 + 'px';
            popup.style.top = rect.top + 'px';
            
            // Adjust if popup goes off screen
            const popupRect = popup.getBoundingClientRect();
            if (popupRect.right > window.innerWidth - 20) {
                popup.style.left = rect.left - popupRect.width - 10 + 'px';
            }
            if (popupRect.bottom > window.innerHeight - 20) {
                popup.style.top = window.innerHeight - popupRect.height - 20 + 'px';
            }
            
            // Show overlay
            document.getElementById('popup-overlay').style.display = 'block';
        }
        
        function closePopup() {
            document.getElementById('popup').style.display = 'none';
            document.getElementById('popup-overlay').style.display = 'none';
            document.querySelectorAll('.session-item').forEach(el => el.classList.remove('active'));
        }
        
        async function triggerSessionFromPopup(event, sessionId) {
            event.preventDefault();
            await triggerSession(event, sessionId);
            closePopup();
        }
        
        async function triggerSession(event, sessionId) {
            event.preventDefault();
            
            const form = event.target;
            const formData = new FormData(form);
            const params = {};
            
            // Convert form data to proper types
            const session = sessions.find(s => s.id === sessionId);
            session.params.forEach(param => {
                let value = formData.get(param.name);
                if (param.type === 'int') {
                    value = parseInt(value);
                } else if (param.type === 'float') {
                    value = parseFloat(value);
                }
                params[param.name] = value;
            });
            
            // Disable button
            const button = form.querySelector('button');
            button.disabled = true;
            button.textContent = '...';
            
            try {
                const response = await fetch('/api/trigger', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        session_id: sessionId,
                        params: params
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    // Don't open broken session details page
                    // Just show success and user can click monitoring link
                    
                    // Start polling for updates
                    startPollingRunning();
                    
                    // Reset form
                    form.reset();
                    button.textContent = '✓';
                    setTimeout(() => {
                        button.disabled = false;
                        button.textContent = '▶ Run';
                    }, 1000);
                } else {
                    alert('Error: ' + data.error);
                    button.disabled = false;
                    button.textContent = '▶ Run';
                }
            } catch (e) {
                alert('Failed to trigger session: ' + e.message);
                button.disabled = false;
                button.textContent = '▶️ Run Session';
            }
        }
        
        async function loadRunning() {
            const response = await fetch('/api/running');
            const data = await response.json();
            
            const container = document.getElementById('running-container');
            if (data.running.length === 0) {
                container.innerHTML = '<div class="no-monitoring">No active sessions. Start a session from the sidebar.</div>';
                // Stop polling if nothing running
                if (runningPollingInterval) {
                    clearInterval(runningPollingInterval);
                    runningPollingInterval = null;
                }
            } else {
                let html = '<div class="sessions-grid">';
                data.running.forEach(session => {
                    const startTime = new Date(session.start_time * 1000).toLocaleTimeString();
                    const monitoringUrl = session.monitoring_port ? 
                        `http://localhost:${session.monitoring_port}` : null;
                    
                    const shortId = session.exec_id.split('-').slice(-2).join('-');
                    const params = Object.entries(session.params)
                        .map(([k,v]) => `${k}:${typeof v === 'string' && v.length > 20 ? v.substring(0,20)+'...' : v}`)
                        .join(', ');
                    
                    html += `
                        <div class="running-item status-${session.status}" 
                             style="${session.monitoring_port ? 'cursor:pointer;' : ''} position:relative;"
                             onclick="${session.monitoring_port ? `showMonitoring(${session.monitoring_port}, '${session.exec_id}')` : ''}">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <strong title="${session.exec_id}">${shortId}</strong>
                                <span style="color:#6b7280; font-size:11px;">${startTime}</span>
                            </div>
                            <div style="color:#4b5563; font-size:11px; margin:4px 0;">${params}</div>
                            ${(session.status === 'running' || session.status === 'completed') ? 
                                `<button onclick="stopSession('${session.exec_id}', event)" 
                                         style="position:absolute; top:8px; right:8px; width:20px; height:20px; 
                                                padding:0; background:#ef4444; border:none; border-radius:3px; 
                                                cursor:pointer; display:flex; align-items:center; justify-content:center;
                                                font-size:14px; color:white; line-height:1;"
                                         title="${session.status === 'running' ? 'Cancel session' : 'Stop monitoring'}">
                                    ×
                                </button>` : ''}
                        </div>
                    `;
                });
                html += '</div>';
                container.innerHTML = html;
            }
        }
        
        function startPollingRunning() {
            if (!runningPollingInterval) {
                loadRunning();
                runningPollingInterval = setInterval(loadRunning, 2000);
            }
        }
        
        function showMonitoring(port, sessionId) {
            // Switch to monitoring tab
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab')[1].classList.add('active');
            
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            document.getElementById('monitoring-panel').classList.add('active');
            
            // Load iframe
            const iframe = document.getElementById('monitoring-frame');
            iframe.src = `http://localhost:${port}`;
        }
        
        async function stopSession(execId, event) {
            if (event) {
                event.stopPropagation();
            }
            if (!confirm(`Stop session ${execId} and release resources?`)) {
                return;
            }
            
            try {
                const response = await fetch('/api/stop', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({exec_id: execId})
                });
                
                const data = await response.json();
                if (data.success) {
                    loadRunning(); // Refresh the list
                } else {
                    alert('Failed to stop session');
                }
            } catch (e) {
                alert('Error stopping session: ' + e.message);
            }
        }
        
        // Keep old function for compatibility
        async function cancelSession(execId, event) {
            if (event) {
                event.stopPropagation();
            }
            if (!confirm(`Are you sure you want to cancel session ${execId}?`)) {
                return;
            }
            
            try {
                const response = await fetch('/api/cancel', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({exec_id: execId})
                });
                
                const data = await response.json();
                if (data.success) {
                    alert('Session cancelled successfully');
                    loadRunning(); // Refresh the list
                } else {
                    alert('Failed to cancel session');
                }
            } catch (e) {
                alert('Error cancelling session: ' + e.message);
            }
        }
        
        // Initial load
        loadSessions();
        loadRunning();
    </script>
</body>
</html>'''
        
        server = ThreadingHTTPServer((host, port), ControlPanelHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        
        print(f"[SessionRegistry] Control panel running at http://{host}:{port}")
        return server, thread


def session_def(
    name: str = None,
    description: str = "",
    params: Dict[str, type] = None,
    category: str = "General"
):
    """
    Decorator that turns a function into a triggerable session.
    
    Args:
        name: Display name for the session
        description: Description shown in UI
        params: Parameter types for UI form generation
        category: Category for organizing sessions in UI
    
    Example:
        @session_def(
            name="Analyze Codebase",
            description="Analyze Python files for issues",
            params={"path": str, "max_files": int},
            category="Code Analysis"
        )
        def analyze_codebase(path: str, max_files: int = 10):
            agent = PolyAgent()
            # ... patterns run here ...
    """
    
    def decorator(func):
        # Extract parameter info from function signature if not provided
        if params is None:
            sig = inspect.signature(func)
            extracted_params = {}
            for param_name, param in sig.parameters.items():
                if param.annotation != inspect.Parameter.empty:
                    extracted_params[param_name] = param.annotation
                else:
                    extracted_params[param_name] = str
        else:
            extracted_params = params
        
        # Store metadata
        func._session_id = func.__name__
        func._session_name = name or func.__name__.replace("_", " ").title()
        func._session_description = description or func.__doc__ or ""
        func._session_params = extracted_params
        func._session_category = category
        func._is_session_def = True
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if we're already in a session context
            current = _current_session.get()
            
            if current is None:
                # Not in session - create one automatically
                print(f"[session_def] Auto-creating session context for {func._session_name}")
                with session() as s:
                    # Optional: auto-serve UI if configured
                    if os.environ.get("AUTO_SERVE_SESSION_UI", "").lower() == "true":
                        serve_session(s)
                    
                    # Execute function in session context
                    return func(*args, **kwargs)
            else:
                # Already in session context (e.g., triggered from registry)
                return func(*args, **kwargs)
        
        # Auto-register with global registry
        global _global_registry
        if _global_registry is None:
            _global_registry = SessionRegistry()
        _global_registry.register(wrapper)
        
        return wrapper
    
    return decorator


# Convenience function to get global registry
def get_registry() -> SessionRegistry:
    """Get the global session registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = SessionRegistry()
    return _global_registry


