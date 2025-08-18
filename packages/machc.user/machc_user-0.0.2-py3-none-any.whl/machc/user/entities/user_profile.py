from typing import Optional
from datetime import datetime
from machc.base import Address

class UserProfile:
    """
    The UserProfile class represents the profile of a user_service, encapsulating key attributes like personal details,
    contact information, and registration metadata. It provides setter and getter methods for controlled
    access to user_service profile attributes.
    """

    def __init__(
        self,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        middle_name: Optional[str] = None,
        last_name: Optional[str] = None,
        gender: Optional[str] = None,
        date_of_birth: Optional[datetime] = None,
        locale: Optional[str] = None,
        auto_login: Optional[bool] = None,
        description: Optional[str] = None,
        registration_date: Optional[datetime] = None,
        home_address: Optional[Address] = None,
        shipping_address: Optional[Address] = None
    ):
        """
        Initializes a new instance of the UserProfile class.

        Args:
            email (Optional[str]): The user_service's email address.
            first_name (Optional[str]): The user_service's first name.
            middle_name (Optional[str]): The user_service's middle name.
            last_name (Optional[str]): The user_service's last name.
            gender (Optional[str]): The user_service's gender.
            date_of_birth (Optional[datetime]): The user_service's date of birth.
            locale (Optional[str]): The user_service's locale (language/region preferences).
            auto_login (Optional[bool]): Whether auto-login is enabled for the user_service.
            description (Optional[str]): A brief description of the user_service.
            registration_date (Optional[datetime]): The date the user_service registered.
            home_address (Optional[Address]): The user_service's home address.
            shipping_address (Optional[Address]): The user_service's shipping address.
        """
        self._email = email
        self._first_name = first_name
        self._middle_name = middle_name
        self._last_name = last_name
        self._gender = gender
        self._date_of_birth = date_of_birth
        self._locale = locale
        self._auto_login = auto_login
        self._description = description
        self._registration_date = registration_date
        self._home_address = home_address
        self._shipping_address = shipping_address

    # Getters and setters
    def get_email(self) -> Optional[str]:
        return self._email

    def set_email(self, email: str):
        self._email = email

    def get_first_name(self) -> Optional[str]:
        return self._first_name

    def set_first_name(self, first_name: str):
        self._first_name = first_name

    def get_middle_name(self) -> Optional[str]:
        return self._middle_name

    def set_middle_name(self, middle_name: str):
        self._middle_name = middle_name

    def get_last_name(self) -> Optional[str]:
        return self._last_name

    def set_last_name(self, last_name: str):
        self._last_name = last_name

    def get_gender(self) -> Optional[str]:
        return self._gender

    def set_gender(self, gender: str):
        self._gender = gender

    def get_date_of_birth(self) -> Optional[datetime]:
        return self._date_of_birth

    def set_date_of_birth(self, date_of_birth: datetime):
        self._date_of_birth = date_of_birth

    def get_locale(self) -> Optional[str]:
        return self._locale

    def set_locale(self, locale: str):
        self._locale = locale

    def get_auto_login(self) -> Optional[bool]:
        return self._auto_login

    def set_auto_login(self, auto_login: bool):
        self._auto_login = auto_login

    def get_description(self) -> Optional[str]:
        return self._description

    def set_description(self, description: str):
        self._description = description

    def get_registration_date(self) -> Optional[datetime]:
        return self._registration_date

    def set_registration_date(self, registration_date: datetime):
        self._registration_date = registration_date

    def get_home_address(self) -> Optional[Address]:
        return self._home_address

    def set_home_address(self, home_address: Address):
        self._home_address = home_address

    def get_shipping_address(self) -> Optional[Address]:
        return self._shipping_address

    def set_shipping_address(self, shipping_address: Address):
        self._shipping_address = shipping_address