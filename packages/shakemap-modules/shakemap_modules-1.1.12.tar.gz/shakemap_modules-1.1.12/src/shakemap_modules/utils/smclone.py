# stdlib imports
import json
import logging
import os
import pathlib
import re
from datetime import datetime, timezone
from io import StringIO
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

# third party imports
import importlib_resources
import numpy as np
import pandas as pd
import requests
from configobj import ConfigObj
from esi_shakelib.station import StationList
from esi_utils_rupture.factory import rupture_from_dict_and_origin, text_to_json
from esi_utils_rupture.origin import Origin, write_event_file
from shakemap_modules.coremods.dyfi import _get_dyfi_dataframe
from shakemap_modules.coremods.sm_select import SelectModule
from shakemap_modules.utils.comcat import get_bytes
from shakemap_modules.utils.dataframe import dataframe_to_xml
from shakemap_modules.utils.utils import get_network_name

EVENT_URL_TEMPLATE = (
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/{eventid}.geojson"
)
EVENT_SCENARIO_TEMPLATE = (
    "https://earthquake.usgs.gov/fdsnws/scenario/1"
    "/query?eventid={eventid}&format=geojson"
)
DEG2SEC = 3600.0  # seconds per kilometer
BRACKETS_REGEX = r"[\[\]]"

CATALOGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/catalogs"
DEFAULT_MIN_RESP = 3


DEFAULT_SOURCE_PREFERENCES = ["atlas", "us"]


