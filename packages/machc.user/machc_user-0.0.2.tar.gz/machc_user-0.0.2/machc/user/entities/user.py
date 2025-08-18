from .authenticated_person import AuthenticatedPerson
from .user_profile import UserProfile


class User(AuthenticatedPerson):
    """
    The User class extends the AuthenticatedPerson class, representing an authenticated individual
    within the system. It introduces the concept of a user_service profile, encapsulated in the UserProfile object.

    This class is a foundational part of the user_service management system in the Machc project.
    """

    def __init__(self, username: str = None):
        """
        Initializes a User instance with a username and an associated UserProfile.

        Args:
            username (str, optional): The username for this authenticated user_service. Defaults to None.
        """
        super().__init__(username)  # Call the parent class constructor
        self._profile = UserProfile()  # Initialize with a new UserProfile object

    @property
    def profile(self) -> UserProfile:
        """
        Retrieves the UserProfile associated with this user_service.

        Returns:
            UserProfile: The profile of this user_service.
        """
        return self._profile

    @profile.setter
    def profile(self, profile: UserProfile):
        """
        Sets or updates the UserProfile associated with this user_service.

        Args:
            profile (UserProfile): The updated UserProfile object.
        """
        self._profile = profile