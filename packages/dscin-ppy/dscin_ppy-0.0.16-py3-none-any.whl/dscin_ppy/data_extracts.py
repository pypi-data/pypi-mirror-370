# This module contains functions to save and load data
import os
import csv
import time
import pickle
import datetime
import pandas as pd

import logging
log = logging.getLogger(__name__)


def remove_special_charachers(text,  special=" ", replace=None):
    if replace is None:
        text = text.replace(special, "")
    else:
        text = text.replace(special, replace)
    return text

def construct_path(*path):
    path = os.path.join(*path)
    path = (
        os.path.join(os.path.dirname(__file__), path)
        if not os.path.isabs(path)
        else path
    )
    return path

def write_pickle(obj, *path):
    """
    Filepath in .pkl
    """
    path = construct_path(*path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def read_pickle(*path):
    path = construct_path(*path)
    with open(path, "rb") as f:
        return pickle.load(f)

def append_csv(dataframe, path):
    os.path.isfile(path)
    path = construct_path(path)
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    if os.path.isfile(path):
        dataframe.to_csv(path, index=False, mode="a", header=False, sep=";")
    else:
        dataframe.to_csv(path, index=False, mode="a", header=True, sep=";")

def write_csv(dataframe: pd.DataFrame, *path, **kwargs):
    """
    Writes a DataFrame to disk as csv file, maintaining project standards.

    Args:
        DataFrame (pandas.DataFrame): the DataFrame to save
        path: file location
    """
    path = construct_path(*path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    dataframe.to_csv(path, index=False, **kwargs)

def read_from_table(connection, table_name, cols_list=None, sum_list=None,
                    filter_condition=None, date_cols=None, extract_csv=False,
                    path="table_extraction.csv"):
    """
    Function that extracts defined table
    If {extract_csv} is True, Extracted file saved as csv to the defined {path}

    Args:
    - connection: pyhdb.connect(host, port, user, password)
    - table_name: table name in the database
    - col_list: list of columns to query
    - sum_list: list of columns to sum from the aggregation
    - filter_condition: string containing the filtering instruction
    - date_cols: list of column date in the data
    - extract_csv: Boolean to control whether to save extraction to csv
    - path: path string where to save the extracted data to csv

    Returns:
    - df (pd.DataFrame) extracted data

    """
    try:
        if cols_list is not None:
            if sum_list is not None:
                group_list = set(cols_list) - set(sum_list)
                group_str = '","'.join(group_list)
                group_str = '"' + group_str + '"'
                cols_list = set(cols_list) - set(sum_list)
            cols_string = '","'.join(cols_list)
            cols_string = '"' + cols_string + '"'

            if sum_list is not None:
                sum_list = ['sum("' + s + '")' for s in sum_list]
                sum_list = ",".join(sum_list)
                cols_string = cols_string + "," + sum_list
        else:
            cols_string = "*"

        if filter_condition is not None and sum_list is None:
            extract_query = "SELECT {} FROM {} WHERE {}".format(
                cols_string, table_name, filter_condition
            )
        elif filter_condition is not None and sum_list is not None:
            extract_query = "SELECT {} FROM {} WHERE {} GROUP BY {}".format(
                cols_string, table_name, filter_condition, group_str
            )
        elif filter_condition is None and sum_list is not None:
            extract_query = "SELECT {} FROM {} GROUP BY {}".format(
                cols_string, table_name, group_str
            )
        else:
            extract_query = "SELECT {} FROM {}".format(
                cols_string, table_name
            )

        log.info(extract_query)
        no_of_zerorecord_check:int = 1
        while no_of_zerorecord_check != 0:
            log.info(
                str("no_of_zerorecord_check :" + str(no_of_zerorecord_check))
            )
            log.info(
                str("Extraction start at :" + str(datetime.datetime.now()))
            )
            _data = pd.DataFrame()
            data_list = []

            if date_cols is None:
                for chunk in pd.read_sql_query(extract_query, connection, chunksize=25000):
                    log.info(
                        str(
                            "Extracting Data from the table " +
                            table_name +
                            "as chunksize of 25000"
                        )
                    )
                    if extract_csv:
                        append_csv(chunk, path)
                    else:
                        data_list.append(chunk)
                    del chunk
            else:
                for chunk in pd.read_sql_query(extract_query, connection, chunksize=25000, parse_dates=date_cols):
                    log.info(
                        str(
                            "Extracting Data from the table " +
                            table_name +
                            "as chunksize of 25000"
                        )
                    )
                    if extract_csv:
                        append_csv(chunk, path)
                    else:
                        data_list.append(chunk)
                    del chunk

            if extract_csv is False:
                _data = pd.concat(data_list, ignore_index=True)

            numOfRows = len(_data.index)

            if numOfRows == 0:
                # job sleeps for 1 minutes
                log.info("Connection has been broken, wait for 10 secs")
                time.sleep(10)
            else:
                break

            no_of_zerorecord_check = no_of_zerorecord_check - 1

        log.info(
            str("Extraction end at :" + str(datetime.datetime.now()))
        )

        return _data

    except Exception as e:
        raise e

def read_csv(file_path, sep=",", decimal=".", header=0, index_col=""):
    try:
        if os.path.isfile(file_path):
            if index_col != "":
                _data = pd.read_csv(
                    file_path,
                    sep=sep,
                    decimal=decimal,
                    header=header,
                    quoting=csv.QUOTE_NONE,
                    index_col=index_col,
                    dtype="str"
                )
            else:
                _data = pd.read_csv(
                    file_path,
                    sep=sep,
                    decimal=decimal,
                    header=header,
                    quoting=csv.QUOTE_NONE,
                    dtype="str"
                )
            return _data
        else:
            raise Exception
    except Exception:
        raise

def read_excel(file_path, sheet_name=0, skiprows=None):
    try:
        if os.path.isfile(file_path):
            _data = pd.read_excel(
                file_path, sheet_name=sheet_name, skiprows=skiprows
            )
            return _data
        else:
            raise Exception
    except Exception:
        raise

def write_excel(dataframe: pd.DataFrame, *path, **kwargs):
    """
    Writes a DataFrame to disk as excel file, maintaining project standards.

    Args:
        DataFrame (pandas.DataFrame): the DataFrame to save
        path: file location
    """
    path = construct_path(*path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    dataframe.to_excel(path, index=False, **kwargs)
