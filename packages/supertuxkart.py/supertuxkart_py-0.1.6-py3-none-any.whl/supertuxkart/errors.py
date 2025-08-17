class SuperTuxKartError(Exception):
    """Base class for all SuperTuxKart errors"""

    pass


class InvalidSession(SuperTuxKartError):
    """Raised when session is invalid"""

    pass


class CannotFriendSelf(SuperTuxKartError):
    """Raised when trying to friend themselves"""

    pass


class AuthFailure(Exception):
    """Raised when authentication fails"""

    pass


class UsernameRequired(AuthFailure):
    """Raised when a username is required"""

    pass


class PasswordRequired(AuthFailure):
    """Raised when a password is required"""

    pass


class InvalidCredentials(AuthFailure):
    """Raised when the username or password is incorrect"""

    pass
