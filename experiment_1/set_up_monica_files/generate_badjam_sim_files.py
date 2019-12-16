import csv
import os
import json
import re

selected_agmip_sites = [5, 9, 15, 16, 17, 18, 27, 28, 29, 37, 38, 39, 40, 41, 42, 43, 44, 48, 49, 50, 52]
irrigated_sites = [5, 27, 28, 29]


def generate_badjam_sim_json_files():
    for agmip_site in selected_agmip_sites:

        # create directory where simulation files should be stored
        site_dir = "sites/agmip-site-%d" % agmip_site
        if not os.path.exists(site_dir):
            os.makedirs(site_dir)

        with open('sim-template.json', 'r') as template_file:
            # read in site template
            sim_data = json.load(template_file)

            # with or without irrigation
            if agmip_site in irrigated_sites:
                sim_data["UseAutomaticIrrigation"] = True
            else:
                sim_data["UseAutomaticIrrigation"] = False

            sim_data["site.json"] = "site-%d.json" % agmip_site
            sim_data["crop.json"] = "crop-%d.json" % agmip_site

            if agmip_site <= 30:
                # no nitrogen or water stress
                sim_data["WaterDeficitResponseOn"] = False
                sim_data["NitrogenResponseOn"] = False

            else:
                # no nitrogen or water stress
                sim_data["WaterDeficitResponseOn"] = True
                sim_data["NitrogenResponseOn"] = True


            # write now individual site file to the resp. agmip site directory
            output_file = site_dir + "/sim-%d.json" % agmip_site
            with open(output_file, 'w') as out_file:
                json.dump(sim_data, out_file, indent=4)


#######################################################################################################
#######################################################################################################
#######################################################################################################


# execute generate_monica_climate_files function of this script
if __name__ == "__main__":
    generate_badjam_sim_json_files()
