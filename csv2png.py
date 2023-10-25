#!/usr/bin/env python3
import sys
from typing import Any

from numpy import isnan
import pandas as pd
from dataframe_image import export as dfi_export

from sys import argv


def usage() -> None:
    """
    Usage: csv2image <in-file> [<in-file...>]
        Reads CSV data from in-file,
        puts it into a nice table and
        stores this as a png file

        -- no options.
    """
    print(usage.__doc__)


def value_to_string(value: Any, digits: int, na_str: str = "&empty;") -> str:
    """
    Convert given value to string given the datatype

    :param value: Value to convert
    :param digits: number of floating digits
                   if negative, format as decimal without thousands separator
    :param na_str: String to use for null values
    :return: string conversion of the input value
    """
    if isinstance(value, str):
        return value
    if value is None or isnan(value):
        return na_str
    if digits < 0:
        return format(value, str(-digits) + 'd')
    if digits == 0:
        return format(value, ',.0f')
    return format(value, ',.' + str(digits) + 'f')


def count_fraction_digits(value: str) -> int:
    """
    Return number of relevant fractional digits in the
    numeric string
    :param value: Input String; does not need to be a number
    :return: Fractional digit count; 0 for integers and strings
    """
    if value == 'nan':
        return 0
    if '.' in value:
        return len(value.split('.')[1].rstrip('0'))
    return 0


def get_max_fraction_digits(series: pd.Series) -> int:
    """
    Return the max amount of fractional digits used in the data series
    :param series: Column from a DataFrame
    :return: 0 for integers and strings, 0..18 for floating point
    """
    return max(series.apply(count_fraction_digits))


def is_session_column(name: str) -> bool:
    """
    Allows override for specific column names.
    While regular numbers are printed using thousands-separators,
    this is usually not so good for session-IDs oor hashes etc.
    :param name: Name of column to check
    :return: True if the column is of session-type
    """
    return name in ("SESSION_ID",)


def convert_numbers(df: pd.DataFrame) -> None:
    """
    Convert numbers in dataframe to strings, because pandas formatting is both too strict and too flexible
    :param df: DataFrame to operate on
    """
    for col in df.columns:
        digits = -18 if is_session_column(col) else get_max_fraction_digits(df[col].astype(str))
        print(col + ": " + str(digits) + " decimals")
        df[col] = df[col].apply(
            lambda x: value_to_string(x, digits)
        )


def csv_to_png(input_file: str, output_file: str) -> None:
    """
    Main conversion function: reads a CSV file and puts it into a nice html table, rendered as image
    :param input_file: Name of input CSV file; first column should contain column names
    :param output_file: Name of image output file
    """
    # Strings in CSV must not be lined with whitespace -- they are either picked up or break on quoted strings
    df: pd.DataFrame = pd.read_csv(input_file, quotechar='"', doublequote=True)

    # manually convert / format data, because the defaults are not nice
    convert_numbers(df)

    # typer complains about Styler vs.DataFrame, but it looks like export accepts the Styler
    # noinspection PyTypeChecker
    dfi_export(
        df.style.hide(axis='index'),
        output_file,
        table_conversion="html2image",
    )


if __name__ == "__main__":
    if len(argv) == 1 or argv[1] in ('-h', '--help',):
        usage()
        sys.exit(0)

    for csv_file in argv[1:]:
        csv_to_png(
            csv_file,
            csv_file.removesuffix(".csv") + ".png"
        )
