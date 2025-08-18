import uuid

from machc.base import EntityId


class UserId(EntityId):
    """
    The UserId class extends the EntityId class, providing a specialized identifier for User entities.
    It leverages the UUID-based unique identification mechanism implemented in the parent EntityId class.

    This class is designed to be a foundational component for identifying User entities within the Machc project.
    """

    def __init__(self, id=None):
        """
        Constructs a UserId using the specified UUID. If no UUID is provided, a default user_service ID can be handled
        by the superclass.

        Args:
            id (uuid.UUID, optional): The UUID for the user_service. Defaults to None.
        """
        super().__init__(id=id)

if __name__ == '__main__':
    # Create a UserId instance with a specific UUID
    user_id_with_uuid = UserId(id=uuid.uuid4())
    print(f"User ID with UUID: {user_id_with_uuid.get_id()}")

    # Create an empty UserId instance for frameworks/tools requiring default constructor
    default_user_id = UserId()
    default_user_id.set_id(uuid.uuid4())  # Assign ID later
    print(f"Default User ID assigned UUID: {default_user_id.get_id()}")