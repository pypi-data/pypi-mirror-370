#!/usr/bin/env python

# stdlib imports
import json
import pathlib
import re
import sqlite3
import sys
from collections import OrderedDict

# third party imports
import pandas as pd
from esi_shakelib.station import TABLES, StationList

IMTS = ["PGV", "PGA", "SA"]


def points_to_station(dataframe, connection):
    fdsn_file = (
        pathlib.Path(__file__).parent / ".." / "data" / "fdsn_networks.json"
    )
    with open(fdsn_file, "rt") as f:
        networks_jdict = json.load(f)
    networks = {
        network["fdsn_code"]: network["name"]
        for network in networks_jdict["networks"]
    }
    stationlist = StationList(connection)
    stationlist._createTables()

    # first get all columns that match an IMT
    matched = []
    keep_cols = ["id", "lat", "lon"]
    for column in dataframe.columns:
        if column in keep_cols:
            continue
        tmpcol = column.split("_")[0]
        colstart = re.sub(r"\([^)]*\)", "", tmpcol)
        if (
            colstart in IMTS
            and "predictions" not in column
            and "std" not in column
        ):
            matched.append(column)
    filtered_dataframe = dataframe[keep_cols + matched]
    imtlist = list(set([m.split("_")[0] for m in matched]))
    imt_dataframe = pd.DataFrame({"imt_type": imtlist})

    # insert those imt types into the imt table and then get them back with id column
    nrows = imt_dataframe.to_sql(
        "imt", connection, index=False, if_exists="append"
    )
    imt_table = pd.read_sql("SELECT id, imt_type FROM imt", connection)

    # now insert all of the station data we have
    station_dataframe = pd.DataFrame(
        data=None, columns=TABLES["station"].keys()
    )
    # id column here is a text primary key, not assigned int
    station_dataframe["id"] = filtered_dataframe["id"]
    result = station_dataframe["id"].str.split(".", expand=True)
    netcodes = result[0]
    station_dataframe["code"] = result[1]
    station_dataframe["name"] = filtered_dataframe["id"]
    station_dataframe["lat"] = filtered_dataframe["lat"]
    station_dataframe["lon"] = filtered_dataframe["lon"]
    station_dataframe["network"] = netcodes
    station_dataframe["instrumented"] = 1  # ??
    sources = []
    for network in netcodes:
        if network not in networks:
            sources.append(f"unknown network {network}")
            continue
        sources.append(networks[network])
    station_dataframe["source"] = sources
    # remove duplicate stations
    station_dataframe.drop_duplicates(subset=["id"], inplace=True)
    nrows = station_dataframe.to_sql(
        "station", connection, index=False, if_exists="append"
    )
    station_table = pd.read_sql("SELECT * FROM station", connection)

    # now make a series of rows for each station row
    amp_frames = []
    for imt in imtlist:
        imt_cols = list(
            filtered_dataframe.columns[
                filtered_dataframe.columns.str.startswith(imt)
            ]
        )
        new_cols = ["id"] + imt_cols
        tmpdf = filtered_dataframe.loc[:, new_cols]
        mapper = {
            "id": "station_id",
            f"{imt}_mean": "amp",
        }
        tmpdf.rename(mapper, axis="columns", inplace=True)
        tmpdf["imt_id"] = imt_table.loc[imt_table["imt_type"] == imt].iloc[0][
            "id"
        ]
        tmpdf["stddev"] = 0.0
        tmpdf["original_channel"] = "H1"
        tmpdf["orientation"] = "H"
        tmpdf["nresp"] = 0
        tmpdf["flag"] = 0
        amp_frames.append(tmpdf)
    amp_dataframe = pd.concat(amp_frames)
    amp_dataframe.to_sql("amp", connection, index=False, if_exists="append")
    amp_table = pd.read_sql("SELECT * FROM amp", connection)
    return stationlist


if __name__ == "__main__":
    pointsfile = pathlib.Path(sys.argv[1])
    dataframe = pd.read_csv(pointsfile)
    connection = sqlite3.connect(":memory:")
    points_to_station(dataframe, connection)
