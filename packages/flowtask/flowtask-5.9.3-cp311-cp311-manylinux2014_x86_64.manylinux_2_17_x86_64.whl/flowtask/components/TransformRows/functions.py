"""
Functions.

Tree of TransformRows functions.

"""
import base64
from enum import Enum
from typing import Dict, List, Optional
import re
import requests
import numpy as np
from numba import njit
from datetime import datetime
import pytz
from zoneinfo import ZoneInfo
from dateutil import parser
import pandas
from pydantic import BaseModel
from datamodel.parsers.json import json_encoder
from ...conf import BARCODELOOKUP_API_KEY
from ...utils.executor import getFunction


def apply_function(
    df: pandas.DataFrame,
    field: str,
    fname: str,
    column: Optional[str] = None,
    **kwargs
) -> pandas.DataFrame:
    """
    Apply any scalar function to a column in the DataFrame.

    Parameters:
    - df: pandas DataFrame
    - field: The column where the result will be stored.
    - fname: The name of the function to apply.
    - column: The column to which the function is applied (if None, apply to `field` column).
    - **kwargs: Additional arguments to pass to the function.
    """

    # Retrieve the scalar function using getFunc
    try:
        func = getFunction(fname)
    except Exception:
        raise

    # If a different column is specified, apply the function to it,
    # but save result in `field`
    try:
        if column is not None:
            df[field] = df[column].apply(lambda x: func(x, **kwargs))
        else:
            if field not in df.columns:
                # column doesn't exist
                df[field] = None
            # Apply the function to the field itself
            df[field] = df[field].apply(lambda x: func(x, **kwargs))
    except Exception as err:
        print(
            f"Error in apply_function for field {field}:", err
        )
    return df


def get_product(row, field, columns):
    """
    Retrieves product information from the Barcode Lookup API based on a barcode.

    :param row: The DataFrame row containing the barcode.
    :param field: The name of the field containing the barcode.
    :param columns: The list of columns to extract from the API response.
    :return: The DataFrame row with the product information.
    """

    barcode = row[field]
    url = f'https://api.barcodelookup.com/v3/products?barcode={barcode}&key={BARCODELOOKUP_API_KEY}'
    response = requests.get(url)
    result = response.json()['products'][0]
    for col in columns:
        try:
            row[col] = result[col]
        except KeyError:
            row[col] = None
    return row


def upc_to_product(
    df: pandas.DataFrame,
    field: str,
    columns: list = ['barcode_formats', 'mpn', 'asin', 'title', 'category', 'model', 'brand']
) -> pandas.DataFrame:
    """
    Converts UPC codes in a DataFrame to product information using the Barcode Lookup API.

    :param df: The DataFrame containing the UPC codes.
    :param field: The name of the field containing the UPC codes.
    :param columns: The list of columns to extract from the API response.
    :return: The DataFrame with the product information.
    """
    try:
        df = df.apply(lambda x: get_product(x, field, columns), axis=1)
        return df
    except Exception as err:
        print(f"Error on upc_to_product {field}:", err)
        return df

def day_of_week(
    df: pandas.DataFrame,
    field: str,
    column: str,
    locale: str = 'en_US.utf8'
) -> pandas.DataFrame:
    """
    Extracts the day of the week from a date column.

    :param df: The DataFrame containing the date column.
    :param field: The name of the field to store the day of the week.
    :param column: The name of the date column.
    :return: The DataFrame with the day of the week.
    """
    try:
        df[field] = df[column].dt.day_name(locale=locale)
        return df
    except Exception as err:
        print(f"Error on day_of_week {field}:", err)
        return df

def duration(
    df: pandas.DataFrame,
    field: str,
    columns: List[str],
    unit: str = 's'
) -> pandas.DataFrame:
    """
    Converts a duration column to a specified unit.

    :param df: The DataFrame containing the duration column.
    :param field: The name of the field to store the converted duration.
    :param column: The name of the duration column.
    :param unit: The unit to convert the duration to.
    :return: The DataFrame with the converted duration.
    """
    try:
        if unit == 's':
            _unit = 1.0
        if unit == 'm':
            _unit = 60.0
        elif unit == 'h':
            _unit = 3600.0
        elif unit == 'd':
            _unit = 86400.0
        # Calculate duration in minutes as float
        df[field] = (
            (df[columns[1]] - df[columns[0]]).dt.total_seconds() / _unit
        )
        return df
    except Exception as err:
        print(f"Error on duration {field}:", err)
        return df


