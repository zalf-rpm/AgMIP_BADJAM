import sys
import pandas as pd
import numpy as np
import os
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pathlib
import re

############################################################################################################
############################################################################################################
############################################################################################################

bias_method_names = ["ECCC_MBCn", "ECCC_MBCp", "ECCC_MBCr", "ECCC_QDM",
                     "IPSL_CDFt", "IPSL_R2D2", "NCAR_KDDM", "PIK_ISIMIP3", "UC_EQM", "PIK_ISIMIP3_multi", "UC_EQM", "UC_EQMs",
                     "UG_QM", "UP_CDFT", "UG_QM"]

climate_model_names = ["CSIRO", "ICHEC", "IPSL", "MPICCLM", "MPIRCA4", "MPIREMO09", "NCCNor", "NOAAGFDL"]

n_stress_responses = ["NNS", "YNS"]

model_output_map = {
    "YLD": "t ha-1",
    "FD": "DOY",
    "MD": "DOY",
    "LAI": "",
    "CWU": "mm"
}  # YLD	SD	ED	HD	FD	MD	BAG	LAI	CWU


############################################################################################################
############################################################################################################
############################################################################################################

def visualize_results_by_climate_method():
    # directory for the output files

    output_base_dir = "monica_results/2019-12-10/"
    model_outputs = model_output_map.keys()

    for climate_model in climate_model_names:

        for n_stress_response in n_stress_responses:

            width = 16
            height = 2 * len(model_outputs) + 1
            png_filename = output_base_dir + "/images/climate_model/%s_%s.png" % (climate_model, n_stress_response)
            fig = plt.figure(figsize=(width, height), dpi=180, facecolor='w', edgecolor='k')
            fig.suptitle("Climate model: %s   N stress: %s" % (climate_model, n_stress_response), fontsize=14)
            print("Visualize climate model %s for %s " % (climate_model, n_stress_response))

            for index, model_output in enumerate(model_outputs):
                ax = fig.add_subplot(len(model_outputs), 1, index + 1)

                for b_index, bias_method in enumerate(bias_method_names):

                    input_dir = output_base_dir + "%s/%s/%s/" % (bias_method, climate_model, n_stress_response)

                    print("input dir", input_dir)
                    site_files = get_files_in_directory(input_dir, '')

                    x_values = range(0, len(site_files))
                    x_values = np.array(x_values)
                    x_values = np.add(x_values, (0.08 * b_index)-0.5)
                    y_values = []
                    error_bar = []
                    x_label = []
                    for site_file in site_files:
                        site_id = re.findall(r'\d+', site_file)[0]
                        x_label.append(str(site_id))
                        input_filename = input_dir + site_file

                        # read in csv file directly into a panda dataframe where the date row is parsed and used as index
                        df = pd.read_csv(open(input_filename, 'rb'), delimiter='\t', header=0, na_values="NA")
                        agg_df = df.agg(['mean', 'std'])
                        mean = agg_df[model_output]['mean']
                        std = agg_df[model_output]['std']

                        # convert from k ha-1 into t ha-1
                        if model_output == "YLD":
                            mean = mean / 1000.0
                            std = std / 1000.0

                        y_values.append(mean)
                        error_bar.append(std)

                    ax.errorbar(x_values, y_values, yerr=error_bar, fmt='o', label=bias_method)
                    plt.xticks(range(0, len(site_files)), x_label)
                    ax.set_ylabel("%s [%s]" % (model_output, model_output_map[model_output]))
                    # ax.legend(loc='lower right')
                if index == 0:
                    ax.legend(bbox_to_anchor=(1.02, 1), borderaxespad=0, fancybox=True, shadow=True, ncol=1)

            plt.savefig(png_filename)
            plt.close(fig)


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
    visualize_results_by_climate_method()
