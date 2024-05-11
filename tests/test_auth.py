from unittest.mock import patch

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from routes.auth import login


@patch("routes.auth.get_user")
@patch("bcrypt.checkpw")
def test_login(mock_checkpw, mock_get_user):
    # Arrange
    mock_get_user.return_value = {"hashed_password": "hashed_password"}
    mock_checkpw.return_value = True
    data = OAuth2PasswordRequestForm(username="test@example.com", password="testpassword")

    # Act
    result = login(data)

    # Assert
    assert result["access_token"] is not None
    assert result["token_type"] == "bearer"
    mock_get_user.assert_called_once_with("test@example.com")
    mock_checkpw.assert_called_once_with("testpassword".encode("utf-8"), "hashed_password".encode("utf-8"))

