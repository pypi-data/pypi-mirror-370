from enum import Enum


class Role(str, Enum):
    """
    Enumeration of most common message roles.

    Examples:
        >>> from chat_object import Role
        >>> Role.System
        'system'
        >>> Role.User
        'user'
        >>> Role.Assistant
        'assistant'
        >>> Role.Tool
        'tool'
        >>> Role.Function
        'function'

        >>> # String comparison works
        >>> Role.User == "user"
        True
        >>> Role.Assistant == "assistant"
        True

        >>> # Can be used in Message objects
        >>> from chat_object import Message
        >>> msg = Message(Role.System, "You are helpful")
        >>> msg.role
        'system'

        >>> # Sorting works
        >>> sorted([Role.Assistant, Role.User, Role.System])
        ['assistant', 'system', 'user']

        >>> # String operations work directly
        >>> Role.User + " message"
        'user message'
        >>> "Hello " + Role.Assistant
        'Hello assistant'
        >>> Role.System in "system prompt"
        True
    """

    System = "system"
    User = "user"
    Assistant = "assistant"
    Tool = "tool"
    Function = "function"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.value == other
        if isinstance(other, Role):
            return super().__eq__(other)
        return NotImplemented

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return repr(self.value)

    def __hash__(self) -> int:
        return hash(self.value)
