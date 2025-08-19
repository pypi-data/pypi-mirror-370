import unittest
from unittest.mock import patch, MagicMock, AsyncMock, mock_open
from types import SimpleNamespace
import os

from src.back_chat.utils.functions import add_user, update_user, save_file
from src.back_chat.models import UserSchema, ApiUser


class TestUserModule(unittest.TestCase):

    @patch("src.back_chat.models.ApiUser")
    def test_add_user_new(self, mock_api_user):
        # Arrange
        user_data = {"name": "John", "postal_code": "12345", "city": "Berlin",
                     "uid": "1"}
        user_schema = UserSchema(**user_data)
        mock_api_user.get_or_none.return_value = None

        fake_user = SimpleNamespace(**user_data)
        mock_api_user.get_or_create.return_value = fake_user

        result = add_user(user_schema)

        self.assertEqual(result, "Added user 1:John to database.")
        mock_api_user.create.assert_called_once_with(**user_data)

    @patch("src.back_chat.models.ApiUser")
    def test_add_user_existing(self, mock_api_user):
        # Arrange
        user_data = {"name": "Jane", "postal_code": "54321", "city": "Madrid"}
        user_schema = UserSchema(**user_data)
        mock_api_user.get_or_none.return_value = True  # Simula existencia

        # Act
        result = add_user(user_schema)

        # Assert
        self.assertEqual(result, "The user already exists!")

    @patch("src.back_chat.models.ApiUser")
    def test_update_user(self, mock_api_user):
        # Arrange
        old_user = MagicMock()
        old_user.uid = 42

        user_update = UserSchema(name="Updated", postal_code="00000", city="Paris")

        mock_query = MagicMock()
        mock_api_user.update.return_value.where.return_value = mock_query
        mock_query.execute.return_value = None

        updated_instance = MagicMock()
        mock_api_user.get.return_value = updated_instance

        # Act
        result = update_user(old_user, user_update)

        # Assert
        mock_api_user.update.assert_called_once_with(**user_update.dict())
        mock_api_user.get.assert_called_once_with(mock_api_user.uid == old_user.uid)
        self.assertEqual(result, updated_instance)

    @patch("src.back_chat.configuration.MANAGER")
    @patch("src.back_chat.configuration.LOGGER")
    @patch("builtins.open", new_callable=mock_open)
    @patch("src.back_chat.models.os.path.join",
           side_effect=lambda *args: os.path.sep.join(args))
    def test_save_file(self, mock_join, mock_file_open, mock_logger, mock_manager):
        # Arrange
        mock_upload_file = MagicMock()
        mock_upload_file.filename = "my file.txt"
        content_chunks = [b"data1", b"data2", b""]
        mock_upload_file.read = AsyncMock(side_effect=content_chunks)

        # Act (call async function in event loop)
        import asyncio
        asyncio.run(save_file(mock_upload_file))

        # Assert
        filename_expected = os.path.join(
            "src.back_chat.configuration.SAVE_FOLDER", "my-file.txt")
        mock_file_open.assert_called_with(filename_expected, "ab")
        mock_manager.broadcast.assert_awaited_once_with("File attached: my file.txt ")


if __name__ == "__main__":
    unittest.main()
