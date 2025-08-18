from .prompt import Prompt
from .consts import RoleType, MessageContent


class Message:
    """
    A message object containing a role and content.

    Attributes:
        role (RoleType): The role of the message (user, assistant, system, etc.).
        content (str): The content/body of the message.

    Examples:
        >>> from chat_object import Message, Role
        >>> msg = Message(Role.User, "Hello, world!")
        >>> msg.role
        'user'
        >>> msg.content
        'Hello, world!'

        >>> msg2 = Message("assistant", "Hi there!")
        >>> msg2.role
        'assistant'
        >>> msg2.content
        'Hi there!'

        >>> # Dict-like access for backward compatibility
        >>> msg["role"]
        'user'
        >>> msg["content"]
        'Hello, world!'
        >>> msg.get("role")
        'user'
        >>> msg.get("nonexistent", "default")
        'default'
        >>> list(msg.keys())
        ['role', 'content']
        >>> list(msg.values())
        ['user', 'Hello, world!']
        >>> list(msg.items())
        [('role', 'user'), ('content', 'Hello, world!')]
    """

    def __init__(self, role: RoleType, content: MessageContent):
        """
        Initialize a message with role and content.

        Args:
            role (RoleType): The role of the message.
            content (str): The content of the message.

        Examples:
            >>> from chat_object import Message, Role
            >>> msg = Message(Role.System, "You are a helpful assistant.")
            >>> msg.role == Role.System
            True
            >>> msg.content == "You are a helpful assistant."
            True

            >>> msg2 = Message("user", "What's the weather like?")
            >>> msg2.role == "user"
            True
        """
        self.role = role
        if isinstance(content, Prompt):
            self.content = str(content)
        else:
            self.content = content

    def as_dict(self) -> dict[str, str]:
        """
        Returns a dictionary representation of the message.

        Returns:
            dict[str, str]: Dictionary with 'role' and 'content' keys.

        Examples:
            >>> from chat_object import Message, Role
            >>> msg = Message(Role.User, "Hello")
            >>> msg.as_dict()
            {'role': 'user', 'content': 'Hello'}
        """
        return {"role": self.role, "content": self.content}

    def __getitem__(self, key: str) -> str:
        """
        >>> from chat_object import Message, Role
        >>> msg = Message(Role.User, "Hello")
        >>> msg["role"]
        'user'
        >>> msg["content"]
        'Hello'
        """
        if key == "role":
            return self.role
        elif key == "content":
            return self.content
        else:
            raise KeyError(f"Message has no key '{key}'")

    def __setitem__(self, key: str, value: str) -> None:
        """
        >>> from chat_object import Message, Role
        >>> msg = Message(Role.User, "Hello")
        >>> msg["content"] = "Goodbye"
        >>> msg.content
        'Goodbye'
        >>> msg["role"] = Role.Assistant
        >>> msg.role
        'assistant'
        """
        if key == "role":
            self.role = value  # type: ignore
        elif key == "content":
            self.content = value
        else:
            raise KeyError(f"Message has no key '{key}'")

    def get(self, key: str, default: str | None = None) -> str | None:
        """
        Dict-like get method with default value.

        Examples:
            >>> from chat_object import Message, Role
            >>> msg = Message(Role.User, "Hello")
            >>> msg.get("role")
            'user'
            >>> msg.get("nonexistent", "default")
            'default'
        """
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self) -> tuple[str, str]:
        """
        Dict-like keys method.

        Examples:
            >>> from chat_object import Message, Role
            >>> msg = Message(Role.User, "Hello")
            >>> list(msg.keys())
            ['role', 'content']
        """
        return ("role", "content")

    def values(self) -> tuple[str, str]:
        """
        Dict-like values method.

        Examples:
            >>> from chat_object import Message, Role
            >>> msg = Message(Role.User, "Hello")
            >>> list(msg.values())
            ['user', 'Hello']
        """
        return (self.role, self.content)

    def items(self) -> list[tuple[str, str]]:
        """
        Dict-like items method.

        Examples:
            >>> from chat_object import Message, Role
            >>> msg = Message(Role.User, "Hello")
            >>> list(msg.items())
            [('role', 'user'), ('content', 'Hello')]
        """
        return [("role", self.role), ("content", self.content)]

    def update(self, other: dict[str, str]) -> None:
        """
        Dict-like update method.

        Examples:
            >>> from chat_object import Message, Role
            >>> msg = Message(Role.User, "Hello")
            >>> msg.update({"content": "Goodbye"})
            >>> msg.content
            'Goodbye'
        """
        for key, value in other.items():
            self[key] = value

    def copy(self) -> "Message":
        """
        Dict-like copy method.

        Examples:
            >>> from chat_object import Message, Role
            >>> msg = Message(Role.User, "Hello")
            >>> msg_copy = msg.copy()
            >>> msg_copy is not msg
            True
            >>> msg_copy.role == msg.role
            True
            >>> msg_copy.content == msg.content
            True
        """
        return Message(self.role, self.content)  # type: ignore

    def __str__(self) -> str:
        """
        >>> from chat_object import Message, Role
        >>> msg = Message(Role.User, "Hello!")
        >>> str(msg)
        'user: Hello!'
        """
        return f"{self.role}: {self.content}"

    def __contains__(self, item: str) -> bool:
        """
        >>> from chat_object import Message, Role
        >>> msg = Message(Role.User, "Hello World!")
        >>> "Hello" in msg
        True
        >>> "Goodbye" in msg
        False
        """
        return item in self.content

    def __repr__(self) -> str:
        """
        >>> from chat_object import Message, Role
        >>> msg = Message(Role.System, "You are helpful.")
        >>> repr(msg)
        "Message(role='system', content='You are helpful.')"
        """
        return f"Message(role={repr(self.role)}, content={repr(self.content)})"

    def __eq__(self, other: object) -> bool:
        """
        >>> from chat_object import Message, Role
        >>> msg1 = Message(Role.User, "Hello")
        >>> msg2 = Message(Role.User, "Hello")
        >>> msg3 = Message(Role.Assistant, "Hello")

        >>> msg1 == msg2
        True
        >>> msg1 == msg3
        False
        """
        if not isinstance(other, Message):
            return NotImplemented
        return self.role == other.role and self.content == other.content

    def __hash__(self) -> int:
        """
        >>> from chat_object import Message, Role
        >>> msg1 = Message(Role.User, "Hello")
        >>> msg2 = Message(Role.User, "Hello")
        >>> hash(msg1) == hash(msg2)
        True
        """
        return hash((self.role, self.content))

    def __len__(self) -> int:
        """
        >>> from chat_object import Message, Role
        >>> msg = Message(Role.User, "Hello, world!")
        >>> len(msg)
        13

        >>> msg2 = Message(Role.Assistant, "")
        >>> len(msg2)
        0
        """
        return len(self.content)
