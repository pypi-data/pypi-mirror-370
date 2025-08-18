"""
WsTools - WebSocket-based implementation of the Tools interface.

The PC runs a WebSocket **server** and waits for a single phone/client
connection.  Every UI-level primitive (tap, swipe, input_text, …) is
translated into a JSON frame and sent over the socket.  The phone is
responsible for executing the action (via accessibility service) and
sending back an acknowledgement result frame.

Message format PC → phone (action request):
{
  "type": "action",
  "id": <int>,          # correlates request/response
  "name": "tap_by_index",
  "args": { ... }
}

Message format phone → PC (action result):
{
  "type": "action_result",
  "id": <int>,          # same as request
  "status": "ok" | "error",
  "info": "human readable text",
  "data": {...}
}

Any other messages (e.g. the initial `goal` frame, ping/pong, state updates) are handled separately or simply logged.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List, Tuple
import functools
import time
import base64

from .tools import Tools
from .wsdevice import WsDevice

logger = logging.getLogger("droidrun")
LOG_FUNCTION_CALLS = False

import websockets

class WsTools(Tools):
    """Async Tools implementation over a `websockets` connection.

    Runs entirely on the server's asyncio event loop. Tool methods are async
    and await action results routed by the single recv() loop in WsClient.
    """

    def __init__(self, websocket: "websockets.WebSocketServerProtocol", loop: asyncio.AbstractEventLoop):
        self.ws = websocket
        self.loop = loop

        # Correlation-id bookkeeping
        self._next_id: int = 0
        self._pending: Dict[int, asyncio.Future] = {}

        # State flags expected elsewhere in the framework
        self.finished: bool = False
        self.success: bool | None = None
        self.reason: str | None = None
        self.memory: List[str] = []  # memory helpers not used in WS mode

        # Instance-level cache for clickable elements (index-based tapping)
        self.clickable_elements_cache: List[Dict[str, Any]] = []

        # Thin wrapper providing adbutils-like API (click, swipe, ...)
        self.device = WsDevice(self)

        # In WebSocket server mode, WsClient owns the single recv() loop.
        # Do not start a competing background listener here.
        self._listener_task = None
        # Stream state (optional)
        self._stream_active: bool = False
        self._stream_params: Dict[str, Any] = {}

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------

    # Decorator to add before/after logs around every public tool method
    def _log_call(func):  # type: ignore[no-redef]
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            start_ts = time.perf_counter()
            try:
                if LOG_FUNCTION_CALLS:
                    logger.info(f"[WsTools] -> {func.__name__}(args={args}, kwargs={kwargs})")
                result = func(self, *args, **kwargs)
                if LOG_FUNCTION_CALLS:
                    duration_ms = int((time.perf_counter() - start_ts) * 1000)
                    logger.info(f"[WsTools] <- {func.__name__} (ok) {duration_ms}ms")
                return result
            except Exception as e:  # pragma: no cover
                duration_ms = int((time.perf_counter() - start_ts) * 1000)
                logger.exception(f"[WsTools] <- {func.__name__} (error) {duration_ms}ms: {e}")
                raise

        return wrapper

    async def _listener(self) -> None:
        """Deprecated: WsClient is the sole reader. Left for compatibility if needed."""
        return

    def notify_disconnect(self, reason: str = "Client disconnected") -> None:
        """Fail all pending requests and mark the workflow as finished.

        Call when the underlying WebSocket disconnects so any synchronous callers
        blocked in _send_action_sync() are released immediately.
        """
        def _fail_all_pending() -> None:
            try:
                for msg_id, fut in list(self._pending.items()):
                    if fut and not fut.done():
                        fut.set_result({
                            "type": "action_result",
                            "id": msg_id,
                            "status": "error",
                            "info": reason,
                            "data": None,
                        })
                self._pending.clear()
            finally:
                self.finished = True
                self.success = False
                self.reason = reason

        try:
            if self.loop and self.loop.is_running():
                self.loop.call_soon_threadsafe(_fail_all_pending)
            else:
                _fail_all_pending()
        except Exception:
            logger.debug("[WsTools] notify_disconnect encountered an error", exc_info=True)

    # ---------------------------------------------------------------------
    # Message routing helpers
    # ---------------------------------------------------------------------
    def _route_message(self, data: Dict[str, Any]) -> None:
        """Dispatch an incoming message from the phone to the appropriate handler.

        Extracted from `_listener` to keep the main receive-loop compact and to
        allow future extensions (e.g. handling *voice transcription* results)
        without cluttering the coroutine.
        """
        msg_type = data.get("type")
        if msg_type == "action_result":
            msg_id = data.get("id")
            fut = self._pending.pop(msg_id, None)
            if fut and not fut.done():
                fut.set_result(data)
        elif msg_type == "pong":
            logger.debug("[WsTools] <pong>")
        else:
            logger.debug(f"[WsTools] Unhandled message type: {msg_type}")

    async def _send_action(self, name: str, **args: Any) -> Any:
        """Serialize + send the action and await the result."""
        self._next_id += 1
        msg_id = self._next_id
        frame = {
            "type": "action",
            "id": msg_id,
            "name": name,
            "args": args,
        }

        # Prepare a future to be resolved by the recv() loop via _route_message
        pending_fut: asyncio.Future = self.loop.create_future()
        self._pending[msg_id] = pending_fut

        send_start = time.perf_counter()
        logger.debug(f"[WsTools] -> action name={name} id={msg_id} args={args}")
        await self.ws.send(json.dumps(frame))

        response: Dict[str, Any] = await pending_fut
        elapsed_ms = int((time.perf_counter() - send_start) * 1000)

        status = response.get("status", "ok")
        info = response.get("info", "")
        data = response.get("data")
        logger.debug(
            f"[WsTools] <- action_result name={name} id={msg_id} status={status} info={info!r} {elapsed_ms}ms"
        )
        if status != "ok":
            return f"Error: {info or status}"
        return data if data is not None else info

    # ------------------------------------------------------------------
    # Streaming control (Control WS → device)
    # ------------------------------------------------------------------
    async def start_stream(
        self,
        url: str | None = None,
        fps: int = 12,
        max_width: int = 720,
        quality: int = 75,
        stream_format: str | None = None,
    ) -> Any:
        args: Dict[str, Any] = {
            "fps": int(max(1, min(30, fps))),
            "max_width": int(max(320, max_width)),
            "quality": int(max(30, min(95, quality))),
        }
        if stream_format:
            # Accept 'jpeg' to trigger client-side JPEG streaming
            fmt_upper = str(stream_format).upper()
            if fmt_upper == "JPEG":
                args["format"] = "JPEG"
        if url:
            args["url"] = url
        # If JPEG requested by UI, map to dedicated client verb when supported
        if args.get("format") == "JPEG":
            args_no_fmt = {k: v for k, v in args.items() if k != "format"}
            res = await self._send_action("start_jpeg_stream", **args_no_fmt)
        else:
            res = await self._send_action("start_stream", **args)
        # Device likely returns ok/info; track desired params locally
        self._stream_active = True
        self._stream_params.update(args)
        return res

    async def update_stream(self, fps: int | None = None, quality: int | None = None, max_width: int | None = None, stream_format: str | None = None) -> Any:
        args: Dict[str, Any] = {}
        if fps is not None:
            args["fps"] = int(max(1, min(30, fps)))
        if quality is not None:
            args["quality"] = int(max(30, min(95, quality)))
        if max_width is not None:
            args["max_width"] = int(max(320, max_width))
        # Route update according to last requested format when possible
        last_fmt = str(self._stream_params.get("format") or "H264").upper()
        if (stream_format or last_fmt).upper() == "JPEG":
            res = await self._send_action("update_jpeg_stream", **args)
        else:
            res = await self._send_action("update_stream", **args)
        if isinstance(res, dict):
            self._stream_params.update(res)
        else:
            self._stream_params.update(args)
        return res

    async def stop_stream(self) -> Any:
        res = await self._send_action("stop_stream")
        self._stream_active = False
        return res

    # ---------------------------------------------------------------------
    # Tools API implementations (mostly 1-liners delegating to _send_action_sync)
    # ---------------------------------------------------------------------

    # UI interaction ------------------------------------------------------
    async def tap_by_index(self, index: int):
        """
        Tap on a UI element by its index.

        This function uses the cached clickable elements
        to find the element with the given index and tap on its center coordinates.

        Args:
            index: Index of the element to tap

        Returns:
            Result message
        """
        def _collect_all_indices(elements):
            indices = []
            for item in elements:
                if item.get("index") is not None:
                    indices.append(item.get("index"))
                indices.extend(_collect_all_indices(item.get("children", [])))
            return indices

        def _find_element_by_index(elements, target_index):
            for item in elements:
                if item.get("index") == target_index:
                    return item
                child_result = _find_element_by_index(item.get("children", []), target_index)
                if child_result:
                    return child_result
            return None

        # Ensure we have a cached tree
        if not self.clickable_elements_cache:
            return "Error: No UI elements cached. Call get_state first."

        element = _find_element_by_index(self.clickable_elements_cache, index)
        if not element:
            indices = sorted(_collect_all_indices(self.clickable_elements_cache))
            indices_str = ", ".join(str(i) for i in indices[:20])
            if len(indices) > 20:
                indices_str += f"... and {len(indices) - 20} more"
            return f"Error: No element found with index {index}. Available indices: {indices_str}"

        bounds_str = element.get("bounds")
        if not bounds_str:
            element_text = element.get("text", "No text")
            element_class = element.get("className", "Unknown class")
            return (
                f"Error: Element with index {index} ('{element_text}', {element_class}) has no bounds and cannot be tapped"
            )

        try:
            left, top, right, bottom = map(int, bounds_str.split(","))
        except ValueError:
            return f"Error: Invalid bounds format for element with index {index}: {bounds_str}"

        x = (left + right) // 2
        y = (top + bottom) // 2

        # Reuse annotated click helper to capture screenshot & log
        return await self.tap_by_coordinates(x, y)

    async def tap_by_description(self, description: str):
        """Tap an element described in natural language.

        This helper mirrors :py:meth:`AdbTools.tap_by_description` but operates
        through the existing WebSocket connection.  The workflow is:

        1. Capture a screenshot from the phone.
        2. Send the image + description to the remote vision service to get
           *normalized* (0-1) coordinates of the target point.
        3. Convert the normalized coordinates to absolute pixels.
        4. Annotate and persist the screenshot for debugging purposes.
        5. Forward the tap to the phone via :py:meth:`tap_by_coordinates`.
        """
        try:
            # ------------------------------------------------------------------
            # 1) Screenshot
            # ------------------------------------------------------------------
            img_format, img_bytes = await self.take_screenshot()

            # ------------------------------------------------------------------
            # 2) Vision service → normalized coords
            # ------------------------------------------------------------------
            import io
            import os
            import json as _json
            from datetime import datetime

            import requests
            from PIL import Image, ImageDraw  # pillow dependency

            url = "http://175.33.151.40:10001/point"
            files = {"file": ("screenshot.png", io.BytesIO(img_bytes), "image/png")}
            data = {"description": description}
            resp = requests.post(url, files=files, data=data, timeout=10)
            resp.raise_for_status()
            result = resp.json()
            x_norm, y_norm = result.get("x"), result.get("y")
            if x_norm is None or y_norm is None:
                return f"Error: Invalid response from point API: {result}"

            # ------------------------------------------------------------------
            # 3) Absolute pixel coords
            # ------------------------------------------------------------------
            img = Image.open(io.BytesIO(img_bytes))
            w, h = img.size
            x, y = int(x_norm * w), int(y_norm * h)
            logger.debug(f"[WsTools] Normalized ({x_norm:.4f}, {y_norm:.4f}) → pixel ({x}, {y})")

            # ------------------------------------------------------------------
            # 4) Annotate screenshot
            # ------------------------------------------------------------------
            draw = ImageDraw.Draw(img)
            r = 8  # radius of the red dot
            draw.ellipse((x - r, y - r, x + r, y + r), fill="red")

            # Prepare debug directory
            desktop = os.path.expanduser("~/Desktop")
            debug_dir = os.path.join(desktop, "DebugImage")
            os.makedirs(debug_dir, exist_ok=True)

            # Unique filename
            ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            fname = f"tap_{ts}.png"
            save_path = os.path.join(debug_dir, fname)
            img.save(save_path)

            # Update JSON log
            log_path = os.path.join(debug_dir, "log.json")
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as f:
                    try:
                        log = _json.load(f)
                    except _json.JSONDecodeError:
                        log = []
            else:
                log = []

            log.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "file": fname,
                    "description": description,
                    "x_norm": x_norm,
                    "y_norm": y_norm,
                    "x": x,
                    "y": y,
                }
            )
            with open(log_path, "w", encoding="utf-8") as f:
                _json.dump(log, f, indent=2)

            # ------------------------------------------------------------------
            # 5) Perform the tap on the device
            # ------------------------------------------------------------------
            await self.tap_by_coordinates(x, y)

            return (
                f"Tapped '{description}' at ({x}, {y}); annotation saved as {save_path}"
            )
        except Exception as e:  # pragma: no cover
            logger.debug(f"[WsTools] Error tapping by description: {e}", exc_info=True)
            return f"Error tapping by description: {e}"

    async def tap_by_coordinates(self, x: int, y: int):
        """
        Tap on the device screen at specific coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Bool indicating success or failure
        """
        try:
            # Delegate the actual tap to the phone
            return await self.device.click(x, y)
        except Exception as e:  # pragma: no cover
            logger.debug(f"[WsTools] Error tapping by coordinates: {e}", exc_info=True)
            return f"Error tapping by coordinates: {e}"


    async def swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration_ms: int = 300,
    ):
        """
        Performs a straight-line swipe gesture on the device screen.
        To perform a hold (long press), set the start and end coordinates to the same values and increase the duration as needed.
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration: Duration of swipe in seconds
        Returns:
            Bool indicating success or failure
        """
        return await self.device.swipe(
            start_x,
            start_y,
            end_x,
            end_y,
            duration_ms,
        )

    async def gesture_path(self, points: List[Dict[str, Any]], duration_ms: int | None = None):
        """
        Perform an arbitrary gesture following the provided path points.

        Args:
            points: List of dicts with keys "x", "y" and optional "t" (ms timestamp or relative).
                    Example: [{"x":120, "y":400, "t":0}, {"x":130, "y":420, "t":15}, ...]
            duration_ms: Optional total duration override. If omitted, computed from
                         the first and last timestamps in points. If timestamps are
                         missing or invalid, defaults to 300ms.

        Returns:
            Result from the device (string or data dict)
        """
        # Basic validation
        if not isinstance(points, list) or len(points) < 2:
            return "Error: 'points' must be a list with at least 2 items"

        # Detect if points appear normalized (all x,y in [0,1])
        try:
            all_norm = all(
                isinstance(p, dict)
                and (isinstance(p.get("x"), (int, float)))
                and (isinstance(p.get("y"), (int, float)))
                and 0 <= float(p["x"]) <= 1
                and 0 <= float(p["y"]) <= 1
                for p in points
            )
        except Exception:
            all_norm = False

        # If normalized, best-effort convert to absolute using device resolution
        width: int | None = None
        height: int | None = None
        if all_norm:
            try:
                info = await self.get_device_info()
                width = int(info.get("width")) if info and info.get("width") else None
                height = int(info.get("height")) if info and info.get("height") else None
            except Exception:
                width = height = None

        sanitized: List[Dict[str, int]] = []
        for p in points:
            try:
                x_val = float(p.get("x"))
                y_val = float(p.get("y"))
            except Exception:
                return "Error: Each point must include numeric 'x' and 'y'"

            if width and height and all_norm:
                x_px = int(round(max(0.0, min(1.0, x_val)) * max(1, width)))
                y_px = int(round(max(0.0, min(1.0, y_val)) * max(1, height)))
                if width:
                    x_px = max(0, min(x_px, max(0, width - 1)))
                if height:
                    y_px = max(0, min(y_px, max(0, height - 1)))
            else:
                # Treat as absolute pixels
                try:
                    x_px = int(round(x_val))
                    y_px = int(round(y_val))
                except Exception:
                    return "Error: Failed to convert point coordinates to integers"

            t_val = p.get("t")
            if t_val is None:
                sanitized.append({"x": x_px, "y": y_px})
            else:
                try:
                    sanitized.append({"x": x_px, "y": y_px, "t": int(round(float(t_val)))})
                except Exception:
                    sanitized.append({"x": x_px, "y": y_px})

        # Compute duration if needed from timestamps
        if duration_ms is None:
            times = [pt.get("t") for pt in sanitized if isinstance(pt.get("t"), int)]
            if len(times) >= 2:
                dt = max(times) - min(times)
                # Clamp to practical bounds
                duration_ms = int(max(50, min(10_000, dt)))
            else:
                duration_ms = 300

        return await self._send_action("gesture_path", points=sanitized, duration_ms=duration_ms)

    async def input_text(self, index: int, text: str):
        """
        Input text on the device at the given index.

        In the background, this function will:
        1. Tap on the element at the given index.
        2. Input the given text into the element.

        Args:
            index: Index of the element to input text into.
            text: Text to input. Can contain spaces, newlines, and special characters including non-ASCII.

        Returns:
            Result message
        """
        # 1. Tap on the element at the given index.
        await self.tap_by_index(index)
        await asyncio.sleep(0.15)
        # 2. Input the given text into the element.
        return await self.input_text_action(text)
    
    async def input_text_action(self, text: str):
        """
        This function is the input text part of the input_text function.
        It is used to input text into the element at the given index.
        """
        return await self._send_action("input_text", text=text)

    async def back(self):
        """
        Go back on the current view.
        This presses the Android back button.
        """
        return await self._send_action("back")

    async def press_key(self, keycode: int):
        """
        Press a key on the Android device.

        Common keycodes:
        - 3: HOME
        - 4: BACK
        - 66: ENTER
        - 67: DELETE

        Args:
            keycode: Android keycode to press
        """
        supported_keycodes = {3, 4, 66, 67}
        if keycode not in supported_keycodes:
            raise ValueError(f"Keycode {keycode} not supported. Only keycodes {sorted(supported_keycodes)} are supported.")
        return await self._send_action("press_key", keycode=keycode)

    # App / system --------------------------------------------------------
    async def start_app(self, package: str, activity: str | None = None):
        """
        Start an app on the device.

        Args:
            package: Package name (e.g., "com.android.settings")
            activity: Optional activity name
        """
        return await self._send_action("start_app", package=package, activity=activity)

    async def take_screenshot(self) -> Tuple[str, bytes]:
        import base64 as _b64
        await asyncio.sleep(0.3)
        max_attempts = 3
        last_error = None
        for attempt in range(max_attempts):
            data = await self._send_action("take_screenshot")
            # Expecting phone to return {"format":"PNG","base64":"..."}
            if isinstance(data, dict):
                try:
                    img_base64 = data.get("base64", "")
                    img_format = data.get("format", "PNG")
                    img_bytes = _b64.b64decode(img_base64) if img_base64 else b""
                    return img_format, img_bytes
                except Exception as e:
                    last_error = e
                    logger.debug(f"[WsTools] Error decoding screenshot (attempt {attempt+1}): {e}", exc_info=True)
            else:
                last_error = RuntimeError(f"Unexpected screenshot data type: {type(data)} – {data}")
                logger.debug(f"[WsTools] Screenshot returned non-dict (attempt {attempt+1}): {data!r}")

            # If we get here, either data was not a dict or decoding failed; try again if attempts remain

        # If all attempts failed, raise the last error
        raise RuntimeError(f"Failed to take screenshot after {max_attempts} attempts: {last_error}")

    async def list_packages(self, include_system_apps: bool = False):
        """
        List installed packages on the device.

        Args:
            include_system_apps: Whether to include system apps (default: False)

        Returns:
            List of package names
        """
        data = await self._send_action("list_packages", include_system_apps=include_system_apps)
        return data if isinstance(data, list) else []

    async def list_apps(self):
        """
        List installed apps on the device with their icons.

        Returns an array of apps with base64 PNG icon data that can be directly 
        displayed in web browsers or decoded for other uses.

        Returns:
            List of dictionaries containing:
            - appName: Display name of the app
            - packageName: Package identifier 
            - icon: Base64-encoded PNG icon data (may be empty string if icon unavailable)
        
        Example usage:
            apps = await tools.list_apps()
            for app in apps:
                print(f"App: {app['appName']} ({app['packageName']})")
                if app['icon']:
                    # icon can be used directly in HTML: <img src="data:image/png;base64,{icon}">
                    pass
        """
        data = await self._send_action("list_apps")
        # Android device returns a list of app objects directly
        return data if isinstance(data, list) else []

    # State helpers -------------------------------------------------------
    async def get_device_info(self) -> Dict[str, Any]:
        """Request device metadata from the phone.

        Expected result example:
        {"device_name":"Pixel 7","serial":"...","brand":"Google","model":"Pixel 7","sdk":34,"width":1080,"height":2400,"battery":92}
        """
        data = await self._send_action("get_device_info")
        if isinstance(data, dict):
            return data
        return {}

    # State helpers -------------------------------------------------------
    async def get_state(self):
        """
        Get both the a11y tree and phone state in a single call using the combined /state endpoint.

        Args:
            serial: Optional device serial number

        Returns:
            Dictionary containing both 'a11y_tree' and 'phone_state' data
        """
        try:
            data = await self._send_action("get_state")
            if not isinstance(data, dict):
                return {
                    "error": "Format Error",
                    "message": f"Unexpected state data type: {type(data)}",
                }

            if "a11y_tree" not in data:
                return {
                    "error": "Missing Data",
                    "message": "a11y_tree not found in combined state data",
                }

            if "phone_state" not in data:
                return {
                    "error": "Missing Data",
                    "message": "phone_state not found in combined state data",
                }

            elements = data.get("a11y_tree")
            if not isinstance(elements, list):
                # Ensure cache is cleared if we get an unexpected payload
                self.clickable_elements_cache = []
                return {
                    "error": "Format Error",
                    "message": f"Unexpected a11y_tree format: {type(elements)}",
                }

            def _filter_element(elem: Dict[str, Any]) -> Dict[str, Any]:
                filtered = {k: v for k, v in elem.items() if k != "type"}
                if "children" in filtered and isinstance(filtered["children"], list):
                    filtered["children"] = [_filter_element(c) for c in filtered["children"]]
                return filtered

            filtered_elements = [_filter_element(e) for e in elements]
            self.clickable_elements_cache = filtered_elements

            return {
                "a11y_tree": filtered_elements,
                "phone_state": data.get("phone_state"),
            }
        except Exception as e:  # pragma: no cover
            return {
                "error": str(e),
                "message": f"Error getting combined state: {str(e)}",
            }

    # Memory helpers ------------------------------------------------------
    async def remember(self, information: str):
        """
        Store important information to remember for future context.

        This information will be extracted and included into your next steps to maintain context
        across interactions. Use this for critical facts, observations, or user preferences
        that should influence future decisions.

        Args:
            information: The information to remember

        Returns:
            Confirmation message
        """
        # No-op in WebSocket mode
        return "Remember/Memory not supported in WsTools"

    async def get_memory(self):
        """
        Retrieve all stored memory items.

        Returns:
            List of stored memory items
        """
        return []

    # Complete ------------------------------------------------------------
    async def complete(self, success: bool, reason: str = ""):
        """
        Mark the task as finished.

        Args:
            success: Indicates if the task was successful.
            reason: Reason for failure/success
        """
        self.finished = True
        self.success = success
        self.reason = reason
        return True

    # ---------------------------------------------------------------------
    # Lifecycle helpers
    # ---------------------------------------------------------------------
    async def close(self):
        """Close the websocket and cancel background listener (async)."""
        try:
            await self.ws.close()
        finally:
            try:
                if self._listener_task and not self._listener_task.done():
                    self._listener_task.cancel()
            except Exception:
                pass