class ShakeClone:
    def __init__(
        self,
        eventid,
        event_path,
        source=None,
        is_online_scenario=False,
        event_dict=None,
    ):
        os.environ["CALLED_FROM_MAIN"] = "True"
        self.source = source

        self.eventid = eventid
        self.event_path = pathlib.Path(event_path)
        if not self.event_path.is_dir():
            self.event_path.mkdir(parents=True)

        self.shakemap = None
        if event_dict is None:
            if not is_online_scenario:
                url = EVENT_URL_TEMPLATE.format(eventid=eventid)
                product = "shakemap"
            else:
                url = EVENT_SCENARIO_TEMPLATE.format(eventid=eventid)
                product = "shakemap-scenario"
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception(f"Failed to get data for {eventid}")
            self.event_json = response.json()

            if product in self.event_json["properties"]["products"]:
                shakemaps = self.event_json["properties"]["products"][product]
                sources = [shakemap["source"] for shakemap in shakemaps]
                idx = 0
                if self.source is not None:
                    if self.source in sources:
                        idx = sources.index(self.source)
                    else:
                        raise KeyError(
                            f"Source {self.source} not in list of available ShakeMap sources: {sources}"
                        )
                else:
                    for prefsource in DEFAULT_SOURCE_PREFERENCES:
                        if prefsource in sources:
                            idx = sources.index(prefsource)
                            break

                self.shakemap = shakemaps[idx]
        self.event_dict = event_dict
        if self.event_dict is None:
            self.event_dict = self.get_event_dict(is_online_scenario=is_online_scenario)

        self.origin = Origin(self.event_dict)

    def clone(
        self,
        module_file=None,
        get_model=True,
        skip_bounds=False,
        get_dyfi=True,
        get_instrumented=True,
        get_macroseismic=True,
        get_rupture=True,
        preserve_version_history=False,
    ):
        edict = self.event_dict.copy()
        edict["time"] = datetime.fromisoformat(edict["time"])
        result = write_event_file(edict, self.event_path / "event.xml")
        assert result is None
        messages = []
        """Grab all requested data and write to event path."""
        model_filename = None
        if get_model:
            if module_file is None:
                module_file = (
                    importlib_resources.files("shakemap_modules")
                    / "data"
                    / "modules.conf"
                )
            select_file = (
                importlib_resources.files("shakemap_modules") / "data" / "select.conf"
            )
            model, messages = self.get_model_conf(
                module_file, select_file, skip_bounds=skip_bounds
            )
            if model is not None:
                model.filename = self.event_path / "model.conf"
                if len(messages):
                    model.filename = self.event_path / "model.conf.incomplete"
                model.write()
                model_filename = model.filename
        if get_dyfi or get_instrumented or get_macroseismic:
            macroseismic_json, instrumented_json, dyfi_json = self.get_data_dicts(
                dyfi=get_dyfi,
                macroseismic=get_macroseismic,
                instrumented=get_instrumented,
            )
            for jsonstr, data_type in zip(
                [macroseismic_json, instrumented_json, dyfi_json],
                ["macroseismic", "instrumented", "dyfi"],
            ):
                if jsonstr is not None:
                    write_data_json(jsonstr, self.event_path, data_type)
        # retrieve the shakemap version history
        if preserve_version_history:
            versiondict = self.get_history_dict()
            if len(versiondict):
                jsonfile = self.event_path / "history.json"
                with open(jsonfile, "wt") as f:
                    json.dump(versiondict, f)
        if get_rupture:
            try:
                rupture_obj = self.get_rupture_object()
                if rupture_obj is not None:
                    rupture_file = self.event_path / "rupture.json"
                    rupture_obj.writeGeoJson(rupture_file)
            except Exception as e:
                print("Unable to retrieve rupture file, error follows:")
                print(e)

        return (messages, model_filename)

    def get_rupture_object(self):
        rupture = None
        if self.shakemap is None:
            return rupture
        """Retrieve rupture file from ShakeMap, return as Rupture object."""
        rupture_key = "download/rupture.json"
        if rupture_key in self.shakemap["contents"]:
            rupture_url = self.shakemap["contents"][rupture_key]["url"]
            response = requests.get(rupture_url)
            rupture_json = response.json()
            if "reference" not in rupture_json["metadata"]:
                rupture_json["metadata"]["reference"] = ""
            rupture = rupture_from_dict_and_origin(rupture_json, self.origin)
        else:
            for key in self.shakemap["contents"]:
                if "fault.txt" in key:
                    rupture_url = self.shakemap["contents"][key]["url"]
                    response = requests.get(rupture_url)
                    rupture_text = response.text

                    rupture_io = StringIO(rupture_text)
                    try:
                        rupture_dict = text_to_json(rupture_io, new_format=True)
                        rupture = rupture_from_dict_and_origin(
                            rupture_dict, self.origin
                        )
                    except Exception as ve:
                        try:
                            rupture_io.seek(0)
                            rupture_dict = text_to_json(rupture_io, new_format=False)
                            rupture = rupture_from_dict_and_origin(
                                rupture_dict, self.origin
                            )
                            has_coordinates = len(
                                rupture_dict["features"][0]["geometry"]["coordinates"][
                                    0
                                ]
                            )
                            if not has_coordinates:
                                raise Exception("No coordinates found.")
                        except Exception as e:
                            raise Exception(
                                (
                                    f"Could not parse fault file {key} from "
                                    f"{rupture_url}, error: '{e}'"
                                )
                            )

                    break

        return rupture

    def get_model_conf(self, module_file, select_file, skip_bounds=False):
        module_conf = ConfigObj(str(module_file))
        select_conf = ConfigObj(str(select_file))
        if self.shakemap is None:
            logging.info(
                (
                    "No existing ShakeMap detected. Run the `select` module to "
                    "create an up-to-date model.conf file."
                )
            )
            return (None, [])

        info_url = self.shakemap["contents"]["download/info.json"]["url"]
        info_json = get_bytes(info_url)
        info_json = info_json.decode("utf-8")
        jsondict = json.loads(info_json)

        messages = []

        # assume we're not going to support migration anymore
        # so if we see that "multigmpe" is missing, this indicates
        # a ShakeMap 3.5 run. In this case, just run select and return
        # the results of that.
        if "multigmpe" not in jsondict:
            logging.info(
                (
                    "INFO: ShakeMap 3.5 detected. Run the `select` module to "
                    "create an up-to-date model.conf file."
                )
            )

            return (None, messages)

        model = ConfigObj(indent_type="  ")

        model["modeling"] = {"bias": {}}
        misc_dict = jsondict["processing"]["miscellaneous"]
        bias_max_mag = float(misc_dict["bias_max_mag"])
        max_range = float(misc_dict["bias_max_range"])
        if bias_max_mag > 0 and max_range > 0:
            model["modeling"]["bias"]["do_bias"] = True
            model["modeling"]["bias"]["max_range"] = max_range
            model["modeling"]["bias"]["max_mag"] = bias_max_mag
        else:
            model["modeling"]["bias"]["do_bias"] = False

        # get the outlier information
        model["data"] = {"outlier": {}}
        max_deviation = float(misc_dict["outlier_deviation_level"])
        outlier_max_mag = float(misc_dict["outlier_max_mag"])
        if outlier_max_mag > 0 and max_deviation > 0:
            model["data"]["outlier"]["do_outlier"] = True
            model["data"]["outlier"]["max_deviation"] = max_deviation
            model["data"]["outlier"]["max_mag"] = outlier_max_mag
        else:
            model["data"]["outlier"]["do_outlier"] = False

        # get a dictionary of model description strings and model keys
        # info.json stores the model description strings, although for
        # gmice and ipes, the model description strings and keys are
        # the same thing.
        model_dicts = get_model_dicts(module_conf)

        # set the gmice in model.conf
        gmm_dict = jsondict["processing"]["ground_motion_modules"]
        if "mi2pgm" in gmm_dict:
            mod_name = "mi2pgm"
        else:
            mod_name = "gmice"

        gmice = gmm_dict[mod_name]["module"]
        if gmice not in model_dicts["gmice_modules"]:
            messages.append(f"WARNING: No GMICE module found for {gmice}.")
            insert_gmice = f"<{gmice}>"
        else:
            insert_gmice = model_dicts["gmice_modules"][gmice]
        model["modeling"]["gmice"] = insert_gmice

        old_gmpe = jsondict["multigmpe"]["PGV"]  # all the metrics are the same
        gmpe_name = old_gmpe["name"]
        gmpe_list = old_gmpe["gmpes"][0]["gmpes"]
        tgmpe_list = [re.sub(r"\[|\]", "", gmpe) for gmpe in gmpe_list]
        # sometimes, gmpes have a second line with region, removing that for now
        gmpe_list = []
        for tgmpe in tgmpe_list:
            nindex = tgmpe.find("\n")
            if nindex > -1:
                gmpe = tgmpe[0:nindex]
            else:
                gmpe = tgmpe
            if gmpe not in model_dicts["gmpe_modules"]:
                messages.append(f"WARNING: No GMPE module found for {gmpe}.")
                insert_gmpe = f"<{gmpe}>"
            else:
                insert_gmpe = model_dicts["gmpe_modules"][gmpe]
            gmpe_list.append(insert_gmpe)
        weights = old_gmpe["gmpes"][0]["weights"]
        gmpe_set = {
            "gmpes": gmpe_list,
            "weights": weights,
            "weights_large_dist": None,
            "dist_cutoff": np.nan,
            "site_gmpes": None,
            "weights_site_gmpes": None,
        }
        model["gmpe_sets"] = {gmpe_name: gmpe_set}
        model["modeling"]["gmpe"] = gmpe_name
        ipe = gmm_dict["ipe"]["module"]
        if ipe not in model_dicts["ipe_modules"]:
            messages.append(f"WARNING: No IPE module found for {ipe}.")
            insert_ipe = f"<{ipe}>"
        else:
            insert_ipe = model_dicts["ipe_modules"][gmm_dict["ipe"]["module"]]
        model["modeling"]["ipe"] = insert_ipe
        ccf = gmm_dict["ccf"]["module"]
        if ccf not in model_dicts["ccf_modules"]:
            messages.append(f"WARNING: No CCF module found for {ccf}.")
            insert_ccf = f"<{ccf}>"
        else:
            insert_ccf = model_dicts["ccf_modules"][gmm_dict["ccf"]["module"]]
        model["modeling"]["ccf"] = insert_ccf

        # work on map extent/resolution data
        if not skip_bounds:
            model["interp"] = {"prediction_location": {}}
            map_dict = jsondict["output"]["map_information"]
            yres_deg = float(map_dict["grid_spacing"]["latitude"])
            yres_sec = int(round(yres_deg * DEG2SEC))
            model["interp"]["prediction_location"]["xres"] = f"{yres_sec:d}c"
            model["interp"]["prediction_location"]["yres"] = f"{yres_sec:d}c"

            model["extent"] = {"bounds": {}}
            xmin = map_dict["min"]["longitude"]
            xmax = map_dict["max"]["longitude"]
            ymin = map_dict["min"]["latitude"]
            ymax = map_dict["max"]["latitude"]
            model["extent"]["bounds"]["extent"] = [xmin, ymin, xmax, ymax]

        return (model, messages)

    def get_event_dict(self, is_online_scenario=False):
        # get basic event information from an origin contributed by input
        # source
        edict = None
        eventid = self.event_json["id"]
        lon, lat, depth = self.event_json["geometry"]["coordinates"]
        if depth is None:
            logging.warning(
                f"Depth for event {eventid} is not set! Setting it to 10 km."
            )
            depth = 10
        ttime = datetime.fromtimestamp(
            self.event_json["properties"]["time"] / 1000, tz=timezone.utc
        ).replace(tzinfo=None)
        time = ttime.isoformat()
        if self.source is not None:
            try:
                edict = {
                    "id": eventid,
                    "netid": self.source,
                    "network": get_network_name(self.source),
                    "lat": lat,
                    "lon": lon,
                    "depth": round(depth, 1),
                    "mag": round(self.event_json["properties"]["mag"], 1),
                    "time": time,
                    "locstring": self.event_json["properties"]["place"],
                    "event_type": "ACTUAL",
                }
            except ValueError:
                print(f"No origin for event {self.source}.")
        else:  # no source specified, use self.event_json object
            if is_online_scenario is True:
                netname = self.event_json["properties"]["net"]
                etype = "SCENARIO"
            else:
                netname = get_network_name(self.event_json["properties"]["net"])
                etype = "ACTUAL"
            edict = {
                "id": eventid,
                "netid": self.event_json["properties"]["net"],
                "network": netname,
                "lat": lat,
                "lon": lon,
                "depth": depth,
                "mag": self.event_json["properties"]["mag"],
                "time": time,
                "locstring": self.event_json["properties"]["place"],
                "event_type": etype,
            }
        if edict["locstring"] is None:
            edict["locstring"] = ""

        return edict

    def get_moment_xml(self):
        pass

    def get_source_xml(self):
        pass

    def get_history_dict(self):
        versiondict = {}
        if self.shakemap is not None:
            infourl = self.shakemap["contents"]["download/info.json"]["url"]
            jdict = json.loads(get_bytes(infourl).decode("utf8"))
            versiondict = jdict["processing"]["shakemap_versions"]["map_data_history"]
        return versiondict

    def get_data_dicts(
        self,
        dyfi=True,
        macroseismic=True,
        instrumented=True,
        min_resp=DEFAULT_MIN_RESP,
    ):
        macroseismic_json = None
        instrumented_json = None
        dyfi_json = None
        if self.shakemap is None:
            return (macroseismic_json, instrumented_json, dyfi_json)
        got_data_file = False
        # reg = re.compile(r'^x')                    # Compile the regex
        # test = list(filter(reg.search, test))
        xml_regex = re.compile("stationlist.xml")
        json_regex = re.compile("stationlist.json")
        xml_match = list(
            filter(xml_regex.search, list(self.shakemap["contents"].keys()))
        )
        json_match = list(
            filter(json_regex.search, list(self.shakemap["contents"].keys()))
        )
        key = None
        # prefer json over xml
        if len(xml_match):
            key = xml_match[0]
            data_file = self.event_path / f"{self.eventid}_dat.xml"
            validate_fxn = validate_xml
        if len(json_match):
            key = json_match[0]
            data_file = self.event_path / f"{self.eventid}_dat.json"
            validate_fxn = validate_json
        if key is None:
            print("No station data found. Continuing.")
        else:
            url = self.shakemap["contents"][key]["url"]
            inbytes = get_bytes(url)
            outbytes = remove_unicode(inbytes)
            with open(data_file, "wb") as f:
                f.write(outbytes)
            got_data_file = True
            if not validate_fxn(data_file):
                data_file.unlink()
                got_data_file = False

        if got_data_file:
            if instrumented:
                instrumented_json = get_instrumented(data_file)
            if macroseismic:
                macroseismic_json = get_macroseismic(data_file)
            data_file.unlink()
        xmlfile = None
        if dyfi:
            dataframe, msg = _get_dyfi_dataframe(
                self.event_json, min_nresp=1, rerun_stddev=True
            )

            reference = "USGS Did You Feel It? System"
            xmlfile = self.event_path / "dyfi_dat.xml"

            if dataframe is not None:
                dataframe_to_xml(dataframe, xmlfile, reference)
                dyfi_list = StationList.loadFromFiles(
                    [str(xmlfile)], min_nresp=min_resp
                )
                dyfi_json = dyfi_list.getGeoJson()
                del dyfi_list
                xmlfile.unlink()

        return (macroseismic_json, instrumented_json, dyfi_json)


