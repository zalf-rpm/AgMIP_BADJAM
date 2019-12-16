import pandas as pd
import os
import csv
import pathlib
import re

############################################################################################################
############################################################################################################
############################################################################################################

bias_method_map = {
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

model_identifier = "DE08"

output_list = ["site", "YLD", "SD", "ED", "HD", "FD", "MD", "BAG", "LAI", "CWU"]


############################################################################################################
############################################################################################################
############################################################################################################

def generate_badjam_output_files():
    # directory for the output files

    input_base_dir = "monica_results/2019-12-10/"

    output_base_dir = "../submission/DE08_AgMIP_BADJAM_2019-12-16-vs2/"
    if not os.path.exists(output_base_dir):
        os.makedirs(output_base_dir)

    bias_method_names = bias_method_map.keys()
    # bias_method_names = ["AGMERRA"]

    n_stress_responses = ["NNS", "YNS"]

    for bias_method in bias_method_names:

        climate_models = bias_method_map[bias_method]

        for c_index, climate_model in enumerate(climate_models):

            for n_stress_response in n_stress_responses:

                years = [1981, 1982, 1983, 1984]

                if climate_model == "":
                    input_dir = input_base_dir + "%s/%s/" % (bias_method, n_stress_response)
                    csv_filename = output_base_dir + "%s_%s_%s.txt" % (model_identifier,
                                                                       bias_method,
                                                                       n_stress_response)
                else:
                    input_dir = input_base_dir + "%s/%s/%s/" % (bias_method, climate_model, n_stress_response)
                    csv_filename = output_base_dir + "%s_%s_%s_%s.txt" % (model_identifier,
                                                                          bias_method,
                                                                          climate_model,
                                                                          n_stress_response)

                site_files = get_files_in_directory(input_dir, '')

                final_output_map = {}
                for year in years:
                    year_array = []
                    for output in output_list:
                        year_array.append([])
                    final_output_map[year] = year_array

                for site_file in site_files:

                    site_id = re.findall(r'\d+', site_file)[0]
                    # print("SITE: ", site_id)
                    input_filename = input_dir + site_file

                    # read in csv file directly into a panda dataframe where the date row is parsed and used as index
                    df = pd.read_csv(input_filename, delimiter='\t', header=0, na_values="NA")

                    for year in years:
                        year_array = final_output_map[year]
                        for o_index, output in enumerate(output_list):
                            o_list = year_array[o_index]
                            if output == "site":
                                o_list.append(f"s%02d" % int(site_id))
                            elif output == "YLD" or output == "BAG":
                                yld = round(float(df.loc[df['Year'] == year][output].values[0]) / 1000.0, 2)
                                o_list.append(yld)
                            elif output == "LAI":
                                o_list.append(round(df.loc[df['Year'] == year][output].values[0], 3))
                            else:
                                o_list.append(round(df.loc[df['Year'] == year][output].values[0], 2))
                            year_array[o_index] = o_list

                        final_output_map[year] = year_array
                # print(final_output_map)

                # now write data structure to csv file
                print("Write to", csv_filename)
                with open(csv_filename, "w", newline='') as o_file:
                    csv_writer = csv.writer(o_file, delimiter='\t')

                    # header of file
                    csv_writer.writerow([model_identifier])
                    csv_writer.writerow([climate_model])
                    csv_writer.writerow([bias_method])

                    for year in years:
                        csv_writer.writerow([])
                        csv_writer.writerow([year])

                        output_array = final_output_map[year]

                        for o_list in output_array:
                            csv_writer.writerow(o_list)


############################################################################################################
############################################################################################################
############################################################################################################

def get_files_in_directory(path, ext):
    """ Returns a list with all files that are located in the directory specified by 'path'
    @:parameter path Path to the directory
    @:returns List with file names.
    """

    directory_list = os.listdir(path)

    def atoi(text):
        return int(text) if text.isdigit() else text

    def natural_keys(text):
        return [atoi(c) for c in re.split('(\d+)', text)]

    directory_list.sort(key=natural_keys)
    files = []

    for item in directory_list:
        if os.path.isfile(path + '/' + item):
            if ext is not None:
                suffix = pathlib.Path(path + '/' + item).suffix
                if ext == suffix:
                    files.append(item)
            else:
                files.append(item)

    return files


############################################################################################################
############################################################################################################
############################################################################################################

if __name__ == "__main__":
    generate_badjam_output_files()
