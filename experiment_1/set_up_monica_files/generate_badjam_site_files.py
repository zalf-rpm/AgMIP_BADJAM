import csv
import os
import json
import re

selected_agmip_sites = [5, 9, 15, 16, 17, 18, 27, 28, 29, 37, 38, 39, 40, 41, 42, 43, 44, 48, 49, 50, 52]

col_index = {
    'depth': 1,
    'slll': 2,
    'sldul': 3,
    'slsat': 4,
    'slbdm': 6,
    'sloc': 7,
    'slph': 8,
    'SLSA': 9,
    'SLCL': 11,
    'sliwat': 12,
    'slinconc': 13,
    'sliammon': 14
}

def main():
    for agmip_site in selected_agmip_sites:

        site_dir = "sites/agmip-site-%d" % agmip_site
        if not os.path.exists(site_dir):
            os.makedirs(site_dir)

        if agmip_site <=30:
            # use just one soil profile for each of the sites from 1-30
            with open('site-template-1-30.json', 'r') as template_file:

                # read in site template
                site_data = json.load(template_file)

                # read in coordinates csv file
                with open('site_coordinates.csv', 'r') as csv_file:
                    reader = csv.DictReader(csv_file, delimiter=';')

                    for row in reader:
                        if int(row['SiteNo']) == agmip_site:
                            print("Found latitude for agmip site:", row['Lat'])
                            site_data['SiteParameters']['Latitude'] = round(float(row['Lat']), 3)
                            site_data["SiteParameters"]["HeightNN"]= [round(float(row['Elevation']), 2),"m"]
                            break


                # write now individual site file to the resp. agmip site directory
                output_file = site_dir + "/site-%d.json" % agmip_site
                with open(output_file, 'w') as out_file:
                    json.dump(site_data, out_file, indent=4)
        else:
            # use individual soil profile information for sites 31-60
            with open('site-template-30-60.json', 'r') as template_file:

                # read in site template
                site_data = json.load(template_file)

                # read in coordinates csv file
                with open('site_coordinates.csv', 'r') as csv_file:
                    reader = csv.DictReader(csv_file, delimiter=';')

                    for row in reader:
                        if int(row['SiteNo']) == agmip_site:
                            print("Found latitude for agmip site:", agmip_site, row['Lat'])
                            site_data['SiteParameters']['Latitude'] = round(float(row['Lat']), 3)
                            site_data["SiteParameters"]["HeightNN"] = [round(float(row['Elevation']), 2), "m"]
                            break

                # read in soil profile parameters
                csv_filename = "31_60/site-%d.csv" % agmip_site
                soil_profile_parameter_list = get_soil_profile_parameters(csv_filename)
                site_data['SiteParameters']["SoilProfileParameters"] = soil_profile_parameter_list

                # write now individual site file to the resp. agmip site directory
                output_file = site_dir + "/site-%d.json" % agmip_site
                with open(output_file, 'w') as out_file:
                    json.dump(site_data, out_file, indent=4)


#######################################################################################################
#######################################################################################################
#######################################################################################################

def get_soil_profile_parameters(filename):
    print("get_soil_profile_parameters:", filename)
    soil_profile_parameter_list = []

    with open(filename, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=';')

        row_index = 0
        for row in reader:
            if row_index < 7:
                # skip first 7 header rows
                row_index += 1
                continue

            clay = round(float(row[col_index['SLCL']]), 2)
            sand = round(float(row[col_index['SLSA']]), 2)
            soil_bulk_density = round(float(row[col_index['slbdm']]) * 1000.0, 1)
            soc = int(float(row[col_index['sloc']]))
            thickness = calc_thickness(row[col_index['depth']])
            fc = round(float(row[col_index['sldul']]), 3)
            soil_moist_init = round(float(row[col_index['sliwat']]), 3)
            print("FC:",fc, "\tSoilMoistInit", soil_moist_init)
            soil_moist_perc_fc = round((soil_moist_init / fc) * 100.0, 2)

            soil_profile_parameter = {
                "Clay": clay,
                "Sand": sand,
                "SoilBulkDensity": soil_bulk_density,
                "PoreVolume": round(float(row[col_index['slsat']]), 3),
                "PermanentWiltingPoint": round(float(row[col_index['slll']]), 3),
                "FieldCapacity": fc,
                "SoilOrganicCarbon": soc,
                "pH": round(float(row[col_index['slph']]), 2),
                "Thickness": [thickness, "cm"],
                "SoilAmmonium": round(float(row[col_index['sliammon']]), 2),
                "SoilNitrate": round(float(row[col_index['slinconc']]), 2),
                "SoilMoisturePercentFC": soil_moist_perc_fc
            }
            soil_profile_parameter_list.append(soil_profile_parameter)
            row_index += 1

    return soil_profile_parameter_list

#######################################################################################################
#######################################################################################################
#######################################################################################################


def calc_thickness(depth_str):

    """
    Calculates the layer thickness based on the pass string which includes information about upper and
    lower limit of the layer.
    """

    temp = re.findall(r'\d+', depth_str)
    result = list(map(int, temp))
    thickness = result[1] - result[0]

    return thickness


#######################################################################################################
#######################################################################################################
#######################################################################################################


# execute generate_monica_climate_files function of this script
main()
