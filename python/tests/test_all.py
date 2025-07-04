import pytest
import stardust


def test_sum_as_string():
    assert stardust.sum_as_string(1, 1) == "2"
