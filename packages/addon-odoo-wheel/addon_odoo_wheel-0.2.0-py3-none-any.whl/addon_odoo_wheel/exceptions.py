class UnsupportedOperation(NotImplementedError):
    pass


class WhoolMangonoException(Exception):
    pass


class NoScmFound(WhoolMangonoException):
    pass


class OnlyCommunityAddonsException(WhoolMangonoException):
    pass


class CantResolveAddonException(WhoolMangonoException):
    pass