def get_moment(
    df: pandas.DataFrame,
    field: str,
    column: str,
    moments: List[tuple] = None,
) -> pandas.DataFrame:
    """
    df: pandas DataFrame
    column: name of the column to compare (e.g. "updated_hour")
    ranges: list of tuples [(label, (start, end)), ...]
            e.g. [("night",(0,7)), ("morning",(7,10)), ...]
    returns: a Series of labels corresponding to each row
    """
    if not moments:
        moments = [
            ("night", (0, 7)),   # >= 0 and < 7
            ("morning", (7, 10)),  # >= 7 and < 10
            ("afternoon", (10, 16)),  # >= 10 and < 16
            ("evening", (16, 20)),  # >= 16 and < 20
            ("night", (20, 24)),  # >= 20 and < 24 (or use float("inf") for open-ended)
        ]
    conditions = [
        (df[column] >= start) & (df[column] < end)
        for _, (start, end) in moments
    ]
    df[field] = np.select(conditions, [label for label, _ in moments], default=None)
    return df


def fully_geoloc(
    df: pandas.DataFrame,
    field: str,
    columns: List[tuple],
    inverse: bool = False
) -> pandas.DataFrame:
    """
    Adds a boolean column (named `field`) to `df` that is True when,
    for each tuple in `columns`, all the involved columns are neither NaN nor empty.

    Parameters:
        df (pd.DataFrame): The DataFrame.
        field (str): The name of the output column.
        columns (list of tuple of str): List of tuples, where each tuple
            contains column names that must be valid (non-null and non-empty).
            Example: [("start_lat", "start_long"), ("end_lat", "end_log")]

    Returns:
        pd.DataFrame: The original DataFrame with the new `field` column.
    """
    # Start with an initial mask that's True for all rows.
    mask = pandas.Series(True, index=df.index)

    # Loop over each tuple of columns, then each column in the tuple.
    for col_group in columns:
        for col in col_group:
            if inverse:
                mask &= df[col].isna() | (df[col] == "")
            else:
                mask &= df[col].notna() & (df[col] != "")

    df[field] = mask
    return df


def any_tuple_valid(
    df: pandas.DataFrame,
    field: str,
    columns: List[tuple]
) -> pandas.DataFrame:
    """
    Adds a boolean column (named `field`) to `df` that is True when
    any tuple in `columns` has all of its columns neither NaN nor empty.

    Parameters:
        df (pd.DataFrame): The DataFrame.
        field (str): The name of the output column.
        columns (list of tuple of str): List of tuples, where each tuple
            contains column names that must be checked.
            Example: [("start_lat", "start_long"), ("end_lat", "end_log")]

    Returns:
        pd.DataFrame: The original DataFrame with the new `field` column.
    """
    # Start with an initial mask that's False for all rows
    result = pandas.Series(False, index=df.index)

    # Loop over each tuple of columns
    for col_group in columns:
        # For each group, assume all columns are valid initially
        group_all_valid = pandas.Series(True, index=df.index)

        # Check that all columns in this group are non-null and non-empty
        for col in col_group:
            group_all_valid &= df[col].notna() & (df[col] != "")

        # If all columns in this group are valid, update the result
        result |= group_all_valid

    df[field] = result
    return df


@njit
def haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    unit: str = 'km'
) -> float:
    """Distance between two points on Earth in kilometers."""
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = np.radians(lat1), np.radians(lon1), np.radians(lat2), np.radians(lon2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    # Select radius based on unit
    if unit == 'km':
        r = 6371.0  # Radius of earth in kilometers
    elif unit == 'm':
        r = 6371000.0  # Radius of earth in meters
    elif unit == 'mi':
        r = 3956.0  # Radius of earth in miles
    else:
        # Numba doesn't support raising exceptions, so default to km
        r = 6371.0

    return c * r

def calculate_distance(
    df: pandas.DataFrame,
    field: str,
    columns: List[tuple],
    unit: str = 'km',
    chunk_size: int = 1000
) -> pandas.DataFrame:
    """
    Add a distance column to a dataframe.

    Args:
        df: pandas DataFrame with columns 'latitude', 'longitude', 'store_lat', 'store_lng'
        columns: list of tuples with column names for coordinates
               - First tuple: [latitude1, longitude1]
               - Second tuple: [latitude2, longitude2]
        unit: unit of distance ('km' for kilometers, 'm' for meters, 'mi' for miles)
        chunk_size: number of rows to process at once for large datasets

    Returns:
        df with additional 'distance_km' column
    """
    result = df.copy()
    result[field] = np.nan
    # Unpack column names
    (lat1_col, lon1_col), (lat2_col, lon2_col) = columns
    try:
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i + chunk_size]
            # Convert to standard NumPy arrays before passing to haversine_distance
            lat1_values = chunk[lat1_col].to_numpy(dtype=np.float64)
            lon1_values = chunk[lon1_col].to_numpy(dtype=np.float64)
            lat2_values = chunk[lat2_col].to_numpy(dtype=np.float64)
            lon2_values = chunk[lon2_col].to_numpy(dtype=np.float64)
            result.loc[chunk.index, field] = haversine_distance(
                lat1_values,
                lon1_values,
                lat2_values,
                lon2_values,
                unit=unit
            )
    except Exception as err:
        print(f"Error on calculate_distance {field}:", err)
    return result


