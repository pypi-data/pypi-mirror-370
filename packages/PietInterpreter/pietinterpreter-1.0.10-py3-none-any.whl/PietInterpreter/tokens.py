class BaseLexerToken():
    def __init__(self, tokenType: str):
        self.tokenType = tokenType

    def __str__(self):
        return f"Token type = {self.tokenType}"

    def __repr__(self):
        return str(self)


class BoBlackToken(BaseLexerToken):
    """
    Used when a transition to black (or edge) occurs
    """

    def __init__(self, tokenType: str = "toBlack"):
        super().__init__(tokenType)


class ToWhiteToken(BaseLexerToken):
    """
    Used when a transition to white occurs
    """

    def __init__(self):
        super().__init__("toWhite")


class TerminateToken(BaseLexerToken):
    """
    Used when a codel has no possible way to escape (8 * toBlack)
    """

    def __init__(self):
        super().__init__("exit")


class ToColorToken(BaseLexerToken):
    """
    Used when a transition to a color occurs
    """

    def __init__(self, tokenType: str, codelSize: int):
        super().__init__(tokenType)
        self.codelSize = codelSize

    def __str__(self):
        return f"{super().__str__()}, codelSize = {self.codelSize}"


def getTokenType(hueChange: int, lightChange: int) -> str:
    """
    Find the toColorToken type based on hue change and lightness change
    :param hueChange: number of hue changes between two pixels
    :param lightChange: number of lightness changes between two pixels
    :return: A string with the toColorToken type
    """
    tokens = [
        ["noop", "push", "pop"],
        ["add", "subtract", "multiply"],
        ["divide", "mod", "not"],
        ["greater", "pointer", "switch"],
        ["duplicate", "roll", "inN"],
        ["inC", "outN", "outC"],
    ]
    return tokens[hueChange][lightChange]
