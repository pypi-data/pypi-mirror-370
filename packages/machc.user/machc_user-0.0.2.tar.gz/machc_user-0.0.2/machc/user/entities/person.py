from .user_id import UserId


class Person(UserId):
    """
    The Person class extends the UserId class by adding a username attribute.
    It represents an entity that not only has a unique ID but also additional
    key information such as a username.

    This class is part of the machc_core entity module for managing users.
    """

    def __init__(self, username: str = None):
        """
        Constructs a Person object with the specified username.

        Args:
            username (str, optional): The username of the person. Defaults to None.
        """
        super().__init__()
        self._username = username

    def get_username(self) -> str:
        """
        Retrieves the username of the person.

        Returns:
            str: The username of the person.
        """
        return self._username

    def set_username(self, username: str):
        """
        Sets or updates the username of the person.

        Args:
            username (str): The new username to assign to the person.
        """
        self._username = username