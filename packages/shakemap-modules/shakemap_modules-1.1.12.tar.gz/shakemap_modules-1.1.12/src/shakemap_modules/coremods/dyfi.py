# stdlib imports
import json
import os.path
from io import StringIO

# third party imports
import numpy as np
import pandas as pd

# local imports
from shakemap_modules.base.base import CoreModule
from shakemap_modules.base.cli import get_module_args
from shakemap_modules.utils.comcat import get_bytes, get_detail_json
from shakemap_modules.utils.config import get_config_paths
from shakemap_modules.utils.dataframe import dataframe_to_xml
from shakemap_modules.utils.logging import get_generic_logger

# Get rid of stupid pandas warning
pd.options.mode.chained_assignment = None

# number of seconds to search for event matching origin time
TIMEWINDOW = 60
# distance in decimal degrees to search for event matching coordinates
DEGWINDOW = 0.1
# +/- magnitude threshold to search for matching events
MAGWINDOW = 0.2

required_columns = ["station", "lat", "lon", "network"]
channel_groups = [["[a-z]{2}e", "[a-z]{2}n", "[a-z]{2}z"], ["h1", "h2", "z"], ["unk"]]
pgm_cols = ["pga", "pgv", "psa03", "psa10", "psa30"]
optional = ["location", "distance", "reference", "intensity", "source"]

# what are the DYFI columns and what do we rename them to?
DYFI_COLUMNS_REPLACE = {
    "Geocoded box": "station",
    "CDI": "intensity",
    "Latitude": "lat",
    "Longitude": "lon",
    "No. of responses": "nresp",
    "Hypocentral distance": "distance",
}

OLD_DYFI_COLUMNS_REPLACE = {
    "ZIP/Location": "station",
    "CDI": "intensity",
    "Latitude": "lat",
    "Longitude": "lon",
    "No. of responses": "nresp",
    "Epicentral distance": "distance",
}

MIN_RESPONSES = 1  # minimum number of DYFI responses per grid
STDDEV_TYPE = 2

STDDEVS_BY_NRESP = [
    [
        1,
        [
            (1.0, 0.8659),
            (2.0, 0.8099),
            (2.5, 0.7899),
            (3.0, 0.8111),
            (3.5, 0.8449),
            (4.0, 0.9016),
            (4.5, 0.9507),
            (5.0, 1.0050),
            (5.5, 1.0253),
            (6.0, 1.0694),
            (6.5, 1.0477),
            (7.0, 0.9897),
            (7.5, 0.9813),
            (8.0, 0.9061),
            (8.5, 0.7202),
            (9.0, 0.7127),
        ],
    ],
    [
        3,
        [
            (1.0, 0.6005),
            (2.0, 0.6177),
            (2.5, 0.6123),
            (3.0, 0.6110),
            (3.5, 0.6283),
            (4.0, 0.6695),
            (4.5, 0.7084),
            (5.0, 0.7871),
            (5.5, 0.8747),
            (6.0, 0.8570),
            (6.5, 0.7443),
            (7.0, 0.6244),
            (7.5, 0.5558),
            (8.0, 0.5713),
            (8.5, 0.4731),
            (9.0, 0.2561),
        ],
    ],
    [
        6,
        [
            (2.0, 0.5463),
            (2.5, 0.5379),
            (3.0, 0.5397),
            (3.5, 0.5119),
            (4.0, 0.5603),
            (4.5, 0.5827),
            (5.0, 0.7060),
            (5.5, 0.8327),
            (6.0, 0.8009),
            (6.5, 0.5516),
            (7.0, 0.4403),
            (7.5, 0.5014),
            (8.0, 0.3721),
            (8.5, 0.2610),
        ],
    ],
    [
        10,
        [
            (2.0, 0.5118),
            (2.5, 0.5229),
            (3.0, 0.4939),
            (3.5, 0.4380),
            (4.0, 0.4889),
            (4.5, 0.4917),
            (5.0, 0.5658),
            (5.5, 0.5669),
            (6.0, 0.8960),
            (6.5, 0.5921),
            (7.0, 0.7533),
            (7.5, 0.3556),
            (8.0, 0.2697),
            (8.5, 0.3418),
        ],
    ],
]


class DYFIModule(CoreModule):
    """
    dyfi -- Search ComCat for DYFI data and turn it into a ShakeMap data file.
    """

    command_name = "dyfi"

    def __init__(self, eventid, process="shakemap", logger=None):
        """
        Instantiate a DYFIModule class with an event ID.
        """
        super(DYFIModule, self).__init__(eventid, logger=logger)
        self.process = process

    def execute(self, outdir=None):
        """ """
        if self.process == "shakemap":
            _, data_path = get_config_paths()
            datadir = os.path.join(data_path, self._eventid, "current")
        else:
            datadir = outdir
        if not os.path.isdir(datadir):
            os.makedirs(datadir)

        # try to find the event by our event id
        try:
            detail_json = get_detail_json(self._eventid)
            dataframe, msg = _get_dyfi_dataframe(detail_json)
        except Exception as e:
            fmt = 'Could not retrieve DYFI data for %s - error "%s"'
            self.logger.warning(fmt % (self._eventid, str(e)))
            return

        if dataframe is None:
            self.logger.info(msg)
            return

        reference = "USGS Did You Feel It? System"
        xmlfile = os.path.join(datadir, "dyfi_dat.xml")
        dataframe_to_xml(dataframe, xmlfile, reference)
        self.logger.info("Wrote %i DYFI records to %s" % (len(dataframe), xmlfile))


