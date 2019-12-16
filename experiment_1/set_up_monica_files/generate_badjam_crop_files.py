import csv
import os
import json
import re
import datetime

selected_agmip_sites = [5, 9, 15, 16, 17, 18, 27, 28, 29, 37, 38, 39, 40, 41, 42, 43, 44, 48, 49, 50, 52]




def main():
    for agmip_site in selected_agmip_sites:

        years = [1980, 1981, 1982, 1983]
        if agmip_site == 44:
            years = [1981, 1982, 1983, 1984]

        # create directory where simulation files should be stored
        site_dir = "sites/agmip-site-%d" % agmip_site
        if not os.path.exists(site_dir):
            os.makedirs(site_dir)



        with open('crop-template.json', 'r') as template_file:
            # read in site template
            crop_data = json.load(template_file)
            n_fert_amount = 0.0
            cultivar = "WW"

            # read in cultivar information from "agmip_crop_infos.csv" file
            crop_cultivar_file = "agmip_crop_infos.csv"
            with open(crop_cultivar_file, "r") as crop_file:
                crop_reader = csv.DictReader(crop_file, delimiter=';')
                for row in crop_reader:
                    if int(row['agmip_station']) == agmip_site:
                        print("Found agmip station and cultivar", agmip_site, row['variety'])
                        crop_data["crops"][row['cultivar']]["cropParams"]["cultivar"] = [
                            "include-from-file",
                            "monica_parameters/crops/wheat/%s" % row['variety']
                        ]
                        n_fert_amount = round(float(row['n_fert']), 2)
                        cultivar = row['cultivar']

            if agmip_site <= 30:
                # no nitrogen or water stress
                sowing_filename = "1_30/1-30_sowing_dates.csv"
                with open(sowing_filename, "r") as sowing_file:
                    crop_reader = csv.DictReader(sowing_file, delimiter=';')

                    for row in crop_reader:
                        if int(row['SiteNo']) == agmip_site:
                            sowing_date = datetime.datetime.strptime(row["sowdate"], "%d.%m.%Y", )
                            day = sowing_date.day
                            month = sowing_date.month
                            crop_rotation = []
                            for year in years:
                                worksteps = []
                                # sowing step
                                sowing_workstep = {
                                    "date": f"%d-%02d-%02d" % (year, month, day),
                                    "type": "Sowing",
                                    "crop": [
                                        "ref",
                                        "crops",
                                        cultivar
                                    ]
                                }

                                # harvest step
                                harvest_step = {
                                    "max-3d-precip-sum": 5,
                                    "harvest-time": "maturity",
                                    "max-curr-day-precip": 1,
                                    "min-%-asw": 0,
                                    "max-%-asw": 100,
                                    "latest-date": "%d-09-01" % (year + 1),
                                    "type": "AutomaticHarvest"
                                }

                                worksteps.append(sowing_workstep)
                                worksteps.append(harvest_step)
                                crop_rotation.append({"worksteps": worksteps})
                            crop_data["cropRotation"] = crop_rotation
            else:
                sowing_filename = "31_60/31-60_sowing_dates.csv"
                with open(sowing_filename, "r") as sowing_file:
                    crop_reader = csv.DictReader(sowing_file, delimiter=';')

                    for row in crop_reader:

                        if int(row['SiteNo']) == agmip_site:

                            crop_rotation = []
                            sowing_date = datetime.datetime.strptime(row["sowdate"], "%d_%b_%Y")
                            print("Sowing date:", sowing_date)
                            day = sowing_date.day
                            month = sowing_date.month

                            for year in years:
                                worksteps = []
                                harvest_year = year + 1
                                harvest_month = 9
                                if agmip_site == 44:
                                    harvest_year = year
                                    harvest_month = 11
                                # sowing step
                                sowing_workstep = {
                                    "date": f"%d-%02d-%02d" % (year, month, day),
                                    "type": "Sowing",
                                    "crop": [
                                        "ref",
                                        "crops",
                                        cultivar
                                    ]
                                }

                                # harvest step
                                harvest_step = {
                                    "max-3d-precip-sum": 5,
                                    "harvest-time": "maturity",
                                    "max-curr-day-precip": 1,
                                    "min-%-asw": 0,
                                    "max-%-asw": 100,
                                    "latest-date": f"%d-%02d-01" % (harvest_year, harvest_month),
                                    "type": "AutomaticHarvest"
                                }

                                fertilizer_step = {
                                    "date": f"%d-%02d-%02d" % (year, month, day),
                                    "amount": [
                                        n_fert_amount,
                                        "kg N"
                                    ],
                                    "partition": [
                                        "include-from-file",
                                        "monica_parameters/mineral-fertilisers/AN.json"
                                    ],
                                    "type": "MineralFertilization"
                                }

                                worksteps.append(sowing_workstep)
                                worksteps.append(harvest_step)
                                worksteps.append(fertilizer_step)

                                crop_rotation.append({"worksteps": worksteps})
                            crop_data["cropRotation"] = crop_rotation

            # write now individual crop file to the resp. agmip site directory
            output_file = site_dir + "/crop-%d.json" % agmip_site
            with open(output_file, 'w') as out_file:
                json.dump(crop_data, out_file, indent=4)


#######################################################################################################
#######################################################################################################
#######################################################################################################


# execute generate_monica_climate_files function of this script
main()
