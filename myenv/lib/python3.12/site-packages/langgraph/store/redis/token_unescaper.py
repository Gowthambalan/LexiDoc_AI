import re
from typing import Match, Optional, Pattern


class TokenUnescaper:
    """Unescape previously escaped punctuation within an input string.

    Handles unescaping of RediSearch escaped characters. Should be used to unescape
    strings that were previously escaped using TokenEscaper.
    """

    # Pattern to match escaped characters (backslash followed by any character)
    DEFAULT_UNESCAPED_PATTERN = r"\\(.)"

    def __init__(self, unescape_pattern: Optional[Pattern] = None):
        if unescape_pattern:
            self.unescaped_pattern_re = unescape_pattern
        else:
            self.unescaped_pattern_re = re.compile(self.DEFAULT_UNESCAPED_PATTERN)

    def unescape(self, value: str) -> str:
        """Unescape a RedisSearch escaped string.

        Args:
            value: The string to unescape

        Returns:
            The unescaped string with backslash escapes removed

        Raises:
            TypeError: If input value is not a string
        """
        if not isinstance(value, str):
            raise TypeError(
                f"Value must be a string object for token unescaping, got type {type(value)}"
            )

        def unescape_symbol(match: Match[str]) -> str:
            # Return just the character after the backslash
            return match.group(1)

        return self.unescaped_pattern_re.sub(unescape_symbol, value)
