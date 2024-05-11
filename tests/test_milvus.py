import pytest
from unittest.mock import MagicMock

from services.milvus import get_milvus_512_collection, get_milvus_87_collection, sort_entities


# # Check the name of the returned collection  // only works locally and not in github actions
# def test_get_milvus_512_collection():
#     collection = get_milvus_512_collection()
#     assert collection.name == "embeddings_512"


# def test_get_milvus_87_collection():
#     collection = get_milvus_87_collection()
#     assert collection.name == "predictions_87"


def test_sort_entities():
    # Create a list of mock hit objects
    hits = [MagicMock() for _ in range(15)]
    for i, hit in enumerate(hits):
        hit.entity.artist = f"Artist {i % 5}"  # This will create 5 unique artists

    result = sort_entities([hits])

    # Check the length of the returned list
    assert len(result) == 9

    # Check the number of unique artists in the returned list
    unique_artists = {hit["artist"] for hit in result}
    assert len(unique_artists) == min(5, len(result))

    # Check the order of the artists in the returned list
    for i in range(1, len(result)):
        assert result[i]["artist"] != result[i - 1]["artist"]