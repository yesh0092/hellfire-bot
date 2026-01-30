def require_level(level: int):
    """
    Attach required staff level to a command.
    """
    def decorator(func):
        func.required_level = level
        return func
    return decorator
