"""client.py - Helper representing a single phone connection handled by WsServer.

Every time a phone connects to the WebSocket server we create one ``WsClient``
instance that owns both the underlying ``websockets`` connection *and* a fully
initialised :class:`~fremko.tools.ws.WsTools` wrapper.

Keeping this inside its dedicated ``fremko.ws`` package avoids further
cluttering the ``fremko.tools`` namespace.
"""
from __future__ import annotations

import asyncio
import base64
import logging
import json
import asyncio
from typing import Any, Dict, TYPE_CHECKING, Optional
from uuid import uuid4

import websockets
from websockets import WebSocketServerProtocol

if TYPE_CHECKING:
    from fremko.ws.server import WsServer

from fremko.agent.droid import DroidAgent
from fremko.agent.utils.llm_picker import load_llm
from fremko.tools.ws import WsTools
from fremko.agent.context.task_manager import TaskManager
from fremko.cli.logs import LogHandler

logger = logging.getLogger("droidrun")

# Import websocket manager for broadcasting device events
try:
    from fremko.web.app import websocket_manager
except ImportError:
    websocket_manager = None
    logger.warning("WebSocket manager not available for device event broadcasting")


class WsClient:
    """Represents a single client connection to the WebSocket server."""

    def __init__(self, websocket: WebSocketServerProtocol, server: "WsServer"):
        self.ws = websocket
        self.server = server
        self.id = str(uuid4())
        self.tools = WsTools(websocket, asyncio.get_running_loop())
        # Concurrency/state management per client
        self._state_lock = asyncio.Lock()
        self.active_goal: Optional[str] = None
        self.is_running: bool = False
        # Device metadata reported by the phone
        self.device_info: Dict[str, Any] = {}
        # Optional per-client task tracking (todo_list semantics via TaskManager)
        self.task_manager = TaskManager()
        self.todo_list = self.task_manager.get_all_tasks()
        self.log_handler = LogHandler()

    async def handle_connection(self):
        """Main loop to handle a client connection."""
        try:
            # On connect: proactively request device info without blocking recv loop
            asyncio.create_task(self._proactive_fetch_device_info())
            while True:
                message = await self.ws.recv()
                # Process sequentially to ensure only one recv() consumer
                await self.process_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {self.id} connection closed.")
            try:
                # Release any pending tool waits and terminate the current workflow run
                self.tools.notify_disconnect("Client disconnected")
            except Exception:
                logger.debug("Failed to notify tools about disconnect", exc_info=True)
        except Exception as e:
            logger.error(f"Error in client {self.id} connection: {e}", exc_info=True)

    async def process_message(self, message: str | bytes):
        """
        Process an incoming message from the client.

        Args:
            message (str | bytes): The message received from the client.
        """
        try:
            data = json.loads(message)
            message_type = data.get("type")

            if message_type == "goal":
                await self.handle_goal(data)
            else:
                # If this action_result announces a following binary frame, pull it now
                if (
                    isinstance(data, dict)
                    and data.get("type") == "action_result"
                ):
                    payload = data.get("data") or {}
                    # Handle case where payload is a list (e.g., list_apps returns array)
                    if isinstance(payload, list):
                        byte_length = None
                    else:
                        byte_length = payload.get("byte_length")
                    if isinstance(byte_length, int) and byte_length > 0:
                        try:
                            binary_frame = await self.ws.recv()
                            if isinstance(binary_frame, (bytes, bytearray)):
                                b64 = base64.b64encode(binary_frame).decode("ascii")
                                data["data"] = {"format": "JPEG", "base64": b64}
                        except Exception:
                            # Best-effort; fall through to routing whatever we have
                            pass

                self.tools._route_message(data)
        except json.JSONDecodeError:
            logger.warning(f"Received non-JSON message from {self.id}: {message!r}")
        except Exception as e:
            logger.error(f"Error processing message from {self.id}: {e}", exc_info=True)

    async def handle_goal(self, payload: Dict[str, Any]):
        """
        Handle a 'goal' message from the client.

        Args:
            payload (Dict[str, Any]): The payload of the 'goal' message.
        """
        goal = payload.get("goal")
        if not goal:
            logger.warning(f"Received goal message with no goal from {self.id}")
            return

        # Enforce single active goal per client
        async with self._state_lock:
            if self.is_running:
                logger.warning(
                    f"Client {self.id} already running goal: {self.active_goal}; rejecting new goal: {goal}"
                )
                return
            self.is_running = True
            self.active_goal = goal

        logger.info(f"Received goal from {self.id}: {goal}")
        self.log_handler.goal = goal
        self.log_handler.current_step = "Initializing..."
        self.log_handler.is_completed = False
        self.log_handler.is_success = False
        agent_config = self._prepare_agent_config(payload)

        # Run the agent on the same asyncio loop as the websocket server
        async def _runner():
            try:
                await self._run_agent_async(goal, agent_config)
            finally:
                async with self._state_lock:
                    self.is_running = False
                    self.active_goal = None

        asyncio.create_task(_runner())

    # ------------------------------------------------------------------
    # Helpers for HTTP control plane
    # ------------------------------------------------------------------
    def get_device_info(self) -> Dict[str, Any]:
        """Return best-effort metadata about the connected device."""
        return {
            **self.device_info,
            "id": self.id,
            "active_goal": self.active_goal,
            "is_running": self.is_running,
        }

    async def start_goal(self, goal: str, payload_overrides: Optional[Dict[str, Any]] = None) -> None:
        """Public method used by the HTTP API to start an agent run for this client."""
        payload = {"goal": goal}
        if payload_overrides:
            payload.update(payload_overrides)
        await self.handle_goal(payload)

    async def _proactive_fetch_device_info(self) -> None:
        """Request device info and store it, expecting an action_result response."""
        try:
            info = await self.tools.get_device_info()
            if isinstance(info, dict):
                self.device_info.update(info)
                # Register serial for video stream association
                serial = str(self.device_info.get("serial") or "").strip()
                if serial:
                    try:
                        self.server.register_serial(serial, self)
                    except Exception:
                        logger.debug("Failed to register device serial with server", exc_info=True)
        except Exception:
            logger.debug("Proactive device info fetch failed", exc_info=True)

    def _prepare_agent_config(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare the configuration for the DroidAgent.

        Args:
            payload (Dict[str, Any]): The payload from the 'goal' message.

        Returns:
            Dict[str, Any]: The configuration for the DroidAgent.
        """
        # Start with server defaults
        config = self.server.agent_config.copy()

        # Merge with client-provided parameters
        config.update({
            "provider": payload.get("provider", config.get("provider")),
            "model": payload.get("model", config.get("model")),
            "base_url": payload.get("base_url", config.get("base_url")),
            "api_base": payload.get("api_base", config.get("api_base")),
            "steps": int(payload.get("steps", config.get("steps", 150))),
            "timeout": int(payload.get("timeout", 1000)),
            "reasoning": bool(payload.get("reasoning", config.get("reasoning", False))),
            "reflection": bool(payload.get("reflection", config.get("reflection", False))),
            "tracing": bool(payload.get("tracing", config.get("tracing", False))),
            "debug": bool(payload.get("debug", config.get("debug", False))),
            "vision": bool(payload.get("vision", config.get("vision", True))),  # Default to True for WS
        })
        
        # Merge kwargs
        kwargs = config.get("kwargs", {})
        kwargs.update(payload.get("kwargs", {}))
        config["kwargs"] = kwargs

        return config

    def _run_agent_sync(self, goal: str, config: Dict[str, Any]):
        # Deprecated: we now run the agent on the same asyncio loop
        raise RuntimeError("_run_agent_sync should not be used in single-loop mode")

    async def _run_agent_async(self, goal: str, config: Dict[str, Any]):
        """
        Asynchronous method to initialize and run the DroidAgent.

        Args:
            goal (str): The goal for the agent.
            config (Dict[str, Any]): The configuration for the agent.
        """
        provider_name = config.get("provider")
        model = config.get("model")
        base_url = config.get("base_url")
        api_base = config.get("api_base")
        kwargs = config.get("kwargs", {})

        llm = load_llm(
            provider_name=provider_name,
            model=model,
            base_url=base_url,
            api_base=api_base,
            **kwargs,
        )

        # New TaskManager instance per goal run to ensure isolation
        tm = TaskManager()
        
        # Register our task manager callback to broadcast task updates
        tm.add_callback(self.task_manager_callback)
        
        # Update instance task manager reference for external access
        self.task_manager = tm
        
        droid_agent = DroidAgent(
            goal=goal,
            llm=llm,
            tools=self.tools,
            max_steps=config.get("steps"),
            timeout=config.get("timeout"),
            vision=config.get("vision"),
            reasoning=config.get("reasoning"),
            reflection=config.get("reflection"),
            enable_tracing=config.get("tracing"),
            debug=config.get("debug"),
            task_manager=tm,
        )

        logger.info(f"Starting agent for goal: {goal}")
        runner = droid_agent.run()
        async for events in runner.stream_events():
            self.log_handler.handle_event(events)
            await self.event_change_callback(events)

        logger.info(f"Agent finished for goal: {goal}")

    async def event_change_callback(self, event):
        """
        Callback function called when agent events change.
        Broadcasts device event updates to all connected web clients.
        
        Args:
            event: The event data from the agent
        """
        if websocket_manager is None:
            return  # WebSocket manager not available
        
        # Prepare device event message
        device_event_message = {
            "type": "device_event",
            "status": "success",
            "client_id": self.id,
            "device_info": {
                "id": self.id,
                "serial": self.device_info.get("serial", ""),
                "device_name": self.device_info.get("device_name", ""),
                "brand": self.device_info.get("brand", ""),
                "model": self.device_info.get("model", "")
            },
            "agent_data": {
                "is_success": self.log_handler.is_success,
                "is_complete": self.log_handler.is_completed,
                "current_step": self.log_handler.current_step,
                "goal": self.log_handler.goal,
                "is_running": self.is_running,
                "active_goal": self.active_goal
            },
            "timestamp": asyncio.get_event_loop().time()
        }
        
        try:
            # Broadcast to all connected web clients
            await websocket_manager.broadcast(device_event_message)
            logger.debug(f"Broadcasted device event for client {self.id}: step='{self.log_handler.current_step}', complete={self.log_handler.is_completed}, success={self.log_handler.is_success}")
        except Exception as e:
            logger.error(f"Failed to broadcast device event: {e}", exc_info=True)

    async def task_manager_callback(self, event_type: str, task):
        """
        Callback function called when task manager events change.
        Fetches all tasks and broadcasts updates to all connected web clients.
        
        Args:
            event_type: Type of event (e.g., "complete_task", "fail_task", "set_tasks_with_agents")
            task: The task object that triggered the event
        """
        if websocket_manager is None:
            return  # WebSocket manager not available
        
        try:
            # Fetch all current tasks from task manager
            all_tasks = self.task_manager.get_all_tasks()
            
            # Convert tasks to serializable format
            tasks_data = []
            for t in all_tasks:
                task_dict = {
                    "description": t.description,
                    "status": t.status,
                    "agent_type": t.agent_type,
                    "message": t.message,
                    "failure_reason": t.failure_reason
                }
                tasks_data.append(task_dict)
            
            # Prepare task update message
            task_update_message = {
                "type": "task_update",
                "status": "success",
                "client_id": self.id,
                "event_type": event_type,
                "device_info": {
                    "id": self.id,
                    "serial": self.device_info.get("serial", ""),
                    "device_name": self.device_info.get("device_name", ""),
                    "brand": self.device_info.get("brand", ""),
                    "model": self.device_info.get("model", "")
                },
                "task_data": {
                    "tasks": tasks_data,
                    "goal_completed": self.task_manager.goal_completed,
                    "goal_message": self.task_manager.message,
                    "total_tasks": len(all_tasks),
                    "completed_tasks": len([t for t in all_tasks if t.status == "completed"]),
                    "failed_tasks": len([t for t in all_tasks if t.status == "failed"]),
                    "pending_tasks": len([t for t in all_tasks if t.status == "pending"])
                },
                "triggered_by": {
                    "description": task.description if task else None,
                    "status": task.status if task else None,
                    "agent_type": task.agent_type if task else None
                },
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # Broadcast to all connected web clients
            await websocket_manager.broadcast(task_update_message)
            logger.debug(f"Broadcasted task update for client {self.id}: event={event_type}, tasks={len(tasks_data)}")
            
        except Exception as e:
            logger.error(f"Failed to broadcast task update: {e}", exc_info=True)

