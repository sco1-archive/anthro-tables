from textwrap import dedent

import pandas as pd
import pytest
from src import parser
from src.parser import FieldSpec


# Provide (text source, resulting varnames, format spec, data start line) test case tuples
# Test case source must end with the format spec since this triggers the parser to stop
# It does not have to match the input variable names
# Data start line is 0-indexed & should point to the line after the format spec
VARIABLE_PARSING_CASES = (
    (
        dedent(
            """\
            1  WEIGHT               86750  218000  132100  5000  3000   0453592  22046226
            2  STATURE             141750  183800  163000  1500  1000   1000000   3937008
            3  SHOULDER HEIGHT     114750  155100  133500  1500  1000   1000000   3937008
            4  THIGH-THIGH BREADT   29750   47800   38300  1000   500   1000000   3937008
            5  BACK ARC, BUST       29750   55500   42000  1000  1000   1000000   3937008
            6  STAND TWO-H 38 A1   139750  345500  226500  8000  5000   0453592  22046226
             (I4,19F4.0)
            """
        ),
        [
            "SUBJECT ID",
            "WEIGHT",
            "STATURE",
            "SHOULDER HEIGHT",
            "THIGH-THIGH BREADT",
            "BACK ARC, BUST",
            "STAND TWO-H 38 A1",
        ],
        "I4,19F4.0",
        7,
    ),
)


@pytest.mark.parametrize(
    ("text_src", "truth_var_names", "truth_spec", "truth_data_start_idx"), VARIABLE_PARSING_CASES
)
def test_variable_name_extraction(
    text_src: str, truth_var_names: list[str], truth_spec: str, truth_data_start_idx: int
) -> None:
    """
    Validate correct extraction of variable names.

    The closing line of a test case source must contain a format spec, as this triggers the parser
    to stop looking for variable names; it does not have to match the shape of the test case data.
    """
    split_src = text_src.splitlines()
    # Ignore the format spec & data start index
    var_names, format_spec, data_start_idx = parser.extract_variable_names(split_src)

    assert var_names == truth_var_names
    assert format_spec == truth_spec
    assert data_start_idx == truth_data_start_idx


# Provide (format spec, truth fields, truth chunk size) test case tuples
FORMAT_SPEC_CASES = (
    # Format spec should be received without whitespace or parentheses, but there is a guard
    ("I4", [FieldSpec(1, "I", 4)], 1),
    ("19F4.0", [FieldSpec(19, "F", 4)], 1),
    ("I4,19F4.0", [FieldSpec(1, "I", 4), FieldSpec(19, "F", 4)], 1),
    ("I4,19F4.0/20F4.0", [FieldSpec(1, "I", 4), FieldSpec(19, "F", 4), FieldSpec(20, "F", 4)], 2),
    # Check parentheses/whitespace stripping
    ("(I4)", [FieldSpec(1, "I", 4)], 1),
    (" (I4)   ", [FieldSpec(1, "I", 4)], 1),
)


@pytest.mark.parametrize(("spec_src", "truth_spec", "truth_chunk_size"), FORMAT_SPEC_CASES)
def test_format_spec_parsing(  # noqa: D103
    spec_src: str, truth_spec: list[FieldSpec], truth_chunk_size: int
) -> None:
    field_specs, chunk_size = parser.parse_format_spec(spec_src)

    assert field_specs == truth_spec
    assert chunk_size == truth_chunk_size


def test_empty_format_spec_raises() -> None:  # noqa: D103
    with pytest.raises(ValueError):
        parser.parse_format_spec("")


# Provide a sample data dictionary for DataFrame creation
# Should have at least one column that will be converted & at least one that will be ignored
PARSED_DATAFRAME = pd.DataFrame(data={"WEIGHT": [3141], "SNEK": [1337]})
TRUTH_DATAFRAME = pd.DataFrame(data={"WEIGHT": [314.1], "SNEK": [1337]})


def test_inplace_converstion() -> None:
    """Test the correct application of inplace converters & ignoring of non-convert columns."""
    converted = parser.do_inplace_conversions(PARSED_DATAFRAME)
    assert converted.equals(TRUTH_DATAFRAME)


# Provide (sample data file, resulting dataframe) test case tuples
# Data file source should contain variable headers, format spec, and at least one row of data
DATA_PARSING_CASES = (
    (
        dedent(
            """\
            1  A
            2  B
            (I4,2F4.0)
            50482313 857
            """
        ),
        pd.DataFrame(data={"SUBJECT ID": [5048], "A": [2313], "B": [857]}).set_index("SUBJECT ID"),
    ),
    (
        dedent(
            """\
            1  A
            2  B
            (I4,F4.0/F4.0)
            50482313
             857
            """
        ),
        pd.DataFrame(data={"SUBJECT ID": [5048], "A": [2313], "B": [857]}).set_index("SUBJECT ID"),
    ),
)


@pytest.mark.parametrize(("full_src", "truth_df"), DATA_PARSING_CASES)
def test_data_parsing(full_src: str, truth_df: pd.DataFrame) -> None:  # noqa: D103
    full_text = full_src.splitlines()
    parsed_df = parser.parse_data(full_text)

    assert parsed_df.equals(truth_df)
