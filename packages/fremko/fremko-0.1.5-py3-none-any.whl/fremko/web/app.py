from __future__ import annotations

import asyncio
import io
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from fremko.ws import server as ws_server
from fremko.web.executor import execute_code_with_persona

logger = logging.getLogger("droidrun")

# Get the directory where this file is located
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


"""
WebSocket JSON Message Format:

All messages are JSON objects with the following required field:
- type: string - The message type

Supported message types:

1. ping: Health check message
   Request: {"type": "ping", "timestamp": <number>}
   Response: {"type": "pong", "status": "success", "message": "pong", "timestamp": <number>, "original_message": <object>}

2. broadcast: Send message to all connected clients
   Request: {"type": "broadcast", "content": <string>, "timestamp": <number>}
   Response: {"type": "broadcast_sent", "status": "success", "message": "Message broadcasted to N clients", "timestamp": <number>}
   Broadcast: {"type": "broadcast", "status": "success", "content": <string>, "timestamp": <number>}

3. client_status: Get current client status
   Request: {"type": "client_status", "timestamp": <number>}
   Response: {"type": "client_status_response", "status": "success", "data": {"count": <number>, "clients": <array>}, "timestamp": <number>}

4. agent_command: Agent-related commands
   Request: {"type": "agent_command", "client_id": <string>, "command": <string>, "timestamp": <number>}
   Supported commands:
   - get_status: Get agent status and todos
     Response: {"type": "agent_status_response", "status": "success", "client_id": <string>, "data": {"status": <object>, "todos": <array>}, "timestamp": <number>}

5. device_event: Real-time device event updates (server-initiated broadcast)
   Broadcast: {"type": "device_event", "status": "success", "client_id": <string>, "device_info": <object>, "agent_data": {"is_success": <boolean>, "is_complete": <boolean>, "current_step": <string>, "goal": <string>, "is_running": <boolean>, "active_goal": <string>}, "timestamp": <number>}

6. task_update: Real-time task manager updates (server-initiated broadcast)
   Broadcast: {"type": "task_update", "status": "success", "client_id": <string>, "event_type": <string>, "device_info": <object>, "task_data": {"tasks": <array>, "goal_completed": <boolean>, "goal_message": <string>, "total_tasks": <number>, "completed_tasks": <number>, "failed_tasks": <number>, "pending_tasks": <number>}, "triggered_by": {"description": <string>, "status": <string>, "agent_type": <string>}, "timestamp": <number>}

Error responses:
{"type": "error", "status": "error", "message": <string>, "timestamp": <number>}

Connection established:
{"type": "connection", "status": "connected", "message": "WebSocket connection established", "timestamp": <number>}
"""


class WebSocketManager:
    """Manages WebSocket connections for JSON message communication"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept and store new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send message to WebSocket: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Send message to all connected WebSocket clients"""
        if not self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to broadcast to WebSocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()


def _get_clients_map():
    if ws_server.server_instance is None:
        raise HTTPException(status_code=503, detail="WebSocket server not started")
    return ws_server.server_instance.clients


