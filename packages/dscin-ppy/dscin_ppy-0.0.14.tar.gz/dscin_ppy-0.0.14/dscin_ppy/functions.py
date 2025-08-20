
import numpy as np
import pandas as pd

from time import time
from functools import wraps
from datetime import datetime


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print('func:%r args:[%r, %r] took: %2.4f sec' % \
          (f.__name__, args, kw, te-ts))
        return result
    return wrap


def fillna_using_dtype(df):
    column_types = df.dtypes.copy()

    for k,v in df.dtypes.items():
        if v == object:
            column_types[k] = "#"
        elif v == float or v == int:
            column_types[k] = 0
        elif v == datetime:
            column_types[k] = pd.NaT
        else:
            column_types[k] = "#"

    df.fillna(column_types, inplace=True)

    return df


def replace_df_comma_semicolon(df):

    for col in df.columns:
        try:
            if any(df[col].str.contains(',')):
                df[col] = df[col].str.replace(',', ';')
        except AttributeError:
            continue

    return df


def replace_comma_with_semicolon(x):
    if isinstance(x, str):
        return x.replace(',', ';')
    else:
        return x


def extract_datetime_columns_from_dictionary(translation_dictionary):
    """
    Function to extract from {translation_dictionary} the columns with
    datetime type and return a list of the corresponding technical names

    Args:
    - translation_dictionary: (dict)
        translation dictionary, consisting of key-value pairs
        {technical column name: [human column name (str), column data type]}

    Returns:
    - date_cols: (list[str])
        list of all technical column names with data type datetime

    Notes:
    - An error is returned if {translation_dictionary} is empty
    """

    assert len(translation_dictionary) > 0, "translation_dictionary is empty"

    date_cols = [
        key for key, val in translation_dictionary.items() if val[1] == datetime
    ]

    return date_cols


def extract_dtype_columns_from_dictionary(translation_dictionary, data_type):
    """
    Function to extract from {translation_dictionary} the columns with
    {data_type} type and return a list of the corresponding technical names

    Args:
    - translation_dictionary: (dict)
        translation dictionary, consisting of key-value pairs
        {technical column name: [human column name (str), column data type]}
    - data_type: (str)
        data type of the desired columns (for example: str, float, int,...)

    Returns:
    - data_type_cols: (list[str])
        list of all technical column names with data type {data_type}

    Notes:
    - An error is returned if {translation_dictionary} is empty
    """

    assert len(translation_dictionary) > 0, "translation_dictionary is empty"

    ### Create a list of the d_non_technical_column_names that match data_type
    data_type_cols = [
        key for key, val in translation_dictionary.items() if val[1] == data_type
    ]

    return data_type_cols


def extract_column_translations_from_dictionary(translation_dictionary):
    """
    Function to extract from {translation_dictionary} the technical names of
    columns and their corresponding human-readable name and return a dictionary

    Args:
    - translation_dictionary: (dict)
        translation dictionary, consisting of key-value pairs
        {technical column name: [human column name (str), column data type]}
    
    Returns:
    - column_translation_dictionary: (dict{str: str}])
       dictionary mapping columns' technical and human-readable names

    Notes:
    - An error is returned if {translation_dictionary} is empty
    """

    assert len(translation_dictionary) > 0, "translation_dictionary is empty"

    # Create a dictionary of technical_column_name: non_technical_column_name
    column_translation_dictionary = {
        key: val[0] for key, val in translation_dictionary.items()
    }

    return column_translation_dictionary


def convert_column_dtype_to_str(df, translation_dictionary):
    """
    Function to convert to string the columns of {df} using the
    {translation_dictionary} as a lookup reference for data types

    Args:
    - df: (pd.DataFrame)
        Pandas.DataFrame whose columns to convert to str
    - translation_dictionary: (dict)
        reference dictionary for looking up the columns with str data type

    Returns:
    - df (pd.DataFrame):
        staring Pandas.DataFrame with columns converted to str data type

    Notes:
    - An error is returned if {translation_dictionary} is empty
    """

    assert len(translation_dictionary) != 0, "translation_dictionary is empty"

    ### Extract the str columns from translation_dictionary and store in list
    str_cols = extract_dtype_columns_from_dictionary(translation_dictionary, str)
    str_cols = [col for col in str_cols if col in df.columns.tolist()]
    
    if len(str_cols) != len(set(str_cols)):
        raise ValueError("Duplicate column names found in str_cols.")

    ### Convert type
    df[str_cols] = df[str_cols].astype(str)

    return df


def convert_column_dtype_to_numeric(df, translation_dictionary, data_type):
    """
    Function to convert to numeric {data_type} the columns of {df} using 
    the {translation_dictionary} as a lookup reference for data types

    Args:
    - df: (pd.DataFrame)
        Pandas.DataFrame whose columns to convert to {data_type}
    - translation_dictionary: (dict)
        reference dictionary for looking up the columns with {data_type} data type
    - data_type: (str)
        numeric data type object to which convert the columns of {df}

    Returns:
    - df (pd.DataFrame):
        staring Pandas.DataFrame with columns converted to {data_type} data type

    Notes:
    - Empty values are replaced with 0's
    - {data_type} needs to be of type float or int
    - An error is returned if {translation_dictionary} is empty
    """

    assert data_type == float or data_type == int, "data_type must be either int or float!"
    assert len(translation_dictionary) > 0, "translation_dictionary is empty"

    ### Extract the int columns from translation_dictionary and store in list
    num_cols = extract_dtype_columns_from_dictionary(translation_dictionary, data_type)
    num_cols = [col for col in num_cols if col in df.columns.tolist()]

    ### Replace empty values in num_cols with 0
    df[num_cols] = df[num_cols].replace(r"^\s*$", np.nan, regex=True)
    df[num_cols] = df[num_cols].fillna(0)

    ### Convert type
    if data_type == float:
        df[num_cols] = df[num_cols].astype(float)
    elif data_type == int:
        df[num_cols] = df[num_cols].astype(float).astype(int)

    return df