def drop_timezone(
    df: pandas.DataFrame,
    field: str,
    column: Optional[str] = None
) -> pandas.DataFrame:
    """
    Drop the timezone information from a datetime column.

    Args:
        df: pandas DataFrame with a datetime column
        field: name of the datetime column

    Returns:
        df with timezone-free datetime column
    """
    try:
        if column is None:
            column = field

        series = df[column]
        if pandas.api.types.is_datetime64tz_dtype(series):
            # This is a regular tz-aware pandas Series
            df[field] = series.dt.tz_localize(None)
            return df

        elif series.dtype == 'object':
            # Object-dtype: apply tz-localize(None) to each element
            def remove_tz(x):
                if isinstance(x, (pandas.Timestamp, datetime)) and x.tzinfo is not None:
                    return x.replace(tzinfo=None)
                return x  # leave as-is (could be NaT, None, or already naive)

            df[field] = series.apply(remove_tz).astype('datetime64[ns]')
            return df

        else:
            # already naive or not datetime
            df[field] = series
            return df
    except Exception as err:
        print(f"Error on drop_timezone {field}:", err)
    return df

def convert_timezone(
    df: pandas.DataFrame,
    field: str,
    *,
    column: str | None = None,
    from_tz: str = "UTC",
    to_tz: str | None = None,
    tz_column: str | None = None,
    default_timezone: str = "UTC",
) -> pandas.DataFrame:
    """
    Convert `field` to a target time‑zone.

    Parameters
    ----------
    df        : DataFrame
    field     : name of an existing datetime column
    column    : name of the output column (defaults to `field`)
    from_tz   : timezone used to localise *naive* timestamps
    to_tz     : target timezone (ignored if `tz_column` is given)
    tz_column : optional column that contains a timezone per row
    default_tz: fallback when a row's `tz_column` is null/NaN

    Returns:
        df with converted datetime column
    """
    if column is None:
        column = field

    try:
        # --- 1. make a working copy of current column
        out = df[column].copy()
        out = pandas.to_datetime(out, errors="coerce")  # force datetime dtype

        # --- 2. give tz‑naive stamps a timezone --------------------------------
        if out.dt.tz is None:
            out = out.dt.tz_localize(from_tz, ambiguous="infer", nonexistent="raise")

        # --- 3. convert ---------------------------------------------------------
        if tz_column is None:
            # same tz for every row
            target = to_tz or default_timezone
            out = out.dt.tz_convert(target)
        else:
            # using the timezone declared on column:
            timezones = (
                df[tz_column]
                .fillna(default_timezone)
                .astype("string")
            )

            # First, convert all timestamps to UTC to have a common base
            utc_times = out.dt.tz_convert('UTC')

            # Create a list to store the converted datetimes
            converted_times = []

            # Apply timezone conversion row by row
            for idx in df.index:
                try:
                    tz_name = timezones.loc[idx]
                    # Convert the UTC time to the target timezone
                    converted_dt = utc_times.loc[idx].tz_convert(ZoneInfo(tz_name))
                    converted_times.append(converted_dt)
                except Exception as e:
                    # Handle invalid timezones gracefully
                    converted_dt = utc_times.loc[idx].tz_convert(ZoneInfo(default_timezone))
                    converted_times.append(converted_dt)

            # Create a new Series with the converted values
            out = pandas.Series(converted_times, index=df.index)

        df[field] = out
    except Exception as err:
        print(f"Error on convert_timezone {field}:", err)

    return df


