class ReactionException(Exception):
    pass


class ReactionCommandFailed(ReactionException):
    pass


class UnsupportedLine(ReactionException):
    pass


class UnsupportedLog(ReactionException):
    pass


class UnmatchedPattern(ReactionException):
    pass
