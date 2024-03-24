import pytest
import os

# test if necessary files exist

def test_env_file():
    assert os.path.isfile('.env_example') == True

def test_gitignore_file():
    assert os.path.isfile('.gitignore') == True
   
def test_music_db_file():
    assert os.path.isfile('source/data/music.db') == True