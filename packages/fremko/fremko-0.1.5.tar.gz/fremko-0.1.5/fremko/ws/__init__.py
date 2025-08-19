"""WebSocket sub-package

This package groups together all WebSocket related helpers (server, client,
  tools wrappers) so the flat ``fremko.tools`` namespace does not get too
  crowded.

Re-exports:
    WsServer – high-level helper that waits for phone connections.
    WsClient – container representing exactly one connected phone.
"""
from __future__ import annotations

from .server import WsServer
from .client import WsClient
