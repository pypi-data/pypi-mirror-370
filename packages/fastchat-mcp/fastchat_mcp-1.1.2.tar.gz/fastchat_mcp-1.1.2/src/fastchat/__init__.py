"""Chat system integrating the MCP Client with Language Model functionality"""

from .app.chat.chat import Fastchat
from .local.local_chat import TerminalChat

__all__ = ["Fastchat", "TerminalChat"]
