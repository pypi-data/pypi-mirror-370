"""
WebSocket Server for Fremko

Runs entirely on a single asyncio event loop. No threads are used.
"""
from __future__ import annotations

import asyncio
import logging
import json
import struct
from io import BytesIO
import av  # PyAV for H.264 decode
from PIL import Image  # Pillow for JPEG encoding
from typing import Optional, Any, Dict, Deque
from collections import deque
from dataclasses import dataclass, field

import websockets
from websockets.server import WebSocketServerProtocol

from fremko.ws.client import WsClient

# Server instance (global helper)
server_instance: "WsServer" | None = None
logger = logging.getLogger("droidrun")


class WsServer:
    """A multi-client, multi-goal WebSocket server.

    Runs on the current asyncio loop. Use ``await WsServer.start()`` to serve
    forever on that loop.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 10001, **kwargs: Any):
        """
        Initialise the server.

        Args:
            host (str): Host to bind the server to.
            port (int): Port to listen on.
            **kwargs: Additional agent configuration arguments.
        """
        self.host = host
        self.port = port
        self.agent_config = kwargs
        self.clients: Dict[str, WsClient] = {}
        # Map device serial -> control client
        self.serial_to_client: Dict[str, WsClient] = {}
        # Map device serial -> active video session state
        self.serial_to_stream: Dict[str, "VideoStreamSession"] = {}
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self.is_running = asyncio.Event()

    async def start(self):
        """Start the WebSocket server on the current event loop and run forever."""
        if self.is_running.is_set():
            logger.warning("Server is already running.")
            return
        self._loop = asyncio.get_running_loop()
        self.is_running.set()
        await self._start_server()

    async def _start_server(self):
        """Starts the WebSocket server on the current event loop."""
        try:
            async with websockets.serve(
                self._handler, self.host, self.port, max_size=20 * 1024 * 1024, max_queue=32
            ):
                logger.info(f"🚀 WebSocket server listening at ws://{self.host}:{self.port}")
                await asyncio.Future()  # Run forever
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}", exc_info=True)
        finally:
            self.is_running.clear()

    def stop(self):
        """Deprecated: server runs on the current loop; cancel the task running start()."""
        logger.warning("stop() is deprecated in single-loop mode. Cancel the task awaiting start().")

    async def _handler(self, websocket: WebSocketServerProtocol, path: str = None):
        """
        Handle a new WebSocket connection.

        Args:
            websocket (WebSocketServerProtocol): The WebSocket connection object.
            path (str): The request path.
        """
        # Route based on path. Control WS is default ("/" or None). Video stream is "/stream".
        if websocket.request.path == "/stream":
            await self._video_handler(websocket)
            return

        client = WsClient(websocket, self)
        self.clients[client.id] = client
        logger.info(f"Client connected: {client.id} (Total: {len(self.clients)})")
        try:
            await client.handle_connection()
        except Exception as e:
            logger.error(f"Error handling client {client.id}: {e}", exc_info=True)
        finally:
            try:
                client.tools.notify_disconnect("Client handler closed")
            except Exception:
                logger.debug("Failed to notify tools during handler cleanup", exc_info=True)
            # Best-effort cleanup of serial mapping
            try:
                # Remove any serials pointing to this client
                to_delete = [s for s, c in self.serial_to_client.items() if c is client]
                for s in to_delete:
                    del self.serial_to_client[s]
            except Exception:
                logger.debug("Failed to cleanup serial mapping for client", exc_info=True)
            del self.clients[client.id]
            logger.info(f"Client disconnected: {client.id} (Total: {len(self.clients)})")

    # ------------------------------
    # Serial registration and lookup
    # ------------------------------
    def register_serial(self, serial: str, client: WsClient) -> None:
        if not serial:
            return
        prev = self.serial_to_client.get(serial)
        self.serial_to_client[serial] = client
        if prev is not None and prev is not client:
            logger.info(f"Serial '{serial}' re-registered to new client {client.id}")

    # ------------------------------
    # Video stream handling (/stream)
    # ------------------------------
    async def _video_handler(self, websocket: WebSocketServerProtocol) -> None:
        """
        Handle the video WebSocket: perform handshake and receive H.264 frames.

        Expected handshake:
          1) {"type":"identify","serial":"..."}
          2) reply: any OK variant (we send {"status":"ok"})
          3) {"type":"stream_start","format":"H264","fps":<int>,"bitrate_kbps":<int>,"serial":"..."}
          4) binary frames
        """
        serial: Optional[str] = None
        try:
            # 1) identify
            first = await websocket.recv()
            if isinstance(first, (bytes, bytearray)):
                # Some devices might send text first; binary is invalid here
                await websocket.close(code=4000, reason="Expected identify JSON")
                return
            try:
                first_js = json.loads(first)
            except Exception:
                await websocket.close(code=4001, reason="Malformed identify JSON")
                return
            if not isinstance(first_js, dict) or first_js.get("type") != "identify":
                await websocket.close(code=4002, reason="First message must be 'identify'")
                return
            serial = str(first_js.get("serial") or "").strip()
            if not serial:
                await websocket.close(code=4003, reason="Missing serial in identify")
                return

            client = self.serial_to_client.get(serial)
            # Enforce: only accept if serial is known AND we requested start_stream
            if client is None:
                await websocket.close(code=4404, reason="unknown_serial")
                return
            # Verify the client's device_info serial matches
            try:
                client_serial = str((client.device_info or {}).get("serial") or "").strip()
            except Exception:
                client_serial = ""
            if client_serial != serial:
                await websocket.close(code=4405, reason="serial_mismatch")
                return
            # Verify we requested the stream on control channel
            stream_active = bool(getattr(client.tools, "_stream_active", False))
            if not stream_active:
                await websocket.close(code=4406, reason="no_active_stream_request")
                return

            # 2) ack (only after validation)
            try:
                await websocket.send(json.dumps({"status": "ok"}))
            except Exception:
                await websocket.send("ok")

            # 3) stream_start
            second = await websocket.recv()
            if isinstance(second, (bytes, bytearray)):
                await websocket.close(code=4004, reason="Expected stream_start JSON")
                return
            try:
                second_js = json.loads(second)
            except Exception:
                await websocket.close(code=4005, reason="Malformed stream_start JSON")
                return
            if second_js.get("type") != "stream_start":
                await websocket.close(code=4006, reason="Second message must be 'stream_start'")
                return
            stream_format = (second_js.get("format") or "").upper()
            if stream_format not in ("H264", "JPEG"):
                logger.warning(f"/stream format {second_js.get('format')} not in (H264,JPEG); defaulting to H264")
                stream_format = "H264"

            fps = int(second_js.get("fps") or 0)
            bitrate_kbps = int(second_js.get("bitrate_kbps") or 0)

            session = VideoStreamSession(
                websocket=websocket,
                serial=serial,
                fps=fps,
                bitrate_kbps=bitrate_kbps,
            )
            self.serial_to_stream[serial] = session
            logger.info(f"🎥 Stream started for serial={serial} fps={fps} bitrate_kbps={bitrate_kbps}")

            # Initialize decoder per session (H264 only)
            if stream_format == "H264":
                try:
                    session.init_decoder()
                except Exception as e:
                    logger.error(f"Failed to init decoder for {serial}: {e}")

            # 4) frames loop
            count = 0
            while True:
                msg = await websocket.recv()
                count += 1
                if isinstance(msg, (bytes, bytearray)):
                    if stream_format == "JPEG":
                        # JPEG path: frames are length-prefixed within the message
                        buf = memoryview(msg)
                        offset = 0
                        total = len(buf)
                        while offset + 4 <= total:
                            try:
                                n = struct.unpack_from(">I", buf, offset)[0]
                            except Exception:
                                break
                            offset += 4
                            if n <= 0 or offset + n > total:
                                break
                            jpeg_payload = bytes(buf[offset:offset+n])
                            offset += n
                            try:
                                session.push_frame(jpeg_payload)
                            except Exception:
                                logger.debug("failed to push JPEG frame", exc_info=True)
                    else:
                        buf = memoryview(msg)
                        offset = 0
                        total = len(buf)
                        while offset + 4 <= total:
                            try:
                                n = struct.unpack_from(">I", buf, offset)[0]
                            except Exception:
                                break
                            offset += 4
                            if n <= 0 or offset + n > total:
                                # malformed or incomplete frame; stop parsing this message
                                break
                            payload = bytes(buf[offset:offset+n])  # Annex-B payload
                            offset += n
                            # Decode Annex-B payload → JPEG and buffer for preview
                            try:
                                for frame in session.decode_payload(payload):
                                    # Convert decoded frame to JPEG bytes
                                    img: Image.Image = frame.to_image()
                                    _b = BytesIO()
                                    img.save(_b, format="JPEG", quality=80)
                                    session.push_frame(_b.getvalue())
                            except Exception:
                                logger.debug("decode failed", exc_info=True)
                else:
                    # Allow mid-stream control messages (e.g., pings, metadata)
                    try:
                        js = json.loads(msg)
                        if js.get("type") == "ping":
                            await websocket.send(json.dumps({"type": "pong"}))
                        elif js.get("type") == "stream_update":
                            # Allow device to notify new params
                            if "fps" in js:
                                session.fps = int(js["fps"])
                            if "bitrate_kbps" in js:
                                session.bitrate_kbps = int(js["bitrate_kbps"])
                    except Exception:
                        logger.debug("Ignored non-binary non-JSON message on /stream", exc_info=True)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"/stream connection closed for serial={serial or '?'}")
        except Exception as e:
            logger.error(f"Error in /stream handler: {e}", exc_info=True)
        finally:
            if serial and serial in self.serial_to_stream:
                del self.serial_to_stream[serial]
                logger.info(f"🎥 Stream stopped for serial={serial}")

@dataclass
class VideoStreamSession:
    websocket: WebSocketServerProtocol
    serial: str
    fps: int
    bitrate_kbps: int
    # Keep a small buffer of recent frames for preview consumers (JPEG bytes)
    frames: Deque[bytes] = None  # type: ignore[assignment]
    # Sequence counter and condition to signal new frames to preview subscribers
    frame_seq: int = 0
    condition: asyncio.Condition = field(default_factory=asyncio.Condition)
    # Decoder
    _decoder: Any | None = None

    def __post_init__(self):
        if self.frames is None:
            self.frames = deque(maxlen=60)  # keep ~2-4 seconds worth depending on fps

    def push_frame(self, frame: bytes) -> None:
        self.frames.append(frame)
        self.frame_seq += 1
        # Notify waiters (must hold the condition)
        async def _notify():
            try:
                async with self.condition:
                    self.condition.notify_all()
            except Exception:
                pass
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(_notify())
        except RuntimeError:
            # No running loop (should not happen); ignore
            pass

    async def start_in_current_loop(self):
        """Alias for start() kept for backwards compatibility."""
        await self.start()

    # ---- Decode helpers ----
    def init_decoder(self) -> None:
        if self._decoder is None:
            self._decoder = av.CodecContext.create('h264', 'r')

    def decode_payload(self, payload: bytes):
        logger.info(f"Decoding payload of length {len(payload)}")
        if not self._decoder:
            self.init_decoder()
        pkt = av.packet.Packet(payload)
        return self._decoder.decode(pkt)


async def start_server(**kwargs: Any):
    """
    Start the global WebSocket server instance on the current asyncio loop.

    This coroutine never returns under normal operation. Cancel the task or
    interrupt the process to stop serving.
    """
    global server_instance
    if server_instance is None:
        server_instance = WsServer(**kwargs)
    await server_instance.start()


def stop_server():
    """Deprecated: cancel the task awaiting start_server() instead."""
    global server_instance
    server_instance = None
