#!/usr/bin/python
# -*- coding: latin1

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */

# Authors:
# Xenia Specka <xenia.specka@zalf.de>
# Michael Berg-Mohnicke <michael.berg@zalf.de>
#
# Maintainers:
# Currently maintained by the authors.
#
# This file has been created at the research platform input_data at ZALF.
# Copyright (C: Leibniz Centre for Agricultural Landscape Research (ZALF)

import imp

import json
import sys

sys.path.append("C:\\Users\\specka\\AppData\\Local\\MONICA")
import datetime
import time
import zmq
import monica_io
import pandas as pd
import csv
from io import StringIO, BytesIO
import os

#############################################################
#############################################################
#############################################################

PATHS = {
    "specka": {
        "INCLUDE_FILE_BASE_PATH": "D:/Eigene Dateien specka/ZALF/devel/github/AgMIP_BADJAM/experiment_1/run_monica_simulation/"
    }
}

#############################################################
#############################################################
#############################################################

climate_data_names = {
    "AGMERRA": [""],
    "ECCC_MBCn": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    "ECCC_MBCp": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    "ECCC_MBCr": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    "ECCC_QDM": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    "IPSL_CDFt": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    "IPSL_R2D2": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    "NCAR_KDDM": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    "PIK_ISIMIP3": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    "PIK_ISIMIP3_multi": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    "UC_EQM": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    "PIK_ISIMIP3_multi": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    "UC_EQM": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    "UC_EQMs": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    "UG_QM": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    "UP_CDFT": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    "UG_QM": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    "UP_REA": [""]

}

# with nitrogen stress activated = True
# without nitrogen stress response = False
locations = {
    5: [False],
    9: [False],
    15: [False],
    16: [False],
    17: [False],
    18: [False],
    27: [False],
    28: [False],
    29: [False],
    37: [False, True],
    38: [False, True],
    39: [False, True],
    40: [False, True],
    41: [False, True],
    42: [False, True],
    43: [False, True],
    44: [False, True],
    48: [False, True],
    49: [False, True],
    50: [False, True],
    52: [False, True]
}

start_date = datetime.date(day=1, month=1, year=1980)
end_date = datetime.date(day=31, month=12, year=1984)

daily_outputs = True


#############################################################
#############################################################
#############################################################

def run_producer():
    # simulation options
    activate_debug = True

    # directory for the output files
    output_base_dir = "monica_results/2019-12-10/"
    if not os.path.exists(output_base_dir):
        os.makedirs(output_base_dir)

    # technical initialisation
    config = {
        "user": "specka",
        "port": "6666",
        "server": "localhost"
    }

    sent_id = 0
    start_send = time.clock()
    socket = initialise_sockets(config)
    print(socket)

    # output file
    paths = PATHS[config["user"]]

    location_ids = sorted(locations.keys())
    climate_simulations = climate_data_names.keys()

    # overwrites for individual simulations
    #location_ids = [5]      # 5, 9, 15, 16, 17, 18, 27
    climate_simulations = ["IPSL_R2D2"]

    for loc_id in location_ids:
        print"############################################"
        print"LOCATION", loc_id
        print"############################################"

        for bias_method in climate_simulations:

            climate_models = climate_data_names[bias_method]
            # overwrites for individual simulations
            #climate_models = ["MPIRCA4"]

            for climate_model in climate_models:

                nitrogen_stress_responses = locations[loc_id]

                for n_stress_response in nitrogen_stress_responses:
                    n_stress_txt = "NNS"
                    if n_stress_response:
                        n_stress_txt = "YNS"

                    sim_id = "%d_%s_%s_%s" % (loc_id, bias_method, climate_model, n_stress_txt)

                    output_dir = output_base_dir + "/%s/%s/%s" % (bias_method, climate_model, n_stress_txt)
                    print("Run simulation " + str(sim_id))
                    sim_parameters = None
                    site_parameters = None
                    crop_parameters = None

                    print(os.path.dirname(__file__))

                    simulation_dir = "agmip_wheat_sites/agmip-site-%d/" % loc_id

                    with open(simulation_dir + "sim-" + str(loc_id) + ".json") as fp:
                        sim_parameters = json.load(fp)

                    with open(simulation_dir + "site-" + str(loc_id) + ".json") as fp:
                        site_parameters = json.load(fp)

                    with open(simulation_dir + "crop-" + str(loc_id) + ".json") as fp:
                        crop_parameters = json.load(fp)

                    if site_parameters is None:
                        print("ERROR: site_parameters == None")
                    if crop_parameters is None:
                        print("ERROR: crop_parameters == None")
                    if sim_parameters is None:
                        print("ERROR: sim_parameters == None")

                    #########################################################
                    # overwrite some simulation parameters
                    sim_parameters["debug?"] = True
                    sim_parameters["NitrogenResponseOn"] = n_stress_response
                    #########################################################

                    # calculation of the heading output based on Christian Kersebaums assumptions
                    tsum_bbch55 = calc_bbch55(loc_id)

                    output_map = update_output_map(sim_parameters, tsum_bbch55)
                    sim_parameters["output"] = output_map

                    # path to climate file
                    if climate_model == "":
                        if bias_method == "UP_REA":
                            climate_file = "climate/%s/%s_%02d.txt" % (bias_method, "UP_CDFT_REA", loc_id)
                        else:
                            climate_file = "climate/%s/%s_%02d.txt" % (bias_method, bias_method, loc_id)
                    else:
                        climate_file = "climate/%s/%s_%s_%02d.txt" % (
                            bias_method, bias_method, climate_model, loc_id)

                    #print("PATH TO CLIMATE:", climate_file)

                    abs_path_climate_file = os.path.abspath(climate_file)
                    #print(abs_path_climate_file)
                    sim_parameters["climate.csv"] = abs_path_climate_file

                    env_map = {
                        "crop": crop_parameters,
                        "site": site_parameters,
                        "sim": sim_parameters
                    }

                    # !IMPORTANT
                    # need to reload monica_io, otherwise some parameters like crop parameter will be internally cached
                    # causing wrong simulation results
                    imp.reload(monica_io)

                    env = monica_io.create_env_json_from_json_config(env_map)

                    # final env object with all necessary information
                    env["customId"] = {
                        "id": sim_id,
                        "bias_method": bias_method,
                        "climate_model": climate_model,
                        "nitrogen_response": n_stress_txt,
                        "output_dir": output_dir,
                        "site": loc_id
                    }

                    #with open("env.json", "w") as fp:
