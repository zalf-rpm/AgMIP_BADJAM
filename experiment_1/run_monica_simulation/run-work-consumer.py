#!/usr/bin/python
# -*- coding: UTF-8

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */

# Authors:
# Michael Berg-Mohnicke <michael.berg@zalf.de>
#
# Maintainers:
# Currently maintained by the authors.
#
# This file has been created at the Institute of
# Landscape Systems Analysis at the ZALF.
# Copyright (C: Leibniz Centre for Agricultural Landscape Research (ZALF)

import sys
# sys.path.insert(0,"C:\\Program Files (x86)\\MONICA")
#sys.path.insert(0, "D:\\Eigene Dateien specka\\ZALF\\devel\\github\\monica-master\\monica\\project-files\\Win32\\Release")
#sys.path.insert(0, "D:\\Eigene Dateien specka\\ZALF\devel\\github\\monica-master\\monica\\src\\python")
sys.path.append("C:\\Users\\specka\\AppData\\Local\\MONICA")
#print sys.path

import csv
import types
import os
import datetime

import zmq
import monica_io
#print zmq.pyzmq_version()

PATHS = {
    "specka": {
        "local-path-to-output-dir": "monica_results/"
    }
}



#############################################################
#############################################################
#############################################################

"""

"""
def run_consumer():
    "collect input_data from workers"

    config = {
        "user": "specka",
        "port": "7776",
        "server": "localhost"
    }
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            k,v = arg.split("=")
            if k in config:
                config[k] = v

    paths = PATHS[config["user"]]

    received_env_count = 1
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.connect("tcp://" + config["server"] + ":" + config["port"])
    socket.RCVTIMEO = 1000
    leave = False
    write_normal_output_files = False

    while not leave:

        try:
            result = socket.recv_json(encoding="latin-1")
        except:
            continue

        if result["type"] == "finish":
            print("Received finish message")
            leave = True

        elif not write_normal_output_files:


            print "Received work result 2 - ", received_env_count, " customId: ", result["customId"]
            write_output_files(result)
            received_env_count += 1

        elif write_normal_output_files:
        #else:

            #print("Received work result 1 - ", received_env_count, " customId: ", result["customId"])
            #write_output_files(result)
            print("\n")
            print ("received work result 1 - ", received_env_count, " customId: ", str(result.get("customId", "").values()))


            custom_id = result["customId"]
            nitrogen_response = custom_id["nitrogen_response"]
            # create output dir if it not exists
            output_dir = custom_id["output_dir"]
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            site_id = custom_id["site"]

            output_file = output_dir + "/site-%d_%s" % (site_id, nitrogen_response)


            print("Write output file:", output_file)
            with open(output_file, 'wb') as _:
                writer = csv.writer(_, delimiter=",")

                for data_ in result.get("data", []):
                    print("Data", data_)

                    results = data_.get("results", [])
                    orig_spec = data_.get("origSpec", "")
                    output_ids = data_.get("outputIds", [])
                    print("Results:", results)
                    if len(results) > 0:
                        writer.writerow([orig_spec.replace("\"", "")])
                        for row in monica_io.write_output_header_rows(output_ids,
                                                                      include_header_row=True,
                                                                      include_units_row=False,
                                                                      include_time_agg=False):
                            writer.writerow(row)

                        for row in monica_io.write_output(output_ids, results):
                            #print(row)
                            writer.writerow(row)

                    writer.writerow([])


            received_env_count += 1


########################################################################
########################################################################
########################################################################

"""
Analyses result object, creates a map with yearly results and then
writes them to filesystem. Output filename is passed with custom_id object.
"""
def write_output_files(result):

    custom_id = result["customId"]
    nitrogen_response = custom_id["nitrogen_response"]
    output_dir = custom_id["output_dir"]
    site_id = custom_id["site"]

    # create output dir if it not exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    #print ("Received results from %s" % custom_id["output_dir"])

    ###########################################################################################
    # restructure results into a printable form
    structured_result = []

    for output_section in result.get("data", []):

        results = output_section.get("results", [])
        output_ids = output_section.get("outputIds", [])
        
        # skip empty results, e.g. when event condition haven't been met
        if len(results) == 0:
            continue

        years_count = len(results[0])

        # initialize  result data structure
        if len(structured_result) == 0:
            for i in range(0, years_count):
                structured_result.append({})

        assert len(output_ids) == len(results)

        for kkk in range(0, years_count):
            # output blöcke aka crop,  while
            #print "kkk", kkk

            result_map = structured_result[kkk]
            for iii in range(0, len(output_ids)):


                oid = output_ids[iii]
                val = results[iii][kkk]
                #print"oid:", oid['name'], "\tval: ", val
                name = oid["name"] if len(oid["displayName"]) == 0 else oid["displayName"]
                if isinstance(val, types.ListType):
                    for val_ in val:
                        result_map[name] = val_
                else:
                    result_map[name] = val

    ###########################################################################################
    # write to csv file
    fp = None
    output_file = output_dir + "/site-%d_%s" % (site_id, nitrogen_response)
    #print("###1", output_file)
    fp = open(output_file, 'wb')

    writer = csv.writer(fp, delimiter="\t")
    writer.writerow(["site", "Year", "YLD", "SD", "ED", "HD", "FD", "MD", "BAG", "LAI", "CWU"])

    for yearly_results in structured_result:
        #print yearly_results

        row = [site_id]

        row.append(yearly_results["Year"]) if "Year" in yearly_results else row.append("NA")
        row.append(yearly_results["Yield"]) if "Yield" in yearly_results else row.append("NA")
        row.append(yearly_results["SD"]) if "SD" in yearly_results else row.append("NA")
        row.append(yearly_results["ED"]) if "ED" in yearly_results else row.append("NA")
        row.append(yearly_results["HD"]) if "HD" in yearly_results else row.append("NA")
        row.append(yearly_results["FD"]) if "FD" in yearly_results else row.append("NA")
        row.append(yearly_results["MD"]) if "MD" in yearly_results else row.append("NA")
        row.append(yearly_results["AbBiom"]) if "AbBiom" in yearly_results else row.append("NA")
        row.append(yearly_results["LAI"]) if "LAI" in yearly_results else row.append("NA")
        row.append(yearly_results["CWU"]) if "CWU" in yearly_results else row.append("NA")

        writer.writerow(row)

    # close csv writer and file
    del writer
    fp.close()



########################################################################
########################################################################
########################################################################


if __name__ == "__main__":
    run_consumer()

