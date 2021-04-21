import datetime as dt

import more_itertools as miter
from src.code_mappings import BIRTHPLACE, HANDEDNESS, MOS, RACE, RANK


def weight(in_weight: int) -> float:
    """Decode weight, assumed to be provided as weight * 10."""
    return in_weight / 10


def age(in_age: int) -> float:
    """Decode age, assumed to be provided as age * 10."""
    return in_age / 10


def race(race_code: int) -> str:
    """
    Match the provided race code with its corresponding description string.

    NOTE: If no matching code is found, an empty string is provided
    """
    return RACE.get(race_code, "")


def mos(mos_code: int) -> str:
    """
    Match the provided MOS code with its corresponding description string.

    NOTE: If no matching code is found, an empty string is provided
    """
    return MOS.get(mos_code, "")


def handedness(handedness_code: int) -> str:
    """
    Match the provided handedness code with its corresponding description string.

    NOTE: If no matching code is found, an empty string is provided
    """
    return HANDEDNESS.get(handedness_code, "")


def birthplace(birthplace_code: int) -> str:
    """
    Match the provided birthplace code with its corresponding description string.

    NOTE: If no matching code is found, an empty string is provided
    """
    return BIRTHPLACE.get(birthplace_code, "")


def rank(rank_code: int) -> str:
    """
    Match the provided rank code with its corresponding description string.

    NOTE: If no matching code is found, an empty string is provided
    """
    return RANK.get(rank_code, "")


def length_of_service(coded_los: int) -> int:
    """
    Decode the provided length of service, assumed to be provided as `YYMMDD`, into days of service.

    NOTE: Years are assumed to be 365 days
    NOTE: Months are assumed to be 30 days
    """
    # Since the encoded length of service is cast to an integer, any leading zeros are lost so we
    # can pad the values to make sure we capture the correct duration
    stringified = list(f"{coded_los:06}")
    years, months, days = map(int, ("".join(chunk) for chunk in miter.chunked(stringified, 2)))

    return (years * 365) + (months * 30) + days


def birth_date(coded_birthdate: int) -> dt.date:
    """Decode the provided birth date, assumed to be provided as `YYMMDD`."""
    # Left-pad the birthdate to account for birthdates before 1910
    # Probably unlikely but it's an easy guard
    stringified = list(f"{coded_birthdate:06}")
    year, month, day = ["".join(chunk) for chunk in miter.chunked(stringified, 2)]

    try:
        # Since this is 1970, we can safely add on the 1900s suffix before casting back to int
        birth_date = dt.date(int(f"19{year}"), int(month), int(day))
    except ValueError:
        # If an invalid birthdate is found, use an obviously invalid placeholder
        birth_date = dt.date(2069, 4, 20)  # YOLO

    return birth_date
