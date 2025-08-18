from .message import Message
from .chat_obj import Chat
from .prompt import Prompt
from .role import Role

from .consts import (
    MessageType,
    DictMessageType,
    LiteralRoleType,
    RoleType,
    MessageContent,
)
from .qol import (
    msgs,
    chat,
    msg,
    prmt,
    msg_user,
    msg_assistant,
    msg_system,
)


__all__ = [
    # core classes
    "Message",
    "Chat",
    "Prompt",
    "Role",
    # consts
    "MessageType",
    "DictMessageType",
    "LiteralRoleType",
    "RoleType",
    "MessageContent",
    # qol features
    "msgs",
    "chat",
    "msg",
    "prmt",
    "msg_user",
    "msg_assistant",
    "msg_system",
]

__author__ = "fresh-milkshake"
__license__ = "MIT"
__url__ = "https://github.com/fresh-milkshake/chat-object"
__description__ = "A simple library for creating and managing chat objects and messages for LLM applications."
