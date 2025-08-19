"""Dependency injection utilities for SQS message handlers.

Provides the SqsDepends class for declaring dependencies that will be
automatically injected into handler functions.
"""

from typing import Callable


class SqsDepends():
    """Dependency injection marker for SQS message handlers.
    
    Used to declare dependencies that should be automatically injected
    into handler functions. The dependency injection system will resolve
    and provide instances of the specified interface/class.
    
    Attributes:
        interface: The class or interface to inject
        
    Example:
        >>> class UserService:
        ...     def get_user(self, user_id: int): ...
        >>> 
        >>> @app.handler("user.created")
        >>> async def handle_user(
        ...     message: dict,
        ...     user_service: UserService = SqsDepends(UserService)
        ... ):
        ...     user = user_service.get_user(message["user_id"])
    """

    def __init__(self, interface: Callable) -> None:
        """Initialize dependency marker.
        
        Args:
            interface: The class or callable to inject as a dependency
        """
        self.interface = interface
