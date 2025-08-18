from abc import ABC, abstractmethod

class UserRegistrationData:
    """
    Represents user data needed for registration.
    """
    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.password = password
        self.first_name = ""
        self.last_name = ""

    def __str__(self):
        return f"UserRegistrationData(username={self.username}, email={self.email})"



class UserRegistrationService(ABC):
    """
    The UserRegistrationService abstract base class defines a contract
    for implementing user registration functionality.

    Subclasses must provide an implementation of the register method.
    """

    @abstractmethod
    def register(self, user: UserRegistrationData) -> None:
        """
        Registers a user using the provided UserRegistrationData.

        Args:
            user (UserRegistrationData): The user's registration details.

        Raises:
            UserException: If registration fails or there are validation errors.
        """
        pass