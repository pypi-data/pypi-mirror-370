import pytest
from vibeincrement import vibeincrement
from dotenv import load_dotenv

load_dotenv()


def test_vibeincrement():
    assert vibeincrement(1) == 2
    assert vibeincrement(5) == 6
    assert vibeincrement(10) == 11
    assert vibeincrement(42) == 43


def test_large_numbers():
    assert vibeincrement(100) == 101
    assert vibeincrement(999) == 1000
    assert vibeincrement(12345) == 12346


def test_edge_cases():
    assert vibeincrement(1) == 2  # smallest positive number
    assert vibeincrement(9) == 10  # increment across digit boundary


def test_invalid_inputs():
    """Test that non-positive numbers raise ValueError"""
    with pytest.raises(ValueError, match="vibeincrement only accepts positive numbers"):
        vibeincrement(0)

    with pytest.raises(ValueError, match="vibeincrement only accepts positive numbers"):
        vibeincrement(-1)

    with pytest.raises(ValueError, match="vibeincrement only accepts positive numbers"):
        vibeincrement(-10)