def add_timestamp_to_time(df: pandas.DataFrame, field: str, date: str, time: str):
    """
    Takes a pandas DataFrame and combines the values from a date column and a time column
    to create a new timestamp column.

    :param df: pandas DataFrame to be modified.
    :param field: Name of the new column to store the combined timestamp.
    :param date: Name of the column in the df DataFrame containing date values.
    :param time: Name of the column in the df DataFrame containing time values.
    :return: Modified pandas DataFrame with the combined timestamp stored in a new column.
    """
    try:
        df[field] = pandas.to_datetime(df[date].astype(str) + " " + df[time].astype(str))
    except Exception as e:
        print(f"Error adding timestamp to time: {str(e)}")
        return df
    return df

def _convert_string_to_vector(vector_string):
    """
    Converts a string representation of a list into an actual list.

    :param vector_string: The string representation of the list.
    :return: The converted list.
    """
    try:
        # Extract the numbers from the string representation
        numbers = re.findall(r'-?\d+\.\d+', vector_string)
        # Convert the extracted strings to float values
        float_values = [float(num) for num in numbers]
        # Return as numpy array
        return np.array(float_values, dtype=np.float32)
    except Exception as err:
        print(
            f"Error converting string to vector: {err}"
        )
        return vector_string

def string_to_vector(df: pandas.DataFrame, field: str) -> pandas.DataFrame:
    """
    Converts a string representation of a list into an actual list.

    :param df: The DataFrame containing the string representation.
    :param field: The name of the field to convert.
    :return: The DataFrame with the converted field.
    """
    try:
        df[field] = df[field].apply(_convert_string_to_vector)
        return df
    except Exception as err:
        print(f"Error on vector_string_to_array {field}:", err)
        return df

def extract_from_dictionary(
    df: pandas.DataFrame,
    field: str,
    column: str,
    key: str,
    conditions: dict = None,
    as_timestamp: bool = False
) -> pandas.DataFrame:
    """
    Extracts a value from a JSON column in the DataFrame.

    :param df: The DataFrame containing the JSON column.
    :param field: The name of the field to store the extracted value.
    :param column: The name of the JSON column.
    :param key: The key to extract from the JSON object.
    :param conditions: Optional dictionary of conditions to filter rows before extraction.
    :param as_timestamp: If True, converts the extracted value to a timestamp.
    :return: The DataFrame with the extracted value.
    """
    def extract_from_dict(row, key, conditions=None, as_timestamp=False):
        items = row if isinstance(row, list) else []
        if not row:
            return None
        # Apply filtering
        if conditions:
            items = [
                item for item in items
                if all(item.get(k) == v for k, v in conditions.items())
            ]
        if not items:
            return None
        # Take last item if multiple
        value = items[-1].get(key)
        if as_timestamp and value:
            try:
                return pandas.to_datetime(value)
            except Exception:
                return None
        return value
    try:
        df[field] = df[column].apply(
            extract_from_dict, args=(key, conditions, as_timestamp)
        )
        return df
    except Exception as err:
        print(f"Error on extract_from_json {field}:", err)
        return df

def extract_from_object(
    df: pandas.DataFrame,
    field: str,
    column: str,
    key: str,
    as_string: bool = False,
    as_timestamp: bool = False
) -> pandas.DataFrame:
    """
    Extracts a value from an object column in the DataFrame.

    :param df: The DataFrame containing the object column.
    :param field: The name of the field to store the extracted value.
    :param column: The name of the object column.
    :param key: The key to extract from the object.
    :param as_string: If True, converts the extracted value to a string.
    :param as_timestamp: If True, converts the extracted value to a timestamp.
    :return: The DataFrame with the extracted value.
    """
    try:
        def _getter(obj):
            # 1) turn a BaseModel into a dict
            if isinstance(obj, BaseModel):
                obj = obj.model_dump()  # or .dict() on older Pydantic

            # 2) if it's not a dict now, we can't extract
            if not isinstance(obj, dict):
                return None

            # 3) pull the raw value
            val = obj.get(key)

            # 4) if it's an Enum, unwrap it
            if isinstance(val, Enum):
                val = val.value

            # 5) optional casts
            if val is not None:
                if as_string:
                    try:
                        return val if isinstance(val, str) else json_encoder(val)
                    except Exception:
                        return str(val)
                elif isinstance(val, (int, float)):
                    return val
                elif as_timestamp:
                    try:
                        val = pandas.to_datetime(val)
                    except Exception:
                        return None

            return val

        # create the column if it doesn't exist
        if field not in df.columns:
            df[field] = None

        # apply our getter
        df[field] = df[column].apply(_getter)
        if as_string:
            df[field] = df[field].astype("string")
        elif as_timestamp:
            df[field] = pandas.to_datetime(df[field], errors='coerce')
        return df
    except Exception as err:
        print(f"Error on extract_from_object {field}:", err)
        return df


