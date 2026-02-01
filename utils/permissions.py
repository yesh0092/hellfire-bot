from functools import wraps


def require_level(level: int):
    """
    Attach a required staff level to a command.

    Used by the global command guard to enforce staff hierarchy.
    Level must be a positive integer.
    """

    if not isinstance(level, int) or level < 1:
        raise ValueError("require_level() expects a positive integer")

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        # Attach required level metadata
        wrapper.required_level = level
        return wrapper

    return decorator
