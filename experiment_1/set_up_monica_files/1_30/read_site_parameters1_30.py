import csv
import json

with open('Loc1_30.csv', 'r') as csv_file:
    reader = csv.DictReader(csv_file, delimiter=';')

    site_parameters = {
        "Slope": 0.01,
        "SoilProfileParameters": []
    }


    for row in reader:
        clay = round(float(row['SLCL']), 2)
        silt = round(float(row['SLSI']), 2)
        sand = round(1.0 - clay - silt, 2)
        soil_bulk_density = round(float(row['slbdm']) * 1000.0, 1)
        soc = int(float(row['sloc']))

        soil_profile_parameter_list = site_parameters["SoilProfileParameters"]
        soil_profile_parameter = {
            "Clay": clay,
            "Sand": sand,
            "SoilBulkDensity": soil_bulk_density,
            "PoreVolume": round(float(row['slsat']), 3),
            "PermanentWiltingPoint": round(float(row['slll']), 3),
            "FieldCapacity": round(float(row['sldul']), 3),
            "SoilOrganicCarbon": soc,
            "pH": 8.2, # bitte
            "Thickness": [int(row['depth']), "cm"]
        }
        site_parameters["SoilProfileParameters"].append(soil_profile_parameter)

    print(json.dumps(site_parameters, indent=4))

csv_file.close()