import pytest
import os

# Test if each file exists
@pytest.mark.parametrize("filepath", [
    '.env_example',
    '.gitignore',
    'source/data/music.db'
])
def test_file_exists(filepath):
    assert os.path.isfile(filepath), f"File {filepath} does not exist"