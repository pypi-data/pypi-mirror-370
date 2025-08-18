from abc import ABC, abstractmethod

from machc.user.entities.user import UserId
from machc.user.entities.user.login_credential import LoginCredential


class UserLoginService(ABC):
    """
    An abstract base class (interface) for the UserLoginService.
    This service defines the contract for login operations, ensuring consistent authentication
    behavior across different implementations.

    Methods:
        login(login_credential): Authenticates a user_service using their login credentials and returns their UserId.
    """

    @abstractmethod
    def login(self, login_credential: LoginCredential) -> UserId:
        """
        Authenticates a user_service using their login credentials.

        Args:
            login_credential (LoginCredential): The user_service's login credentials.

        Returns:
            UserId: The unique identifier of the authenticated user_service.

        Raises:
            UserException: If authentication fails or credentials are invalid.
        """
        pass