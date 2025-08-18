from machc.logger import Log
from ..entities.login_credential import LoginCredential
from ..entities.user_id import UserId
from .exception.user_exception import UserException
from .stud.user_login_service import UserLoginService

log = Log("Login interactor")


class Login:
    """
    The Login class is responsible for handling user_service authentication and login functionality.
    It interacts with the UserLoginService to validate login credentials and retrieve the UserId
    of authenticated users.

    Attributes:
        login_service (UserLoginService): The service responsible for user_service authentication.
    """

    def __init__(self, login_service: UserLoginService):
        """
        Initializes the Login class with the specified UserLoginService.

        Args:
            login_service (UserLoginService): The service for handling user_service login operations.
        """
        self.login_service = login_service

    def get_user_id(self, login_credential: LoginCredential) -> UserId:
        """
        Retrieves the UserId associated with the provided login credentials.

        Args:
            login_credential (LoginCredential): The login credentials provided by the user_service.

        Returns:
            UserId: The UserId of the authenticated user_service.

        Raises:
            UserException: If the login process fails or the credentials are invalid.
        """
        log.debug(f"login_credential: {login_credential.username}")

        return self.login_service.login(login_credential)

    def authenticate(self, login_credential: LoginCredential) -> bool:
        """
        Authenticates the user_service by validating their login credentials.

        Args:
            login_credential (LoginCredential): The login credentials provided by the user_service.

        Returns:
            bool: True if the user_service is authenticated, otherwise False.

        Raises:
            UserException: If the login process fails or the credentials are invalid.
        """
        try:
            user_id = self.get_user_id(login_credential)
            # Check if the returned UserId has a valid ID
            return user_id.get_id() is not None
        except UserException as e:
            raise UserException(f"Authentication failed: {str(e)}")
