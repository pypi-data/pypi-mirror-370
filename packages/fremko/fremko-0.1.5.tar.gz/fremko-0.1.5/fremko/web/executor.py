"""
Web-based code executor using the DEFAULT persona and a real Tools instance (e.g., WsTools).
"""

import asyncio
import logging
from typing import Any, Dict, Tuple

from fremko.agent.utils.executer import SimpleCodeExecutor
from fremko.agent.context.personas.default import DEFAULT
from fremko.tools.tools import Tools, describe_tools

logger = logging.getLogger("droidrun")


class WebExecutorContext:
    """Minimal context implementation for code execution."""

    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}

    async def get(self, key: str, default=None):
        return self._data.get(key, default)

    async def set(self, key: str, value: Any):
        self._data[key] = value


def create_executor_for_tools(tools: Tools) -> SimpleCodeExecutor:
    """
    Create a SimpleCodeExecutor filtered by DEFAULT persona allowed tools,
    mirroring CodeActAgent's initialization pattern.
    """
    all_tools_list = describe_tools(tools)
    tool_list: Dict[str, Any] = {}

    for tool_name in DEFAULT.allowed_tools:
        if tool_name in all_tools_list:
            tool_list[tool_name] = all_tools_list[tool_name]
    tool_list["get_state"] = tools.get_state

    logger.debug(f"Web executor using DEFAULT persona tools: {list(tool_list.keys())}")

    executor = SimpleCodeExecutor(
        loop=asyncio.get_event_loop(),
        locals={},
        tools=tool_list,
        globals={"__builtins__": __builtins__},
    )
    return executor


async def execute_code_with_persona(code: str, tools: Tools) -> Dict[str, Any]:
    """
    Execute code using the DEFAULT persona and the provided Tools instance.
    """
    try:
        executor = create_executor_for_tools(tools)
        ctx = WebExecutorContext()
        output = await executor.execute(ctx, code)
        return {
            "success": True,
            "output": output,
            "finished": getattr(tools, "finished", False),
            "task_success": getattr(tools, "success", False),
            "task_reason": getattr(tools, "reason", ""),
        }
    except Exception as e:
        logger.error(f"Code execution error: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"{type(e).__name__}: {str(e)}",
            "output": str(e),
        }
