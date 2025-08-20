# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2025 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

import json
from collections import defaultdict
from typing import Any, Dict, List, Tuple

import pandas as pd


def custom_metrics_to_dataframe(data: Dict[str, Any], sql: str) -> pd.DataFrame:
    """
    Convert the given dict into a pandas DataFrame.
    """
    # Collect the dates
    dates = [point["x"] for point in data["data"][0]["data"]]
    df = pd.DataFrame({"timestamp": pd.to_datetime(dates)})

    # For each series, add a column
    sql_set = set()
    series_data = {}
    for series in data["data"]:
        if "data" not in series:
            continue
        # FIXME: only allow one select statement, and get it from parameter
        colname = sql
        sql_set.add(colname)
        predkey = series.get("predicateKey", "predicate")
        y_values = [point["y"] for point in series["data"]]
        key = (predkey, colname)
        series_data[key] = y_values

    series_df = pd.DataFrame(series_data)
    df = pd.concat([df, series_df], axis=1)
    df.set_index("timestamp", inplace=True)
    if len(sql_set) == 1:
        column_names: List[str] = [
            str(name).replace("'", "")
            if isinstance(name, str)
            else str(name[0]).replace("'", "")
            for name in df.columns
        ]
        df.columns = column_names
    else:
        column_tuples: List[Tuple[str, str]] = [
            (str(name[0]).replace("'", ""), str(name[1]).replace("'", ""))
            for name in df.columns
        ]
        df.columns = pd.MultiIndex.from_tuples(
            column_tuples, names=["predicateKey", "columnName"]
        )
    return df


def feature_drift_to_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    rows: Dict[Any, Dict[str, Any]] = defaultdict(dict)
    for filter_dict in data["data"]:
        filter_name = filter_dict["predicateKey"]
        for xy in filter_dict["data"]:
            key = xy["x"]  # timestamp
            rows[key][filter_name] = xy["y"]
    # Unwrap
    new_rows = []
    for key in rows:
        row = {"timestamp": key}
        for filter_name in rows[key]:
            row[filter_name] = rows[key][filter_name]
        new_rows.append(row)
    df = pd.DataFrame(new_rows)
    if "timestamp" in df.columns:
        df = df.set_index("timestamp")
    return df


def feature_category_distribution_to_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    # First, collect the filter columns:
    rows: Dict[str, Dict[str, Any]] = defaultdict(dict)
    for filter_dict in data["data"]:
        for chart_data in filter_dict["chartData"]:
            for point in chart_data["points"]:
                key = json.dumps((chart_data["value"], point["x"]))
                rows[key].update({filter_dict["predicateKey"]: point["y"]})
    # Next, unwrap into rows:
    new_rows = []
    for key in rows:
        value, x = json.loads(key)
        new_row = {
            "timestamp": x,
            "value": value,
        }
        new_row.update(rows[key])
        new_rows.append(new_row)
    df = pd.DataFrame(new_rows)
    if "timestamp" in df.columns:
        df = df.set_index("timestamp")
    return df


def feature_density_to_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    rows: Dict[Any, Dict[str, Any]] = defaultdict(dict)
    for item in data["data"]:
        predicate = item["predicateKey"]
        for point in item["pdfDistributionGraphs"]["wholeTimeRangeDistribution"][
            "graphPoints"
        ]:
            key = point["x"]
            rows[key][predicate] = point["y"]
    new_rows = []
    for key in rows:
        row = {"x": key}
        for item in rows[key]:
            row[item] = rows[key][item]
        new_rows.append(row)
    df = pd.DataFrame(new_rows)
    if "x" in df.columns:
        df = df.set_index("x")
        df.sort_values(by="x", inplace=True)

    return df


def feature_percentiles_to_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    rows: Dict[Tuple[str, str], Dict[str, Any]] = defaultdict(dict)
    for item in data["data"]:
        for chart_data in item["chartData"]:
            predicate_key = item["predicateKey"]
            for point in chart_data["points"]:
                timestamp = point["x"]
                key = (timestamp, chart_data["value"])
                rows[key][predicate_key] = point["y"]
    new_rows = []
    for key in rows:
        timestamp, percentile = key
        row = {
            "timestamp": timestamp,
            "percentile": percentile,
        }
        for predicate in rows[key]:
            row[predicate] = rows[key][predicate]
        new_rows.append(row)
    df = pd.DataFrame(new_rows)
    if "timestamp" in df.columns:
        df = df.set_index("timestamp")
    return df
