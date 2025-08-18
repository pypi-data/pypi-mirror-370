class LoginCredential:
    """
    Represents user_service login credentials (e.g., username and password).
    """

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def get_username(self) -> str:
        return self.username

    def get_password(self) -> str:
        return self.password