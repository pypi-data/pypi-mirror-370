import pytest
from vibedecrement import vibedecrement
from dotenv import load_dotenv

load_dotenv()


def test_vibedecrement():
    assert vibedecrement(2) == 1
    assert vibedecrement(5) == 4
    assert vibedecrement(10) == 9
    assert vibedecrement(42) == 41


def test_large_numbers():
    assert vibedecrement(101) == 100
    assert vibedecrement(1000) == 999
    assert vibedecrement(12346) == 12345


def test_edge_cases():
    assert vibedecrement(1) == 0  # decrementing 1 gives 0
    assert vibedecrement(10) == 9  # decrement across digit boundary
    assert vibedecrement(100) == 99  # another digit boundary case


def test_special_cases():
    assert vibedecrement(11) == 10
    assert vibedecrement(21) == 20
    assert vibedecrement(101) == 100


def test_invalid_inputs():
    """Test that non-positive numbers raise ValueError"""
    with pytest.raises(ValueError, match="vibedecrement only accepts positive numbers"):
        vibedecrement(0)

    with pytest.raises(ValueError, match="vibedecrement only accepts positive numbers"):
        vibedecrement(-1)

    with pytest.raises(ValueError, match="vibedecrement only accepts positive numbers"):
        vibedecrement(-10)