def _get_dyfi_dataframe(
    detail_json, inputfile=None, min_nresp=MIN_RESPONSES, rerun_stddev=True
):
    if inputfile:
        with open(inputfile, "rb") as f:
            rawdata = f.read()
        if "json" in inputfile:
            df = _parse_geocoded_json(rawdata, min_nresp)
        else:
            df = _parse_geocoded_csv(rawdata, min_nresp)
        if df is None:
            msg = f"Could not read file {inputfile}"
    elif isinstance(detail_json, str):
        # This is a URL, send query to Comcat
        detail_json = get_detail_json(detail_json)
        df, msg = _parse_dyfi_detail(detail_json, min_nresp)
    else:
        df, msg = _parse_dyfi_detail(detail_json, min_nresp)

    if df is None:
        return None, msg

    if rerun_stddev:
        get_stddev(df)  # redo stddev calculation

    df["netid"] = "DYFI"
    df["source"] = "USGS (Did You Feel It?)"
    df.columns = df.columns.str.upper()

    return (df, "")


def _parse_dyfi_detail(detail_json, min_nresp):
    if "dyfi" not in detail_json["properties"]["products"]:
        msg = f"Detail for {detail_json['properties']['url']} has no DYFI product at this time."
        dataframe = None
        return (dataframe, msg)

    dyfi = detail_json["properties"]["products"]["dyfi"][0]

    # search the dyfi product for the 1km gridded geojson file.
    # get 1km data set, if exists
    if "dyfi_geo_1km.geojson" in dyfi["contents"]:
        url = dyfi["contents"]["dyfi_geo_1km.geojson"]["url"]
        bytes_1k = get_bytes(url)
        df_1k = _parse_geocoded_json(bytes_1k, min_nresp)
        if len(df_1k):
            return df_1k, ""
    else:
        return None, "No 1km DYFI data found."

    return None, "No 1km DYFI data found."


def _parse_geocoded_csv(bytes_data, min_nresp):
    # the dataframe we want has columns:
    # 'intensity', 'distance', 'lat', 'lon', 'station', 'nresp'
    # the cdi geo file has:
    # Geocoded box, CDI, No. of responses, Hypocentral distance,
    # Latitude, Longitude, Suspect?, City, State

    # download the text file, turn it into a dataframe

    text_geo = bytes_data.decode("utf-8")
    if "502 Proxy Error" in text_geo:
        return pd.DataFrame([])
    lines = text_geo.split("\n")
    if not len(lines):
        return pd.DataFrame([])
    columns = lines[0].split(":")[1].split(",")
    columns = [col.strip() for col in columns]

    fileio = StringIO(text_geo)
    df = pd.read_csv(fileio, skiprows=1, names=columns)
    if "ZIP/Location" in columns:
        df = df.rename(index=str, columns=OLD_DYFI_COLUMNS_REPLACE)
    else:
        df = df.rename(index=str, columns=DYFI_COLUMNS_REPLACE)
    df = df.drop(["Suspect?", "City", "State"], axis=1)
    df = df[df["nresp"] >= min_nresp]

    return df


def _parse_geocoded_json(bytes_data, min_nresp):
    text_data = bytes_data.decode("utf-8")
    try:
        jdict = json.loads(text_data)
    except Exception:
        return pd.DataFrame([])
    if len(jdict["features"]) == 0:
        return pd.DataFrame(data={})
    prop_columns = list(jdict["features"][0]["properties"].keys())
    columns = ["lat", "lon"] + prop_columns
    arrays = [[] for col in columns]
    df_dict = dict(zip(columns, arrays))
    for feature in jdict["features"]:
        for column in prop_columns:
            if column == "name":
                prop = feature["properties"][column]
                prop = prop[0 : prop.find("<br>")]
            else:
                prop = feature["properties"][column]

            df_dict[column].append(prop)
        # the geojson defines a box, so let's grab the center point
        lons = [c[0] for c in feature["geometry"]["coordinates"][0]]
        lats = [c[1] for c in feature["geometry"]["coordinates"][0]]
        clon = np.mean(lons)
        clat = np.mean(lats)
        df_dict["lat"].append(clat)
        df_dict["lon"].append(clon)

    df = pd.DataFrame(df_dict)
    df = df.rename(
        index=str, columns={"cdi": "intensity", "dist": "distance", "name": "station"}
    )
    if df is not None:
        df = df[df["nresp"] >= min_nresp]

    return df


def get_stddev(dataframe):
    if STDDEV_TYPE == 2:
        nresp = dataframe["nresp"]
        mi = dataframe["intensity"]
        stddev_function = stddev_function2(nresp, mi)
        return

    dataframe["stddev"] = stddev_function(nresp)
    return


# From SM paper, then add 0.2 sigma
def stddev_function(nresp):
    stddev = np.exp(nresp * (-1 / 24.02)) * 0.25 + 0.09 + 0.2
    stddev = np.round(stddev, 4)
    return stddev


# TODO: rewrite this loop in pandas
def stddev_function2(nresps, mis):
    results = mis * 0.0

    for i in range(len(results)):
        nresp = nresps.iloc[i]
        mi = mis.iloc[i]
        for nrespmin, sds in reversed(STDDEVS_BY_NRESP):
            if nresp >= nrespmin:
                break

        for minint, sd in reversed(sds):
            if mi >= minint:
                break

        results.iloc[i] = sd
    return results


def main():
    os.environ["CALLED_FROM_MAIN"] = "True"

    description = """
    Get Geocoded DYFI data for an event.
    """
    evid, datadir, outdir, logdir, config, _ = get_module_args(
        description, get_datadir=False, get_config=False
    )

    if logdir is None:
        logfile = None
    else:
        logfile = os.path.join(logdir, "shape.log")
    logger = get_generic_logger(logfile=logfile)

    mod = DYFIModule(evid, process="main", logger=logger)
    mod.execute(outdir=outdir)


if __name__ == "__main__":
    main()
