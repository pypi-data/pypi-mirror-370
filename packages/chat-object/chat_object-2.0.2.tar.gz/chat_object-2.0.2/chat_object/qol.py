from .role import Role
from .consts import RoleType, MessageContent
from .message import Message
from .chat_obj import Chat
from .prompt import Prompt


def msgs(*messages: tuple[RoleType, MessageContent] | Message) -> list[Message]:
    """
    Quickly create a list of Message objects from tuples or Message instances.

    Args:
        *messages: Each message can be a tuple (role, content) or a Message object.

    Returns:
        list[Message]: List of Message objects.

    Examples:
        >>> from chat_object.qol import msgs
        >>> from chat_object import Message
        >>> msgs(("user", "Hello"), ("assistant", "Hi!"))
        [Message(role='user', content='Hello'), Message(role='assistant', content='Hi!')]
        >>> msgs(Message("user", "Hello"))
        [Message(role='user', content='Hello')]
    """
    new_messages = []
    for msg in messages:
        if isinstance(msg, Message):
            new_messages.append(msg)
        else:
            role, content = msg
            new_messages.append(Message(role, content))
    return new_messages


def chat(*messages: tuple[RoleType, MessageContent] | Message) -> Chat:
    """
    Quickly create a Chat object from tuples or Message objects.

    Args:
        *messages: Each message can be a tuple (role, content) or a Message object.

    Returns:
        Chat: A Chat object containing the provided messages.

    Examples:
        >>> from chat_object.qol import chat
        >>> chat(("user", "Hello"), ("assistant", "Hi!"))
        Chat(messages=Message(role='user', content='Hello'), Message(role='assistant', content='Hi!'))
    """
    return Chat(*msgs(*messages))


def msg(role: RoleType, content: MessageContent) -> Message:
    """
    Quickly create a Message object.

    Args:
        role (RoleType): The role of the message (e.g., "user", "assistant").
        content (str): The content of the message.

    Returns:
        Message: The created Message object.

    Examples:
        >>> msg("user", "Hello")
        Message(role='user', content='Hello')
    """
    return Message(role, content)


def msg_user(content: MessageContent) -> Message:
    """
    Quickly create a Message object with the user role.
    """
    return Message(Role.User, content)


def msg_assistant(content: MessageContent) -> Message:
    """
    Quickly create a Message object with the assistant role.
    """
    return Message(Role.Assistant, content)


def msg_system(content: MessageContent) -> Message:
    """
    Quickly create a Message object with the system role.
    """
    return Message(Role.System, content)


def prmt(content: str) -> Prompt:
    """
    Quickly create a Prompt object.

    Args:
        content (str): The prompt content.

    Returns:
        Prompt: The created Prompt object.

    Examples:
        >>> prmt("You are a helpful assistant.")
        Prompt('You are a helpful assistant.')
    """
    return Prompt(content)
