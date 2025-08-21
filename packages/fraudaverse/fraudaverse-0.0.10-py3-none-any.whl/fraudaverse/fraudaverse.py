#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Fraudaverse data and scoring API library
# Copyright (C) 2022, 2025, by Fraudaverse Group GmbH

import json
import os
import requests
import pandas
import datetime
import dateutil
import re

"""
Available environment variables:
API_TOKEN             : an API authentication token for the UI
TLS_VERIFICATION_PATH : path to TLS cerficate authority (CA) file
TLS_CLIENT_CERT_PATH  : path to TLS client certificate file
UI_HOST               : url of the UI host, for example https://localhost
"""

_req = requests.Session()
_pipeline_id = None
_host = None
_api_key = None
SAMPLE_PATH = "/api/sample"
PERSIST_PATH = "/api/save_scoring"


def set_api_key(key: str):
    """
    Set API Key for authentication on UI
    ----------
    key : str
    """
    global _api_key
    _api_key = key


def set_cert_path(path: str):
    """
    Set TLS certificate path for HTTPS verification. Path of file can be in PEM format.
    Use "False" to disable certificate verification.
    ----------
    path : str
    """
    global _req
    _req.verify = False if path == "False" else path


def set_client_cert_path(path: str):
    """
    Set TLS client side certificate path for mTLS. Path of file can be in PEM format.
    ----------
    path : str
    """
    global _req
    _req.cert = path


def set_pipeline_id(pipeline_id_param: str):
    """Set the pipeline id as in the URL"""
    global _pipeline_id
    _pipeline_id = pipeline_id_param


def set_host(host: str):
    """Set the pipeline id as in the URL"""
    global _host
    if host:
        _host = host


def get_host():
    return _host

def convert_dates_to_days(from_iso_date: str, to_iso_date: str) -> tuple[float, float]:
    today = datetime.datetime.now()
    from_date = dateutil.parser.isoparse(from_iso_date)
    to_date = dateutil.parser.isoparse(to_iso_date)
    seconds_per_day = 60*60*24
    return (today - from_date).total_seconds() / seconds_per_day, (today - to_date).total_seconds() / seconds_per_day

def sample(
    host: str = None,
    genuine: int = -1,
    fraud: int = -1,
    from_days: float = None,
    to_days: float = None,
    from_date: str = None,
    to_date: str = None,
) -> tuple[pandas.DataFrame, pandas.Series]:
    """
    Returns a data sample for machine learning of [data, fraud_label].
    "data" and "fraud_label" have the same length of genuine + fraud.
    "data" doesn't contain the fraud label
    and "fraud_label" only contains the fraud label.
    """
    if from_date != None and to_date != None:
        from_days, to_days = convert_dates_to_days(from_date, to_date)
    data, fraud_field = sample_get_data(host, genuine, fraud, from_days, to_days)
    return sample_convert_data(data, fraud_field)


def sample_get_data(
    host: str = None,
    genuine: int = -1,
    fraud: int = -1,
    from_days: float = None,
    to_days: float = None,
    from_date: str = None,
    to_date: str = None,
) -> tuple[pandas.DataFrame, str]:
    """
    Internal function that is called by 'sample'.
    Returns tuple of pandas.DataFrame and label of fraud field
    """
    try:
        set_host(host)
        _validate_env()
        data = _query_json_request(genuine, fraud, from_days, to_days)
        data.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"Reason: {data.reason}")
        print(f"Response: {data.text}")
        print(f"HTTP error occurred: {err}")
        raise err
    except requests.exceptions.RequestException as err:
        print(f"Reason: {data.reason}")
        print(f"Response: {data.text}")
        print(f"Request error occurred: {err}")
        raise err
    
    if len(data.text) == 0:
        error = "The server response from 'sample' is empty. Cannot continue."
        print(error)
        raise Exception(error)
    try:
        data = json.loads(data.text)
    except json.JSONDecodeError as err:
        print(f"Response '{data}' doesn't contain valid json: {err}")
        raise err
    if "error" in data:
        error = data["error"]
        print(error)
        raise Exception(f"The server response from 'sample' contained following error message: {error}")
    fraud_field = data["fraud_field"]
    data = pandas.json_normalize(data["data"])
    return data, fraud_field


def sample_convert_data(
    data: pandas.DataFrame, fraud_field: str
) -> tuple[pandas.DataFrame, pandas.Series]:
    """
    Internal function that is called by 'sample'.
    Converts data so it can be processed by xgboost.
    Returns tuple of pandas.DataFrame that doesn't contain the fraud field 
    and pandas.Series that only contains fraud values
    """
    data = _convert_categories_and_timestamps(data)
    if fraud_field in data:
        data_fraud = data[fraud_field].astype("int")
        data.drop(columns=[fraud_field], inplace=True)
    else:
        if len(data) == 0:
            print(f"Queried data is empty. Cannot continue with empty data.")
            raise Exception("No data found")
        else:
            print(f"Fraud field '{fraud_field}' missing in data:")
            print(data)
            raise Exception("No fraud data found")
    return data, data_fraud