#                        json.dump(env, fp=fp, indent=4)

                    # sending env object to MONICA ZMQ
                    print("sent env ", sent_id, " customId: ", env["customId"])
                    socket.send_json(env)
                    sent_id += 1


    stop_send = time.clock()
    print("sending ", sent_id, " envs took ", (stop_send - start_send), " seconds")


#############################################################
#############################################################
#############################################################

def calc_bbch55(site):
    # read in cultivar information from "agmip_crop_infos.csv" file

    crop_cultivar_file = "../set_up_monica_files/agmip_crop_infos.csv"
    with open(crop_cultivar_file, "r") as crop_file:
        crop_reader = csv.DictReader(crop_file, delimiter=';')
        for row in crop_reader:
            if int(row['agmip_station']) == site:
                variety = row['variety']
                # read in cultivar information from "agmip_crop_infos.csv" file
                variety_file = "monica_parameters/crops/wheat/%s" % row['variety']
                print "variety_file", variety_file
                with open(variety_file, "r") as variety_f:
                    crop_parameter = json.load(variety_f)
                    stage2_sum = crop_parameter["StageTemperatureSum"][0][1]
                    stage3_sum = crop_parameter["StageTemperatureSum"][0][2]

                    tsum_bbch55 = (stage2_sum + stage3_sum)
                    return tsum_bbch55



#############################################################
#############################################################
#############################################################

def update_output_map(sim_parameters, bbch55):

    output_map = {

        "events": [
            #"daily", ["Date","Crop", "Stage", "DOY","AbBiom","Tmin", "Tavg", "Tmax", "Wind", "Globrad", "Relhumid"],
            "crop", [
                ["Year", "LAST"],
                ["Yield", "LAST"],
                ["AbBiom|AbBiom", "LAST"],
                ["DOY|SD", "FIRST"],
                ["DOY|MD", "LAST"],
                ["Act_ET|CWU", "SUM"]
            ],
            ["while", "Stage", "=", 2], [
                ["DOY|ED", "FIRST"]  # emergence date
            ],
            ["while", "TempSum", ">=", bbch55], [
                ["DOY|HD", "FIRST"]  # heading date
            ],
            ["while", "Stage", "=", 3], [
                ["DOY|Stage3DOY", "FIRST"]
            ],
            ["while", "Stage", "=", 5], [
                ["DOY|FD", "FIRST"],
                ["LAI|LAI", "FIRST"]
            ],
            "anthesis", [
                "DOY|AD"               # anthesis
            ],
            "maturity", [
                "DOY|MD",               # maturity,
                "AbBiom|BAG"
            ],
        ]
    }
    return output_map


#############################################################
#############################################################
#############################################################


def initialise_sockets(config):
    """ Initialises the socket based on command line parameter information"""

    context = zmq.Context()
    socket = context.socket(zmq.PUSH)

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            k, v = arg.split("=")
            if k in config:
                config[k] = v

    socket.connect("tcp://" + config["server"] + ":" + str(config["port"]))
    return socket


#############################################################
#############################################################
#############################################################


def get_monica_date_string(date):
    """ Converts a date string provide by the AgMIP Mgt File into a MONICA date string (isoformat). """

    if date == "NA":
        return "NA"

    new_date = datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")
    return new_date


#############################################################
#############################################################
#############################################################


if __name__ == "__main__":
    run_producer()