def validate_json(jsonfile):
    try:
        with open(jsonfile, "rt") as fh:
            _ = json.load(fh)
        return True
    except Exception:
        return False


def validate_xml(xmlfile):
    parser = make_parser()
    parser.setContentHandler(ContentHandler())
    try:
        parser.parse(xmlfile)
        return True
    except Exception:
        return False
    return False


def get_instrumented(data_file):
    instrumented = StationList.loadFromFiles([str(data_file)])
    db = instrumented.db
    cursor = instrumented.cursor
    cursor.execute("SELECT count(*) FROM station")
    nrows = cursor.fetchone()[0]
    # sys.stderr.write('Original data set had %i total stations.\n' % nrows)
    query1 = "SELECT id FROM station WHERE instrumented != 1"
    cursor.execute(query1)
    srows = cursor.fetchall()
    for srow in srows:
        sid = srow[0]
        query2 = f"DELETE FROM amp WHERE station_id='{sid}'"
        cursor.execute(query2)
        db.commit()
        query3 = f"DELETE FROM station WHERE id='{sid}'"
        cursor.execute(query3)
        db.commit()

    cursor.execute("SELECT count(*) FROM station")
    nrows = cursor.fetchone()[0]
    instrumented_json = None
    if nrows:
        instrumented_json = instrumented.getGeoJson()
    return instrumented_json


