from unittest.mock import patch
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from routes.auth import login
from services.auth import hash_password
from models.users import User 

@patch("routes.auth.get_user")
@patch("bcrypt.checkpw")
def test_login(mock_checkpw, mock_get_user):
    # Arrange
    mock_user = User()
    mock_user.hashed_password = hash_password("testpassword") 
    mock_get_user.return_value = mock_user
    mock_checkpw.return_value = True
    data = OAuth2PasswordRequestForm(username="test@example.com", password="testpassword")

    # Act
    result = login(data)

    # Assert
    assert result["access_token"] is not None
    assert result["token_type"] == "bearer"
    mock_get_user.assert_called_once_with("test@example.com")
    mock_checkpw.assert_called_once_with("testpassword".encode("utf-8"), mock_user.hashed_password.encode("utf-8"))