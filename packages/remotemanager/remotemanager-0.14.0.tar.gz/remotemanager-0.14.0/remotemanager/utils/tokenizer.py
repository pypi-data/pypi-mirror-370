"""Module to store the tokenizer class"""

import tokenize
from typing import Union


class Tokenizer:
    """
    generate_tokens() requires a file-like object to function

    This class mimics this behaviour by raising StopIteration once the
    end of the content is reached.
    """

    __slots__ = ["content", "row", "_tokens", "_names", "_numbers"]

    def __init__(self, content: str):
        self.content = content.split("\n")
        self.row = 0

        self._names = None
        self._numbers = None
        self._tokens = []
        self.tokenize()

    def __call__(self) -> Union[str, StopIteration]:
        if self.row == len(self.content):
            self.row = 0  # reset
            raise StopIteration
        line = self.content[self.row]
        self.row += 1
        return line

    def tokenize(self) -> list:
        """Runs the tokenization"""
        for token in tokenize.generate_tokens(self):  # type: ignore
            self._tokens.append([token.type, token.string.strip()])
        return self.tokens

    @property
    def tokens(self) -> list:
        """
        Returns all stored tokens

        list format is [(type, string), ...]
        """
        return self._tokens

    @property
    def names(self) -> list:
        """Returns the derived name list"""
        if self._names is None:
            tmp = []
            for token in self.tokens:
                if token[0] == 1 and token[1] not in tmp:
                    tmp.append(token[1])
            self._names = tmp
        return self._names

    @property
    def numbers(self) -> list:
        """Returns derived number list"""
        if self._numbers is None:
            tmp = []
            for token in self.tokens:
                if token[0] == 2 and token[1] not in tmp:
                    tmp.append(token[1])
            self._numbers = tmp
        return self._numbers

    def exchange_name(self, a: str, b: str):
        """
        Exchanges name a with name b
        """
        for token in self.tokens:
            if token[1] == a:
                token[1] = b
        self._names = None  # invalidate the name cache

    @property
    def source(self):
        """
        Regenerate the source from the stored tokens

        untokenize is... unreliable, since it focuses on the
        repeatability of the round trip

        So we should reconstruct manually

        Key tokens:
        0: End marker
        1: Name
        2: Number
        3: String
        4: Newline
        5: Indent
        6: Dedent
        54: iterable related characters such as `()` `[]` `,`

        Returns:
            (str): reconstructed source
        """
        indent = 0
        output = []
        tmp = []
        for i, (ttype, token) in enumerate(self.tokens):
            if ttype in (
                0,
                4,
            ):  # end of line, add the cached line at the correct indent
                output.append("    " * indent + "".join(tmp))
                tmp = []
                continue
            if ttype == 5:  # indent token, increase indent
                output.append("    " * indent + "".join(tmp))
                tmp = []
                indent += 1
                continue
            if ttype == 6:  # dedent token, decrease indent
                output.append("    " * indent + "".join(tmp))
                tmp = []
                indent -= 1

            # If the current token is a registered name (or a number), and is followed
            # immediately by another, add a space to separate them
            try:
                # self.tokens[i + 1][0] is the token type of the following token
                nexttype = self.tokens[i + 1][0]
            except AttributeError:
                nexttype = 0

            # prevent character joining by requesting an additional space
            request_space = False
            # names and numbers should always be followed by whitespace
            if token in self.names or ttype == 2:
                request_space = True
            elif token in (",", "="):  # formatting tweaks
                request_space = True

            if request_space and nexttype in (1, 2):
                token += " "

            tmp.append(token)

        return "\n".join(output).strip()