def _get_client_or_404(client_id: str):
    clients = _get_clients_map()
    client = clients.get(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


def create_app() -> FastAPI:
    app = FastAPI(title="Fremko Control Panel", version="0.1.0")
    # Serve static assets (css/js)
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})
    
    @app.get("/executor", response_class=HTMLResponse)
    async def executor_page(request: Request):
        return templates.TemplateResponse("executor.html", {"request": request})

    # ------------------------------------------------------------------
    # Control-plane API
    # ------------------------------------------------------------------
    @app.get("/api/clients")
    async def list_clients():
        clients = _get_clients_map()

        async def _ping(client):
            try:
                # Await pong with a short timeout
                await asyncio.wait_for(client.ws.ping(), timeout=0.8)
                return True
            except Exception:
                return not getattr(client.ws, "closed", True)

        # Ping all clients concurrently
        connected_list = await asyncio.gather(*[_ping(c) for c in clients.values()], return_exceptions=False)

        # Merge info + connectivity
        data = []
        for (c, is_connected) in zip(clients.values(), connected_list):
            info = c.get_device_info()
            info["connected"] = bool(is_connected)
            data.append(info)
        return {"count": len(data), "clients": data}

    @app.get("/api/clients/{client_id}")
    async def get_client(client_id: str):
        client = _get_client_or_404(client_id)
        # Ping this client as part of refresh
        is_connected = True
        try:
            await asyncio.wait_for(client.ws.ping(), timeout=0.8)
        except Exception:
            is_connected = not getattr(client.ws, "closed", True)
        info = client.get_device_info()
        info["connected"] = bool(is_connected)
        return info

    @app.post("/api/clients/{client_id}/refresh_device_info")
    async def refresh_device_info(client_id: str):
        client = _get_client_or_404(client_id)
        try:
            info = await client.tools.get_device_info()
            if isinstance(info, dict):
                client.device_info.update(info)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to refresh device info: {e}")
        return client.get_device_info()

    @app.get("/api/config")
    async def get_config():
        if ws_server.server_instance is None:
            raise HTTPException(status_code=503, detail="Server not started")
        return ws_server.server_instance.agent_config

    @app.put("/api/config")
    async def update_config(payload: Dict[str, Any]):
        if ws_server.server_instance is None:
            raise HTTPException(status_code=503, detail="Server not started")
        ws_server.server_instance.agent_config.update(payload or {})
        return ws_server.server_instance.agent_config
    
    @app.post("/api/executor/execute")
    async def execute_code(payload: Dict[str, Any]):
        """Execute Python code using DEFAULT persona and a client's WsTools."""
        code = payload.get("code")
        client_id = payload.get("client_id")
        if not code:
            raise HTTPException(status_code=400, detail="'code' is required")
        if not client_id:
            raise HTTPException(status_code=400, detail="'client_id' is required")

        # Get client's tools (WsTools instance)
        client = _get_client_or_404(client_id)
        tools = client.tools
        if tools is None:
            raise HTTPException(status_code=503, detail="Client tools not available")

        # Execute with provided tools, filtered by DEFAULT persona
        result = await execute_code_with_persona(code, tools)
        return result

    # ------------------------------------------------------------------
    # Device actions
    # ------------------------------------------------------------------
    @app.post("/api/clients/{client_id}/goal")
    async def post_goal(client_id: str, payload: Dict[str, Any]):
        client = _get_client_or_404(client_id)
        goal = payload.get("goal")
        if not goal:
            raise HTTPException(status_code=400, detail="'goal' is required")
        overrides = {k: v for k, v in payload.items() if k != "goal"}
        await client.start_goal(goal, overrides)
        return {"ok": True}

    @app.get("/api/clients/{client_id}/screenshot")
    async def get_screenshot(client_id: str):
        client = _get_client_or_404(client_id)
        try:
            fmt, img_bytes = await client.tools.take_screenshot()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Screenshot failed: {e}")
        media_type = "image/png" if fmt.upper() == "PNG" else "image/jpeg"
        return StreamingResponse(io.BytesIO(img_bytes), media_type=media_type)

    @app.get("/api/clients/{client_id}/state")
    async def get_state(client_id: str):
        client = _get_client_or_404(client_id)
        data = await client.tools.get_state()
        return JSONResponse(content=data)

    @app.get("/api/clients/{client_id}/status")
    async def get_agent_status(client_id: str):
        client = _get_client_or_404(client_id)
        
        # Determine agent status
        status = {"status": "ready", "message": "Ready"}
        if client.is_running:
            status = {"status": "running", "message": client.active_goal or "Running..."}
        
        # Get todos from task manager if available
        todos = []
        if hasattr(client, 'task_manager') and client.task_manager:
            all_tasks = client.task_manager.get_all_tasks()
            todos = [
                {
                    "description": task.description,
                    "status": task.status,
                    "agent_type": task.agent_type
                }
                for task in all_tasks
            ]
            
            # Check if goal is completed
            if client.task_manager.goal_completed:
                if client.task_manager.message:
                    status = {"status": "completed", "message": client.task_manager.message}
                else:
                    status = {"status": "completed", "message": "Goal completed"}
        
        return {"status": status, "todos": todos}

    @app.post("/api/clients/{client_id}/tap")
    async def tap(client_id: str, payload: Dict[str, Any]):
        client = _get_client_or_404(client_id)
        try:
            x = int(payload.get("x"))
            y = int(payload.get("y"))
        except Exception:
            raise HTTPException(status_code=400, detail="x and y are required integers")
        res = await client.tools.tap_by_coordinates(x, y)
        return {"result": res}

    @app.post("/api/clients/{client_id}/swipe")
    async def swipe(client_id: str, payload: Dict[str, Any]):
        client = _get_client_or_404(client_id)
        try:
            sx = int(payload.get("start_x"))
            sy = int(payload.get("start_y"))
            ex = int(payload.get("end_x"))
            ey = int(payload.get("end_y"))
            duration_ms = int(payload.get("duration_ms", 300))
        except Exception:
            raise HTTPException(status_code=400, detail="start_x,start_y,end_x,end_y must be integers")
        res = await client.tools.swipe(sx, sy, ex, ey, duration_ms)
        return {"result": res}

    @app.post("/api/clients/{client_id}/gesture_path")
    async def gesture_path(client_id: str, payload: Dict[str, Any]):
        client = _get_client_or_404(client_id)
        points = payload.get("points")
        if not isinstance(points, list) or len(points) < 2:
            raise HTTPException(status_code=400, detail="'points' must be a list with at least 2 items")
        duration_ms = payload.get("duration_ms")
        # Let tools handle validation/normalization and duration inference
        res = await client.tools.gesture_path(points=points, duration_ms=duration_ms)
        return {"result": res}

    @app.post("/api/clients/{client_id}/input")
    async def input_text(client_id: str, payload: Dict[str, Any]):
        client = _get_client_or_404(client_id)
        text = payload.get("text", "")
        res = await client.tools.input_text_action(text)
        return {"result": res}

    @app.post("/api/clients/{client_id}/key")
    async def press_key(client_id: str, payload: Dict[str, Any]):
        client = _get_client_or_404(client_id)
        try:
            keycode = int(payload.get("keycode"))
        except Exception:
            raise HTTPException(status_code=400, detail="keycode is required integer")
        res = await client.tools.press_key(keycode)
        return {"result": res}

    @app.post("/api/clients/{client_id}/start_app")
    async def start_app(client_id: str, payload: Dict[str, Any]):
        client = _get_client_or_404(client_id)
        package = payload.get("package")
        activity = payload.get("activity")
        if not package:
            raise HTTPException(status_code=400, detail="package is required")
        res = await client.tools.start_app(package=package, activity=activity)
        return {"result": res}

    @app.get("/api/clients/{client_id}/apps")
    async def list_apps(client_id: str):
        client = _get_client_or_404(client_id)
        try:
            apps = await client.tools.list_apps()
            return apps
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to list apps: {e}")

    # ------------------------------------------------------------------
    # Stream control endpoints (Control WS → device)
    # ------------------------------------------------------------------
    @app.post("/api/clients/{client_id}/stream/start")
    async def start_stream(client_id: str, payload: Dict[str, Any]):
        client = _get_client_or_404(client_id)
        url = payload.get("url")
        fps = int(payload.get("fps", 12))
        max_width = int(payload.get("max_width", 720))
        quality = int(payload.get("quality", 75))
        fmt = payload.get("format")
        res = await client.tools.start_stream(url=url, fps=fps, max_width=max_width, quality=quality, stream_format=fmt)
        return {"result": res}

    @app.post("/api/clients/{client_id}/stream/update")
    async def update_stream(client_id: str, payload: Dict[str, Any]):
        client = _get_client_or_404(client_id)
        fps = payload.get("fps")
        quality = payload.get("quality")
        max_width = payload.get("max_width")
        fmt = payload.get("format")
        res = await client.tools.update_stream(fps=fps, quality=quality, max_width=max_width, stream_format=fmt)
        return {"result": res}

    @app.post("/api/clients/{client_id}/stream/stop")
    async def stop_stream(client_id: str):
        client = _get_client_or_404(client_id)
        # Stop device-side encoder first
        res = await client.tools.stop_stream()
        # Then force finalize capture file (if any) on server side
        try:
            serial = str((client.device_info or {}).get("serial") or "")
            if ws_server.server_instance and serial:
                session = ws_server.server_instance.serial_to_stream.get(serial)
                if session:
                    session.stop_capture()
        except Exception:
            pass
        return {"result": res}

    # ------------------------------------------------------------------
    # Preview WebSocket (browser ← server). Sends JPEG frames.
    # Path: /ws/preview/{client_id}
    # ------------------------------------------------------------------
    @app.websocket("/ws/preview/{client_id}")
    async def preview_ws(websocket: WebSocket, client_id: str):
        await websocket.accept()
        try:
            clients = _get_clients_map()
            client = clients.get(client_id)
            if not client:
                await websocket.close(code=4404)
                return
            serial = str((client.device_info or {}).get("serial") or "")
            if not serial:
                await websocket.close(code=4405)
                return

            # Send basic info
            await websocket.send_json({"type": "preview_info", "serial": serial})

            last_seq = -1
            while True:
                server = ws_server.server_instance
                if server is None:
                    await asyncio.sleep(0.2)
                    continue
                session = server.serial_to_stream.get(serial)
                if session is None:
                    # No active stream yet; small backoff
                    await asyncio.sleep(0.2)
                    continue

                # Wait for a new frame (or send the latest if we missed many)
                async with session.condition:
                    await session.condition.wait_for(lambda: session.frame_seq != last_seq)
                    last_seq = session.frame_seq
                try:
                    frame = session.frames[-1]
                except Exception:
                    continue
                # Send as binary JPEG
                await websocket.send_bytes(frame)
        except WebSocketDisconnect:
            return
        except Exception as e:
            logger.error(f"preview_ws error: {e}", exc_info=True)
            try:
                await websocket.close(code=1011)
            except Exception:
                pass
            return

    # ------------------------------------------------------------------
    # JSON message WebSocket endpoint
    # Path: /ws/messages
    # ------------------------------------------------------------------
    @app.websocket("/ws/messages")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket_manager.connect(websocket)
        
        # Send welcome message
        welcome_message = {
            "type": "connection",
            "status": "connected",
            "message": "WebSocket connection established",
            "timestamp": asyncio.get_event_loop().time()
        }
        await websocket_manager.send_personal_message(welcome_message, websocket)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    await handle_websocket_message(message, websocket)
                except json.JSONDecodeError:
                    error_response = {
                        "type": "error",
                        "status": "error",
                        "message": "Invalid JSON format",
                        "timestamp": asyncio.get_event_loop().time()
                    }
                    await websocket_manager.send_personal_message(error_response, websocket)
                except Exception as e:
                    logger.error(f"Error handling WebSocket message: {e}", exc_info=True)
                    error_response = {
                        "type": "error",
                        "status": "error",
                        "message": f"Message processing failed: {str(e)}",
                        "timestamp": asyncio.get_event_loop().time()
                    }
                    await websocket_manager.send_personal_message(error_response, websocket)
        except WebSocketDisconnect:
            websocket_manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}", exc_info=True)
            websocket_manager.disconnect(websocket)

    return app