def bytesio_to_base64(
    df: pandas.DataFrame,
    field: str,
    column: str,
    as_string: bool = False,
    as_image: bool = True,
    image_mime: str = 'image/png'
) -> pandas.DataFrame:
    """
    Converts bytes in a DataFrame column to a Base64 encoded string.

    :param df: The DataFrame containing the bytes column.
    :param field: The name of the field to store the Base64 encoded string.
    :param column: The name of the bytes column.
    :param as_string: If True, converts the Base64 bytes to a string.
    :return: The DataFrame with the Base64 encoded string.
    """
    def to_base64(x, mime: str = 'image/png'):
        """
        Converts BytesIO to Base64 encoded string.
        """
        return f"data:{mime};base64,{base64.b64encode(x.getvalue()).decode('ascii')}"

    try:
        if as_string:
            df[field] = df[column].apply(lambda x: x.decode('utf-8') if as_string else x)
        elif as_image:
            # Convert bytes to Base64 encoded string
            df[field] = df[column].apply(lambda x: to_base64(x, mime=image_mime))
        return df
    except Exception as err:
        print(f"Error on bytes_to_base64 {field}:", err)
        return df


def create_attachment_column(
    df: pandas.DataFrame,
    field: str,
    columns: List[str],
    colnames: Optional[Dict[str, str]] = None

) -> pandas.DataFrame:
    """
    Create a column with a list of attachments from one or more path/URL columns.

    Args:
        df: Input DataFrame.
        field: Name of the new column to store the list of attachments.
        columns: Column names to convert. You can pass either the exact column
              (e.g., "pdf_path_m0") or the base name (e.g., "pdf_path").
        colnames: Optional list of names for the attachments. If not provided,
                  the column names will be used as names.

    Returns:
        The same DataFrame with `field` added.
    """
    def _humanize(col: str, colname: dict) -> str:
        """
        Turn 'podcast_path' -> 'Podcast', 'pdf_path' -> 'PDF', etc.
        """
        if colname and col in colname:
            return colname[col]
        base = re.sub(r'(?:_)?path$', '', col, flags=re.IGNORECASE)  # drop trailing 'path'
        base = base.replace('_', ' ').strip()
        title = base.title()

        # Acronym fixes
        fixes = {
            "Pdf": "PDF",
            "Url": "URL",
            "Id": "ID",
            "Mp3": "MP3",
            "Csv": "CSV",
            "Html": "HTML",
            "Json": "JSON"
        }
        return fixes.get(title, title)

    def _row_to_attachments(row: pandas.Series) -> list[dict]:
        out = []
        for c in columns:
            if c not in row:
                continue
            val = row[c]
            if pandas.isna(val) or (isinstance(val, str) and not val.strip()):
                continue
            out.append({"name": _humanize(c, colnames), "url": str(val)})
        return out

    df[field] = df.apply(_row_to_attachments, axis=1)
    return df


def path_to_url(
    df: pandas.DataFrame,
    field: str,
    column: str = None,
    base_path: str = 'files/',
    base_url: str = "https://example.com/files/"
) -> pandas.DataFrame:
    """
    Converts a file path in a DataFrame column to a URL.
    Replaces the base path with the base URL.

    :param df: The DataFrame containing the file path column.
    :param field: The name of the field to store the URL.
    :param column: The name of the file path column (defaults to `field`).
    :param base_path: The base path to replace in the file path.
    :param base_url: The base URL to use for the conversion.

    :return: The DataFrame with the URL in the specified field.
    """
    if column is None:
        column = field

    try:
        def convert_path_to_url(path):
            if not isinstance(path, str):
                return None
            # Ensure the path starts with the base path
            if path.startswith(base_path):
                return base_url + path[len(base_path):]
            return base_url + path

        df[field] = df[column].apply(convert_path_to_url)
    except Exception as err:
        print(f"Error on path_to_url {field}:", err)
        return df
    return df
