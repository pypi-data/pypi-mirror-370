"""
Fremko - A framework for controlling Android devices through LLM agents.
"""

__version__ = "0.1.0"

# Import main classes for easier access
from fremko.agent.utils.llm_picker import load_llm
from fremko.tools import Tools
from fremko.agent.droid import DroidAgent


# Make main components available at package level
__all__ = [
    "DroidAgent",
    "load_llm",
    "Tools",
]
