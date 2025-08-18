from .person import Person, UserId


class AuthenticatedPerson(Person):
    """
    The AuthenticatedPerson class extends the Person class by adding an association with a UserId.
    It represents an authenticated individual, combining username and unique user_service identification.

    This class is designed to support authentication and identification logic within the Machc project.
    """

    def __init__(self, username: str, user_id: UserId = None):
        """
        Constructs an AuthenticatedPerson object with the specified username and optional UserId.

        Args:
            username (str): The username of the authenticated person.
            user_id (UserId, optional): The UserId associated with the person. Defaults to None.
        """
        super().__init__(username=username)
        self._user_id = user_id

    def get_user_id(self) -> UserId:
        """
        Retrieves the UserId associated with the authenticated person.

        Returns:
            UserId: The UserId of the person, or None if not set.
        """
        return self._user_id

    def set_user_id(self, user_id: UserId):
        """
        Sets or updates the UserId associated with the authenticated person.

        Args:
            user_id (UserId): The new UserId to assign.
        """
        self._user_id = user_id