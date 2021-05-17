import datetime as dt

import pytest
from src import converters


def test_weight_converter() -> None:
    """Weight is assumed to be provided as `weight * 10`."""
    assert converters.weight(3141) == pytest.approx(314.1)


def test_age_converter() -> None:
    """Age is assumed to be provided as `age * 10`."""
    assert converters.age(314) == pytest.approx(31.4)


def test_race_converter() -> None:
    """Check a randomly selected mapping & fallback to empty string on unavialable key."""
    assert converters.race(2) == "BLACK"
    assert converters.race(314) == ""


def test_mos_converter() -> None:
    """Check a randomly selected mapping & fallback to empty string on unavialable key."""
    assert converters.mos(21) == "BAND"
    assert converters.mos(314) == ""


def test_handedness_converter() -> None:
    """Check a randomly selected mapping & fallback to empty string on unavialable key."""
    assert converters.handedness(2) == "LEFT-HANDED"
    assert converters.handedness(314) == ""


def test_birthplace_converter() -> None:
    """Check a randomly selected mapping & fallback to empty string on unavialable key."""
    assert converters.birthplace(95) == "HAWAII"
    assert converters.birthplace(314) == ""


def test_rank_converter() -> None:
    """Check a randomly selected mapping & fallback to empty string on unavialable key."""
    assert converters.rank(13) == "O3"
    assert converters.rank(314) == ""


# Provide length of service test cases as (integer test case, expected output) tuples
LOS_CASES = (
    (1, 1),
    (10, 10),
    (100, 30),
    (101, 31),
    (1000, 300),
    (1001, 301),
    (10000, 365),
    (10001, 366),
    (10100, 395),
    (10101, 396),
    (101010, 3960),
)


@pytest.mark.parametrize(("test_input", "truth_days"), LOS_CASES)
def test_length_of_service_converter(test_input: int, truth_days: int) -> None:
    """
    Length of service is assumed to be provided as `YYMMDD`.

    NOTE: Years are assumed to be 365 days
    NOTE: Months are assumed to be 30 days
    """
    assert converters.length_of_service(test_input) == truth_days


# Provide birthdate test cases as (integer test case, expected output) tuples
BIRTHDATE_CASES = (
    (-1, dt.date(2069, 4, 20)),  # fallback for invalid inputs
    (10314, dt.date(1901, 3, 14)),
    (100314, dt.date(1910, 3, 14)),
)


@pytest.mark.parametrize(("test_input", "truth_birthdate"), BIRTHDATE_CASES)
def test_birth_date_converter(test_input: int, truth_birthdate: dt.date) -> None:
    """
    Birth date is assumed to be provided as `YYMMDD`.

    All birth dates are assumed to be in the 20th century.
    """
    assert converters.birth_date(test_input) == truth_birthdate