def write_data_json(jsonstr, event_dir, data_type):
    data_file = event_dir / f"{data_type}_dat.json"
    with open(data_file, "wt") as f:
        json.dump(jsonstr, f)
    return data_file


def get_macroseismic(data_file):
    # load the file, nuke any data that is not macroseismic
    macroseismic = StationList.loadFromFiles([str(data_file)])
    db = macroseismic.db
    cursor = macroseismic.cursor
    cursor.execute("SELECT count(*) FROM station")
    nrows = cursor.fetchone()[0]
    # sys.stderr.write('Original data set had %i total stations.\n' % nrows)
    # first remove instruments
    query1 = "SELECT id FROM station WHERE instrumented == 1"
    cursor.execute(query1)
    srows = cursor.fetchall()
    for srow in srows:
        sid = srow[0]
        query2 = f"DELETE FROM amp WHERE station_id='{sid}'"
        cursor.execute(query2)
        db.commit()
        query3 = f"DELETE FROM station WHERE id='{sid}'"
        cursor.execute(query3)
        db.commit()
    # next, remove DYFI
    query4 = "SELECT id FROM station WHERE network in ('DYFI', 'CIIM')"
    cursor.execute(query4)
    srows = cursor.fetchall()
    for srow in srows:
        sid = srow[0]
        query5 = f"DELETE FROM amp WHERE station_id='{sid}'"
        cursor.execute(query5)
        db.commit()
        query6 = f"DELETE FROM station WHERE id='{sid}'"
        cursor.execute(query6)
        db.commit()
    cursor.execute("SELECT count(*) FROM station")
    nrows = cursor.fetchone()[0]
    jsonstr = None
    if nrows:
        jsonstr = macroseismic.getGeoJson()
    return jsonstr


