from .consts import MessageType
from .message import Message
from typing import Iterator, Callable, Any, Iterable


class Chat:
    """
    A chat object containing a list of messages.

    Attributes:
        messages (tuple[Message, ...]): The list of messages in the chat.

    Examples:
        >>> from chat_object import Chat, Message, Role
        >>> chat = Chat()
        >>> len(chat)
        0

        >>> msg1 = Message(Role.User, "Hello")
        >>> msg2 = Message(Role.Assistant, "Hi there!")
        >>> chat = Chat(msg1, msg2)
        >>> len(chat)
        2
        >>> chat[0].content
        'Hello'
        >>> chat[1].content
        'Hi there!'

        >>> # List-like operations for backward compatibility
        >>> chat.append({"role": "user", "content": "How are you?"})
        >>> len(chat)
        3
        >>> chat[2]["content"]
        'How are you?'

        >>> # Dict-like access to messages
        >>> for msg in chat:
        ...     print(f"{msg['role']}: {msg['content']}")
        user: Hello
        assistant: Hi there!
        user: How are you?

        >>> # List operations
        >>> chat.pop()
        Message(role='user', content='How are you?')
        >>> len(chat)
        2
    """

    _messages: list[Message]

    def __init__(self, *messages: MessageType):
        """
        Creates a chat object.

        Args:
            *messages (MessageType): The list of messages in the chat.

        Examples:
            >>> from chat_object import Chat, Message, Role
            >>> chat = Chat()
            >>> len(chat)
            0

            >>> msg1 = Message(Role.User, "Hello")
            >>> msg2 = Message(Role.Assistant, "Hi!")
            >>> chat = Chat(msg1, msg2)
            >>> len(chat)
            2

            >>> # Test with dictionary messages
            >>> chat2 = Chat({"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi!"})
            >>> len(chat2)
            2
            >>> chat2[0].role
            'user'
        """
        self._messages = []
        self.extend(messages)

    @property
    def messages(self) -> tuple[Message, ...]:
        """
        Returns the list of messages in the chat.

        Returns:
            list[Message]: List of messages.

        Examples:
            >>> from chat_object import Chat, Message, Role
            >>> msg = Message(Role.User, "Hello")
            >>> chat = Chat(msg)
            >>> chat.messages
            (Message(role='user', content='Hello'),)
            >>> len(chat.messages)
            1
        """
        return tuple(self._messages)

    def _validate_message(self, message: MessageType) -> Message:
        """
        >>> from chat_object import Chat, Message, Role
        >>> chat = Chat()
        >>> msg = chat._validate_message(Message(Role.User, "Hello"))
        >>> isinstance(msg, Message)
        True
        >>> msg.role
        'user'

        >>> msg2 = chat._validate_message({"role": "assistant", "content": "Hi!"})
        >>> isinstance(msg2, Message)
        True
        >>> msg2.role
        'assistant'
        """
        if isinstance(message, Message):
            return message
        elif isinstance(message, dict) and "role" in message and "content" in message:
            return Message(message["role"], message["content"])  # type: ignore
        else:
            raise TypeError(f"Invalid message: {message}")

    def add(self, message: MessageType) -> None:
        """
        Adds a single message to the chat.

        Args:
            message (MessageType): Message to add.

        Examples:
            >>> from chat_object import Chat, Message, Role
            >>> chat = Chat()
            >>> chat.add(Message(Role.User, "Hello"))
            >>> len(chat)
            1
            >>> chat[0].content
            'Hello'

            >>> chat.add({"role": "assistant", "content": "Hi!"})
            >>> len(chat)
            2
            >>> chat[1].content
            'Hi!'
        """
        self._messages.append(self._validate_message(message))

    def get_messages(self) -> list[Message]:
        """
        Returns the list of messages in the chat.

        Returns:
            list[Message]: List of messages.

        Examples:
            >>> from chat_object import Chat, Message, Role
            >>> msg1 = Message(Role.User, "Hello")
            >>> msg2 = Message(Role.Assistant, "Hi!")
            >>> chat = Chat(msg1, msg2)
            >>> messages = chat.get_messages()
            >>> len(messages)
            2
            >>> messages[0].role
            'user'
            >>> messages[1].role
            'assistant'
        """
        return self._messages

    def extend(self, messages: Iterable[MessageType]) -> None:
        """
        Extends the chat with multiple messages.

        Args:
            messages (list[MessageType]): List of messages to add.

        Examples:
            >>> from chat_object import Chat, Message, Role
            >>> chat = Chat()
            >>> msg1 = Message(Role.User, "Hello")
            >>> msg2 = Message(Role.Assistant, "Hi!")
            >>> chat.extend([msg1, msg2])
            >>> len(chat)
            2

            >>> chat.extend([{"role": "user", "content": "How are you?"}])
            >>> len(chat)
            3
            >>> chat[2].content
            'How are you?'
        """
        for message in messages:
            self._messages.append(self._validate_message(message))

    def clear(self) -> None:
        """
        Removes all messages from the chat.

        Examples:
            >>> from chat_object import Chat, Message, Role
            >>> msg1 = Message(Role.User, "Hello")
            >>> msg2 = Message(Role.Assistant, "Hi!")
            >>> chat = Chat(msg1, msg2)
            >>> len(chat)
            2
            >>> chat.clear()
            >>> len(chat)
            0
            >>> chat.messages
            ()
        """
        self._messages.clear()

    def as_dict(self) -> list[dict[str, str]]:
        """
        Returns a list of dictionaries representing the messages in the chat.
        Role values are already strings, so no conversion is needed.

        Returns:
            list[dict[str, str]]: List of dictionaries with 'role' and 'content' keys.

        Examples:
            >>> from chat_object import Chat, Message, Role
            >>> msg1 = Message(Role.User, "Hello")
            >>> msg2 = Message(Role.Assistant, "Hi!")
            >>> chat = Chat(msg1, msg2)
            >>> chat.as_dict()
            [{'role': 'user', 'content': 'Hello'}, {'role': 'assistant', 'content': 'Hi!'}]
        """
        return [
            {"role": message.role, "content": message.content}
            for message in self._messages
        ]

    def append(self, message: MessageType) -> None:
        """
        List-like append method.

        Examples:
            >>> from chat_object import Chat, Message, Role
            >>> chat = Chat()
            >>> chat.append(Message(Role.User, "Hello"))
            >>> len(chat)
            1
            >>> chat.append({"role": "assistant", "content": "Hi!"})
            >>> len(chat)
            2
        """
        self.add(message)

    def insert(self, index: int, message: MessageType) -> None:
        """
        List-like insert method.

        Examples:
            >>> from chat_object import Chat, Message, Role
            >>> chat = Chat(Message(Role.User, "Hello"))
            >>> chat.insert(0, Message(Role.System, "You are helpful"))
            >>> len(chat)
            2
            >>> chat[0].role
            'system'
        """
        self._messages.insert(index, self._validate_message(message))

    def pop(self, index: int = -1) -> Message:
        """
        List-like pop method.

        Examples:
            >>> from chat_object import Chat, Message, Role
            >>> chat = Chat(Message(Role.User, "Hello"), Message(Role.Assistant, "Hi!"))
            >>> msg = chat.pop()
            >>> msg.role
            'assistant'
            >>> len(chat)
            1
        """
        return self._messages.pop(index)

    def remove(self, message: MessageType) -> None:
        """
        List-like remove method.

        Examples:
            >>> from chat_object import Chat, Message, Role
            >>> msg = Message(Role.User, "Hello")
            >>> chat = Chat(msg, Message(Role.Assistant, "Hi!"))
            >>> chat.remove(msg)
            >>> len(chat)
            1
            >>> chat[0].role
            'assistant'
        """
        validated_message = self._validate_message(message)
        self._messages.remove(validated_message)

    def index(self, message: MessageType) -> int:
        """
        List-like index method.

        Examples:
            >>> from chat_object import Chat, Message, Role
            >>> msg = Message(Role.User, "Hello")
            >>> chat = Chat(msg, Message(Role.Assistant, "Hi!"))
            >>> chat.index(msg)
            0
        """
        validated_message = self._validate_message(message)
        return self._messages.index(validated_message)

    def count(self, message: MessageType) -> int:
        """
        List-like count method.

        Examples:
            >>> from chat_object import Chat, Message, Role
            >>> msg = Message(Role.User, "Hello")
            >>> chat = Chat(msg, msg, Message(Role.Assistant, "Hi!"))
            >>> chat.count(msg)
            2
        """
        validated_message = self._validate_message(message)
        return self._messages.count(validated_message)

    def reverse(self) -> None:
        """
        List-like reverse method.

        Examples:
            >>> from chat_object import Chat, Message, Role
            >>> chat = Chat(Message(Role.User, "Hello"), Message(Role.Assistant, "Hi!"))
            >>> chat.reverse()
            >>> chat[0].role
            'assistant'
        """
        self._messages.reverse()

    def sort(
        self, key: Callable[[Message], Any] = lambda x: x, reverse: bool = False
    ) -> None:
        """
        List-like sort method.

        Examples:
            >>> from chat_object import Chat, Message, Role
            >>> chat = Chat(Message(Role.Assistant, "Hi!"), Message(Role.User, "Hello"))
            >>> chat.sort(key=lambda msg: msg.role)
            >>> chat[0].role
            'assistant'
        """
        self._messages.sort(key=key, reverse=reverse)

    def __contains__(self, string: str) -> bool:
        """
        >>> from chat_object import Chat, Message, Role
        >>> "Hello" in Chat(Message(Role.Assistant, "Hello World!"))
        True
        >>> "Goodbye" in Chat(Message(Role.Assistant, "Hello World!"))
        False
        """
        return any(string in message for message in self._messages)

    def __str__(self) -> str:
        """
        >>> from chat_object import Chat, Message, Role
        >>> msg1 = Message(Role.User, "Hello")
        >>> msg2 = Message(Role.Assistant, "Hi there!")
        >>> chat = Chat(msg1, msg2)
        >>> str(chat)
        'user: Hello\\nassistant: Hi there!'
        """
        return "\n".join(str(message) for message in self._messages)

    def __repr__(self) -> str:
        """
        >>> from chat_object import Chat, Message, Role
        >>> msg = Message(Role.User, "Hello")
        >>> chat = Chat(msg)
        >>> repr(chat)
        "Chat(messages=Message(role='user', content='Hello'))"

        >>> chat2 = Chat()
        >>> repr(chat2)
        'Chat(messages=[])'
        """
        return f"Chat(messages={', '.join(repr(message) for message in self._messages) if self._messages else '[]'})"

    def __eq__(self, other: object) -> bool:
        """
        >>> from chat_object import Chat, Message, Role
        >>> msg1 = Message(Role.User, "Hello")
        >>> msg2 = Message(Role.Assistant, "Hi!")
        >>> chat1 = Chat(msg1, msg2)
        >>> chat2 = Chat(msg1, msg2)
        >>> chat3 = Chat(msg2, msg1)

        >>> chat1 == chat2
        True
        >>> chat1 == chat3
        False
        """
        if not isinstance(other, Chat):
            return NotImplemented
        return self._messages == other._messages

    def __hash__(self) -> int:
        """
        >>> from chat_object import Chat, Message, Role
        >>> msg1 = Message(Role.User, "Hello")
        >>> msg2 = Message(Role.Assistant, "Hi!")
        >>> chat1 = Chat(msg1, msg2)
        >>> chat2 = Chat(msg1, msg2)
        >>> hash(chat1) == hash(chat2)
        True
        """
        return hash(tuple(self._messages))

    def __len__(self) -> int:
        """
        >>> from chat_object import Chat, Message, Role
        >>> chat = Chat()
        >>> len(chat)
        0

        >>> msg1 = Message(Role.User, "Hello")
        >>> msg2 = Message(Role.Assistant, "Hi!")
        >>> chat = Chat(msg1, msg2)
        >>> len(chat)
        2
        """
        return len(self._messages)

    def __getitem__(self, index: int) -> Message:
        """
        >>> from chat_object import Chat, Message, Role
        >>> msg1 = Message(Role.User, "Hello")
        >>> msg2 = Message(Role.Assistant, "Hi!")
        >>> chat = Chat(msg1, msg2)
        >>> chat[0].content
        'Hello'
        >>> chat[1].content
        'Hi!'
        >>> chat[0].role
        'user'
        """
        return self._messages[index]

    def __setitem__(self, index: int, message: MessageType) -> None:
        """
        >>> from chat_object import Chat, Message, Role
        >>> chat = Chat(Message(Role.User, "Hello"))
        >>> chat[0] = Message(Role.Assistant, "Hi!")
        >>> chat[0].role
        'assistant'
        """
        self._messages[index] = self._validate_message(message)

    def __delitem__(self, index: int) -> None:
        """
        >>> from chat_object import Chat, Message, Role
        >>> chat = Chat(Message(Role.User, "Hello"), Message(Role.Assistant, "Hi!"))
        >>> del chat[0]
        >>> len(chat)
        1
        >>> chat[0].role
        'assistant'
        """
        del self._messages[index]

    def __iter__(self) -> Iterator[Message]:
        """
        >>> from chat_object import Chat, Message, Role
        >>> chat = Chat(Message(Role.User, "Hello"), Message(Role.Assistant, "Hi!"))
        >>> messages = list(chat)
        >>> len(messages)
        2
        >>> messages[0].role
        'user'
        """
        return iter(self._messages)
