import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_serializer
from xlin import *


class UserData(BaseModel):
    """
    UserData is a Pydantic model that represents the data structure for user information.
    It includes fields for user ID, name, email, and other relevant details.
    """

    user_id: str
    name: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

    user_profile: str = ""
    preferences: str = ""

    @field_serializer("created_at")
    def serialize_dt(self, dt: datetime.datetime, _info):
        return dt.isoformat()



class UserStore:
    """
    UserStore is responsible for managing user data.
    It provides methods to store, retrieve, and delete user information.
    """

    def __init__(self):
        self.users: dict[str, UserData] = {}

    def add_user(self, user_id: str, user_data: UserData):
        """Add a new user to the store."""
        self.users[user_id] = user_data

    def get_user(self, user_id: str) -> Optional[UserData]:
        """Retrieve user data by user ID."""
        return self.users.get(user_id)

    def delete_user(self, user_id: str):
        """Delete a user from the store."""
        if user_id in self.users:
            del self.users[user_id]

    def update_preferences(self, user_id: str, preferences: str):
        """Update user preferences."""
        if user_id in self.users:
            self.users[user_id].preferences = preferences
        else:
            raise ValueError(f"User with ID {user_id} does not exist.")

    def update_user_profile(self, user_id: str, profile: str):
        """Update user profile information."""
        if user_id in self.users:
            self.users[user_id].user_profile = profile
        else:
            raise ValueError(f"User with ID {user_id} does not exist.")

    def load_from_file(self, file_path: str):
        """Load user data from a file."""
        try:
            jsonlist = read_as_json_list(file_path)
            for user in jsonlist:
                user_data = UserData(**user)
                self.add_user(user_data.user_id, user_data)
        except FileNotFoundError:
            print(f"File {file_path} not found.")
        except Exception as e:
            print(f"Error loading user data: {e}")

    def save_to_file(self, file_path: str):
        """Save user data to a file."""
        try:
            jsonlist = [user.model_dump() for user in self.users.values()]
            save_json_list(jsonlist, file_path)
        except Exception as e:
            print(f"Error saving user data: {e}")


class MemoryManager:
    """
    MemoryManager is responsible for managing the memory of the agent.
    It provides methods to store, retrieve, and delete memory entries.
    """

    def __init__(self):
        self.memory = {}

    def store_memory(self, key: str, value: str):
        """Store a memory entry."""
        self.memory[key] = value

    def retrieve_memory(self, key: str) -> str:
        """Retrieve a memory entry."""
        return self.memory.get(key, "")

    def delete_memory(self, key: str):
        """Delete a memory entry."""
        if key in self.memory:
            del self.memory[key]