def get_model_dicts(module_conf):
    # info.json stores the models for gmpe, gmice, ipe, and ccf as the
    # "values" of those models from modules.conf. For example, the
    # ccf modules in modules.conf are specified as:
    # [ccf_modules]
    #     LB13 = LothBaker2013, esi_shakelib.correlation.loth_baker_2013
    #
    # we're defining here that "LB13" is the "key", and "LothBaker2013"
    # is the "value". Confusingly, the IPEs and GMICE use the same string
    # for both "key" and "value" in this context:
    # [ipe_modules]
    #     VirtualIPE = VirtualIPE, esi_shakelib.virtualipe
    #     Allen12IPE = AllenEtAl2012, openquake.hazardlib.gsim.allen_2012_ipe
    #
    # we'll need to build a dictionary mapping where these "values" are the keys
    # and the "keys" become the values.
    top_keys = ["gmpe_modules", "ipe_modules", "gmice_modules", "ccf_modules"]
    models_dict = {}
    for top_key in top_keys:
        model_dict = {}
        for model_key, model_value in module_conf[top_key].items():
            key = model_value[0]
            value = model_key
            model_dict[key] = value
        models_dict[top_key] = model_dict
    return models_dict


def remove_unicode(inbytes):
    darray = np.frombuffer(inbytes, dtype=np.uint8).copy()
    darray[darray >= 127] = 32
    return darray.tobytes()
