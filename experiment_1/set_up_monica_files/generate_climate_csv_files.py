import datetime
import csv
import os

path_to_original_climate_files = "historical_climate_data/"
output_base_dir = "monica_climate_files/"

climate_data_names = {
    #"AGMERRA": [""],
    #"ECCC_MBCn": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    #"ECCC_MBCp": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    #"ECCC_MBCr": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    #"ECCC_QDM": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    #"IPSL_CDFt": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    "IPSL_R2D2": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"]
    #"NCAR_KDDM": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    #"PIK_ISIMIP3": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    #"PIK_ISIMIP3_multi": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    #"UC_EQM": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    #"PIK_ISIMIP3_multi": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    #"UC_EQM": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    #"UC_EQMs": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    #"UG_QM": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    #"UP_CDFT": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    #"UG_QM": ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"],
    #"UP_REA": [""]

}


#############################################################
#############################################################
#############################################################

def generate_monica_climate_files():
    locations = [5, 9, 15, 16, 17, 18, 27, 28, 29, 37, 38, 39, 40, 41, 42, 43, 44, 48, 49, 50, 52]
    climate_simulations = climate_data_names.keys()

    for loc_id in locations:

        for climate_sim in climate_simulations:
            climate_methods = climate_data_names[climate_sim]

            for climate_method in climate_methods:
                # path to climate file
                climate_dir = path_to_original_climate_files + "%s/" % climate_sim
                if climate_method == "":
                    if climate_sim == "UP_REA":
                        climate_file = "%s_%02d.txt" % ("UP_CDFT_REA", loc_id)
                    else:
                        climate_file = "%s_%02d.txt" % (climate_sim, loc_id)
                else:
                    climate_file = "%s_%s_%02d.txt" % (climate_sim, climate_method, loc_id)

                output_dir = output_base_dir + climate_sim + "/"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                output_file = output_dir + climate_file

                monica_climate_csv = read_climate(climate_dir + climate_file)
                print("Write", climate_file, "to", output_file)
                with open(output_file, "wb") as f:
                    monica_csv = csv.writer(f, delimiter=';')
                    monica_csv.writerows(monica_climate_csv)


#############################################################
#############################################################
#############################################################

def read_climate(path_to_file):
    "read climate data locally"

    # climate_csv_string = ""
    # last_in_section = False
    with open(path_to_file) as f:
        ccc = []
        reader = csv.reader(f, delimiter=' ')

        # skip 5 header rows
        for i in range(5):
            reader.next()

        csv_header = ["iso-date", "tmin", "tavg", "tmax", "precip", "globrad", "wind", "relhumid"]
        ccc.append(csv_header)
        for row in reader:
            date_string = datetime.date(day=int(row[3]), month=int(row[2]), year=int(row[1])).isoformat()
            tmin = float(row[6])
            tavg = round((float(row[6]) + float(row[5])) / 2, 2)
            tmax = float(row[5])  # tmax
            precip = float(row[7])  # precip
            globrad = round(float(row[4]) *86400 / 1000000, 3)  # globrad
            wind = float(row[8])  # wind
            relhumid = float(row[11])  # relhumid

            ccc.append([date_string, tmin, tavg, tmax, precip, globrad, wind, relhumid])

    return ccc


#############################################################
#############################################################
#############################################################


if __name__ == "__main__":
    generate_monica_climate_files()
