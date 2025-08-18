from typing import Union
import textwrap


class Prompt:
    """
    A class for creating prompts for chat models.

    Primarily intended to be used with triple-quoted strings. The class will automatically
    strip the string and remove common leading whitespace from each line while preserving
    relative indentation.

    Attributes:
        content (str): The processed prompt content with normalized indentation.

    Examples:
        >>> prompt = Prompt(\"\"\"
        ...     Hello
        ...      World
        ...         This is a test
        ... \"\"\")
        >>> print(prompt)
        Hello
         World
            This is a test

        >>> # Multiple arguments are joined with newlines
        >>> prompt = Prompt("First line", "Second line", "Third line")
        >>> print(prompt)
        First line
        Second line
        Third line

        >>> # Empty prompt
        >>> empty = Prompt("")
        >>> str(empty)
        ''

        >>> # Single line
        >>> single = Prompt("Hello World")
        >>> str(single)
        'Hello World'

        >>> # Prompt with only whitespace
        >>> whitespace = Prompt("   \\n  \\n   ")
        >>> str(whitespace)
        ''
    """

    def __init__(self, *prompt: str):
        """
        Initialize a Prompt with one or more strings.

        Args:
            *prompt (str): One or more strings to create the prompt from.
                          Multiple strings will be joined with newlines.

        Examples:
            >>> p = Prompt("Hello")
            >>> p.content
            'Hello'

            >>> p2 = Prompt("Line 1", "Line 2")
            >>> p2.content
            'Line 1\\nLine 2'

            >>> # Handling indented text
            >>> p3 = Prompt(\"\"\"
            ...     def function():
            ...         return "hello"
            ...
            ...     print("world")
            ... \"\"\")
            >>> print(p3)
            def function():
                return "hello"
            <BLANKLINE>
            print("world")
        """
        if not prompt:
            self.content = ""
        else:
            # Join all arguments with newlines
            combined_text = "\n".join(prompt)
            # Process the text to remove common indentation
            self.content = self._process_text(combined_text)

    def _process_text(self, text: str) -> str:
        """
        Process text to remove common leading whitespace while preserving relative indentation.

        Args:
            text (str): Raw text input.

        Returns:
            str: Processed text with normalized indentation.

        Examples:
            >>> p = Prompt("")
            >>> p._process_text("    Hello\\n      World")
            'Hello\\n  World'

            >>> p._process_text("\\n    Line 1\\n      Line 2\\n    ")
            'Line 1\\n  Line 2'

            >>> p._process_text("   ")
            ''
        """
        if not text or text.isspace():
            return ""

        # Use textwrap.dedent to remove common leading whitespace
        processed = textwrap.dedent(text)

        # Strip leading and trailing newlines
        processed = processed.strip()

        return processed

    def append(self, text: str) -> None:
        """
        Append text to the existing prompt content.

        Args:
            text (str): Text to append.

        Examples:
            >>> p = Prompt("Hello")
            >>> p.append("World")
            >>> str(p)
            'Hello\\nWorld'

            >>> p.append("")
            >>> str(p)
            'Hello\\nWorld\\n'
        """
        if self.content:
            self.content += "\n" + self._process_text(text)
        else:
            self.content = self._process_text(text)

    def prepend(self, text: str) -> None:
        """
        Prepend text to the existing prompt content.

        Args:
            text (str): Text to prepend.

        Examples:
            >>> p = Prompt("World")
            >>> p.prepend("Hello")
            >>> str(p)
            'Hello\\nWorld'
        """
        processed_text = self._process_text(text)
        if self.content:
            self.content = processed_text + "\n" + self.content
        else:
            self.content = processed_text

    def clear(self) -> None:
        """
        Clear the prompt content.

        Examples:
            >>> p = Prompt("Some content")
            >>> p.clear()
            >>> str(p)
            ''
        """
        self.content = ""

    def replace(self, old: str, new: str) -> "Prompt":
        """
        Return a new Prompt with all occurrences of old replaced with new.

        Args:
            old (str): String to replace.
            new (str): Replacement string.

        Returns:
            Prompt: New Prompt instance with replacements made.

        Examples:
            >>> p = Prompt("Hello World")
            >>> p2 = p.replace("World", "Universe")
            >>> str(p2)
            'Hello Universe'
            >>> str(p)  # Original unchanged
            'Hello World'
        """
        new_content = self.content.replace(old, new)
        return Prompt(new_content)

    def copy(self) -> "Prompt":
        """
        Create a copy of the prompt.

        Returns:
            Prompt: A new Prompt instance with the same content.

        Examples:
            >>> p1 = Prompt("Hello")
            >>> p2 = p1.copy()
            >>> p2 is p1
            False
            >>> str(p1) == str(p2)
            True
        """
        return Prompt(self.content)

    def strip(self) -> "Prompt":
        """
        Return a new Prompt with leading and trailing whitespace removed.

        Returns:
            Prompt: New Prompt instance with stripped content.

        Examples:
            >>> p = Prompt("  Hello World  ")
            >>> p2 = p.strip()
            >>> str(p2)
            'Hello World'
        """
        return Prompt(self.content.strip())

    def __str__(self) -> str:
        """
        Return the string representation of the prompt content.

        Returns:
            str: The processed prompt content.

        Examples:
            >>> p = Prompt("Hello")
            >>> str(p)
            'Hello'
        """
        return self.content

    def __repr__(self) -> str:
        """
        Return the official string representation of the Prompt.

        Returns:
            str: String representation showing the constructor call.

        Examples:
            >>> p = Prompt("Hello")
            >>> repr(p)
            "Prompt('Hello')"

            >>> p2 = Prompt("")
            >>> repr(p2)
            "Prompt('')"
        """
        return f"Prompt({self.content!r})"

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another Prompt or string.

        Args:
            other: Object to compare with.

        Returns:
            bool: True if contents are equal, False otherwise.

        Examples:
            >>> p1 = Prompt("Hello")
            >>> p2 = Prompt("Hello")
            >>> p1 == p2
            True

            >>> p1 == "Hello"
            True

            >>> p1 == "World"
            False
        """
        if isinstance(other, Prompt):
            return self.content == other.content
        elif isinstance(other, str):
            return self.content == other
        return NotImplemented

    def __len__(self) -> int:
        """
        Return the length of the prompt content.

        Returns:
            int: Number of characters in the content.

        Examples:
            >>> p = Prompt("Hello")
            >>> len(p)
            5

            >>> p2 = Prompt("")
            >>> len(p2)
            0
        """
        return len(self.content)

    def __bool__(self) -> bool:
        """
        Return True if the prompt has content, False otherwise.

        Returns:
            bool: True if content is not empty, False otherwise.

        Examples:
            >>> p = Prompt("Hello")
            >>> bool(p)
            True

            >>> p2 = Prompt("")
            >>> bool(p2)
            False
        """
        return bool(self.content)

    def __contains__(self, item: str) -> bool:
        """
        Check if the prompt content contains the specified string.

        Args:
            item (str): String to search for.

        Returns:
            bool: True if item is found in content, False otherwise.

        Examples:
            >>> p = Prompt("Hello World")
            >>> "Hello" in p
            True

            >>> "xyz" in p
            False
        """
        return item in self.content

    def __add__(self, other: Union["Prompt", str]) -> "Prompt":
        """
        Concatenate this prompt with another prompt or string.

        Args:
            other (Union[Prompt, str]): Prompt or string to concatenate.

        Returns:
            Prompt: New Prompt with concatenated content.

        Examples:
            >>> p1 = Prompt("Hello")
            >>> p2 = Prompt("World")
            >>> p3 = p1 + p2
            >>> str(p3)
            'Hello\\nWorld'

            >>> p4 = p1 + " there"
            >>> str(p4)
            'Hello\\n there'
        """
        if isinstance(other, Prompt):
            if self.content and other.content:
                return Prompt(self.content + "\n" + other.content)
            elif self.content:
                return Prompt(self.content)
            else:
                return Prompt(other.content)
        elif isinstance(other, str):
            if self.content and other:
                return Prompt(self.content + "\n" + other)
            elif self.content:
                return Prompt(self.content)
            else:
                return Prompt(other)
        return NotImplemented

    def __hash__(self) -> int:
        """
        Return hash of the prompt content.

        Returns:
            int: Hash value of the content.

        Examples:
            >>> p1 = Prompt("Hello")
            >>> p2 = Prompt("Hello")
            >>> hash(p1) == hash(p2)
            True
        """
        return hash(self.content)
