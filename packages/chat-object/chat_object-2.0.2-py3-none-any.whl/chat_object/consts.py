from typing import Literal, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .role import Role
    from .message import Message
    from .prompt import Prompt

LiteralRoleType = Literal["system", "user", "assistant", "tool", "function"]
RoleType = Union["Role", str, LiteralRoleType]
DictMessageType = dict[Literal["role", "content"], str]
PureDictMessageType = dict[str, str]
MessageType = Union["Message", DictMessageType, PureDictMessageType]
MessageContent = Union[str, "Prompt"]