def get_categories(pd_dataframe: pandas.DataFrame):
    """Extracts all categories from pandas dataframe into single json."""
    categories = json.loads("{}")
    for frame in pd_dataframe:
        if pd_dataframe[frame].dtype == "category":
            cats = pandas.DataFrame({frame: pd_dataframe[frame].cat.categories})
            pd_dataframe[frame]
            categories[frame] = json.loads(cats.to_json())[frame]
    return categories


def persist(
    model: str,
    categories: str = "",
    host: str = None,
    model_name: str = "uploaded_by_python.json",
    comment: str = "",
):
    """Persists a model in a scoring compute referenced by a pipeline and compute id
    Parameters
    ----------
    model : str
        The model as string in xgboost json format
    categories : str
        (optional) A json string of all categories that were used during training in following format
        {"attr1": { "0": "val_1", "1": "val_2"}, "attr2": { "0": "a", "b": "c"} }
    host : str
        (optional) Host that is used
    model_name : str
        (optional) File name that should be displayed
    """
    set_host(host)
    _validate_env()

    try:
        response = _persist_model_request(model_name, comment, model, categories)
        response.raise_for_status()  # Raises an HTTPError if the status code is 4xx, 5xx
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 401:
            print("API key seems to be invalid. Please verify that the key is correct.")
        elif err.response.status_code == 404:
            print("Invalid URL. Version mismatch or host is not a fraudaverse server.")
        print(f"HTTP error occurred: {err}")
        raise
    except requests.exceptions.RequestException as err:
        print(f"Request error occurred: {err}")
        raise
    except err:
        print(f"Error occurred: {err}")
        raise

    return response.text


def _get_headers():
    return {"X-API-KEY": _api_key}

def _validate_env():
    if _host is None:
        error = "The FraudAverse UI server host must be either passed as the `host` argument or set by using `fraudaverse.set_host(...)`."
        print(error)
        raise Exception(error)
    if _api_key is None:
        error = "No UI api key found. Set the API key by using `fraudaverse.set_api_key(...)`."
        print(error)
        raise Exception(error)


def _query_json_request(genuine=10000, fraud=-1, from_days=None, to_days=None):
    day_in_seconds = 60 * 60 * 24
    from_secs = None if from_days == None else from_days * day_in_seconds
    to_secs = None if to_days == None else to_days * day_in_seconds
    return _req.get(
        get_host() + SAMPLE_PATH + f"?genuine={genuine}&fraud={fraud}&from={from_secs}&to={to_secs}",
        headers=_get_headers()
    )


def _persist_model_request(model_name, comment, model, categories):
    return _req.put(
        get_host() + PERSIST_PATH,
        headers=_get_headers(),
        json={
            "name": model_name,
            "comment": comment,
            "model": model,
            "categories": categories,
        },
    )


def _convert_categories_and_timestamps(data: pandas.DataFrame):
    try:
        if "rulesFired" in data:
            # drop rulesFired if it isn't a string
            if data[
                "rulesFired"
            ].dtype != "String" and not pandas.api.types.is_integer_dtype(
                data["rulesFired"].dtype
            ):
                data = data.drop(columns=["rulesFired"])
    except Exception as e:
        print(e)
    drop_frames = []
    # convert strings and objects to categories, convert dates to timestamps
    for frame in data:
        try:
            if data[frame].dtype == "datetime64[ns, UTC]" and re.search(
                "timestamp", frame, re.IGNORECASE
            ):
                data[frame] = data[frame].astype("uint64")
            if data[frame].dtype == "object" and re.search(
                "timestamp", frame, re.IGNORECASE
            ):
                if re.search("\\$date\\.\\$numberLong", frame):
                    data[frame.replace(".$date.$numberLong", "")] = data[frame].astype(
                        "uint64"
                    )
                    drop_frames.append(frame)
                else:
                    data[frame] = (
                        (
                            pandas.to_datetime(data[frame], utc=True)
                            - pandas.Timestamp("1970-01-01", tz=datetime.timezone.utc)
                        )
                        // pandas.Timedelta("1s")
                    ).astype("uint64")
            elif data[frame].dtype == "object":
                data[frame] = data[frame].astype("category")
            if data[frame].dtype == "String":
                data[frame] = data[frame].astype("category")
        except Exception as e:
            print(f"Warning: Removing {frame} due to conversion issue:", e)
            drop_frames.append(frame)
    data.drop(columns=drop_frames, inplace=True)
    return data


def _read_env_vars():
    auth_session = os.environ.get("API_TOKEN", False)
    if auth_session:
        set_api_key(auth_session)
    tls_verification = os.environ.get("TLS_VERIFICATION_PATH", False)
    if tls_verification:
        set_cert_path(tls_verification)
    tls_cert = os.environ.get("TLS_CLIENT_CERT_PATH", False)
    if tls_cert:
        set_client_cert_path(tls_cert)
    set_host(os.environ.get("UI_HOST", False))


_read_env_vars()
