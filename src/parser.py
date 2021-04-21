import re
from collections import deque, namedtuple

import more_itertools as miter
import pandas as pd


FieldSpec = namedtuple("FieldSpec", ["n_repeats", "type", "width"])


def extract_variable_names(full_text: list[str]) -> tuple[list[str], str, int]:
    """"""
    var_names = ["SUBJECT ID"]
    for _idx, line in enumerate(full_text):
        # Check if we've gotten to the data format spec
        if line.strip().startswith("("):
            break

        # There should be at least 2 spaces between columns & we only care about column 2
        # Leading whitespace is not significant here
        split_line = re.split(r"\s{2,}", line.strip(), maxsplit=2)
        var_names.append(split_line[1])

    format_spec = full_text[_idx].strip(" ()")
    data_start_idx = _idx + 1

    return var_names, format_spec, data_start_idx


def parse_format_spec(raw_spec: str) -> tuple[list[FieldSpec], int]:
    """"""
    chunk_size = raw_spec.count("/") + 1

    # Specs are delimited either by a comma (change in type) or a forward slash (newline)
    fields = re.split(r"[,/]", raw_spec)

    # Field specifier is assumed to be <n repeats><type><width>.<decimal width>
    # If <n repeats> isn't specified it's assumed to be 1
    # Since all data specifies 0 decimal digits we can ignore them
    spec_pattern = r"(\d*)(\w)(\d+)\.?"
    matches = [re.search(spec_pattern, field).groups() for field in fields]
    field_specs = []
    for n_repeats, field_type, field_width in matches:
        field_specs.append(
            FieldSpec(
                int(n_repeats) if n_repeats else 1,
                field_type,
                int(field_width),
            )
        )

    return field_specs, chunk_size


def parse_data(full_text: list[str]) -> pd.DataFrame:
    """"""
    var_names, format_spec, data_start_idx = extract_variable_names(full_text)
    field_specs, chunk_size = parse_format_spec(format_spec)

    parsed_rows = []
    for chunk in miter.chunked(full_text[data_start_idx:], chunk_size):
        parsed_row = []

        # Trailing whitespace is just padding to get to 80 characters for the line
        # Dump row into a deque so we can pop off the leading digits as we read
        row = deque("".join(chunk).rstrip())
        for field in field_specs:
            for _ in range(field.n_repeats):
                parsed_row.append(int("".join(row.popleft() for _ in range(field.width))))

        parsed_rows.append(parsed_row)

    parsed_df = pd.DataFrame(parsed_rows, columns=var_names).set_index("SUBJECT ID")

    return parsed_df
