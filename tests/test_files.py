import pytest
import os


files_to_test = [
    '.env_example',
    '.gitignore',
    'core/data/music.db'
]


# Test if each file in files_to_test exists
@pytest.mark.parametrize("filepath", files_to_test)
def test_file_exists(filepath):
    assert os.path.isfile(filepath), f"File {filepath} does not exist"


# Test is .env is in the .gitignore file
def test_env_in_gitignore():
    with open('.gitignore', 'r') as f:
        assert '.env' in f.read(), ".env needs to be in the .gitignore file"