async def handle_websocket_message(message: Dict[str, Any], websocket: WebSocket):
    """Handle incoming WebSocket JSON messages"""
    
    message_type = message.get("type")
    
    if not message_type:
        response = {
            "type": "error",
            "status": "error",
            "message": "Missing 'type' field in message",
            "timestamp": asyncio.get_event_loop().time()
        }
        await websocket_manager.send_personal_message(response, websocket)
        return
    
    # Handle different message types
    if message_type == "ping":
        response = {
            "type": "pong",
            "status": "success",
            "message": "pong",
            "timestamp": asyncio.get_event_loop().time(),
            "original_message": message
        }
        await websocket_manager.send_personal_message(response, websocket)
    
    elif message_type == "broadcast":
        # Broadcast message to all connected clients
        content = message.get("content", "")
        broadcast_message = {
            "type": "broadcast",
            "status": "success",
            "content": content,
            "timestamp": asyncio.get_event_loop().time()
        }
        await websocket_manager.broadcast(broadcast_message)
        
        # Send confirmation to sender
        confirmation = {
            "type": "broadcast_sent",
            "status": "success",
            "message": f"Message broadcasted to {len(websocket_manager.active_connections)} clients",
            "timestamp": asyncio.get_event_loop().time()
        }
        await websocket_manager.send_personal_message(confirmation, websocket)
    
    elif message_type == "client_status":
        # Send current client status
        try:
            clients = _get_clients_map()
            client_data = []
            for client in clients.values():
                info = client.get_device_info()
                info["connected"] = True  # Simplified for now
                client_data.append(info)
            
            response = {
                "type": "client_status_response",
                "status": "success",
                "data": {
                    "count": len(client_data),
                    "clients": client_data
                },
                "timestamp": asyncio.get_event_loop().time()
            }
            await websocket_manager.send_personal_message(response, websocket)
        except Exception as e:
            error_response = {
                "type": "error",
                "status": "error",
                "message": f"Failed to get client status: {str(e)}",
                "timestamp": asyncio.get_event_loop().time()
            }
            await websocket_manager.send_personal_message(error_response, websocket)
    
    elif message_type == "agent_command":
        # Handle agent-related commands
        client_id = message.get("client_id")
        command = message.get("command")
        
        if not client_id or not command:
            response = {
                "type": "error",
                "status": "error",
                "message": "Missing 'client_id' or 'command' field",
                "timestamp": asyncio.get_event_loop().time()
            }
            await websocket_manager.send_personal_message(response, websocket)
            return
        
        try:
            client = _get_client_or_404(client_id)
            
            if command == "get_status":
                # Get agent status for specific client
                status = {"status": "ready", "message": "Ready"}
                if client.is_running:
                    status = {"status": "running", "message": client.active_goal or "Running..."}
                
                todos = []
                if hasattr(client, 'task_manager') and client.task_manager:
                    all_tasks = client.task_manager.get_all_tasks()
                    todos = [
                        {
                            "description": task.description,
                            "status": task.status,
                            "agent_type": task.agent_type
                        }
                        for task in all_tasks
                    ]
                    
                    if client.task_manager.goal_completed:
                        if client.task_manager.message:
                            status = {"status": "completed", "message": client.task_manager.message}
                        else:
                            status = {"status": "completed", "message": "Goal completed"}
                    elif client.is_running:
                        status = {"status": "running", "message": client.log_handler.current_step}
                    else:
                        status = {"status": "ready", "message": "Ready"}

                response = {
                    "type": "agent_status_response",
                    "status": "success",
                    "client_id": client_id,
                    "data": {
                        "status": status,
                        "todos": todos
                    },
                    "timestamp": asyncio.get_event_loop().time()
                }
                await websocket_manager.send_personal_message(response, websocket)
            
            else:
                response = {
                    "type": "error",
                    "status": "error",
                    "message": f"Unknown agent command: {command}",
                    "timestamp": asyncio.get_event_loop().time()
                }
                await websocket_manager.send_personal_message(response, websocket)
        
        except HTTPException as e:
            response = {
                "type": "error",
                "status": "error",
                "message": f"Client error: {e.detail}",
                "timestamp": asyncio.get_event_loop().time()
            }
            await websocket_manager.send_personal_message(response, websocket)
    
    else:
        # Unknown message type
        response = {
            "type": "error",
            "status": "error",
            "message": f"Unknown message type: {message_type}",
            "supported_types": ["ping", "broadcast", "client_status", "agent_command"],
            "timestamp": asyncio.get_event_loop().time()
        }
        await websocket_manager.send_personal_message(response, websocket)


# Convenience app object for uvicorn dotted path
app = create_app()


