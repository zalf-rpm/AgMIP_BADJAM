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

climate_model_names = {
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

def visualize_results():
    # directory for the output files

    output_base_dir = "monica_results/2019-12-10/"
    model_outputs = model_output_map.keys()
    bias_method_names = climate_model_names.keys()

    # bias_method_names = ["AGMERRA", "ECCC_MBCn"]

    n_stress_responses = ["NNS", "YNS"]

    for bias_method in bias_method_names:

        climate_models = climate_model_names[bias_method]
        number_of_climate_models = len(climate_models)

        for n_stress_response in n_stress_responses:

            width = 16
            height = 2 * (len(model_outputs) + 1)
            png_filename = output_base_dir + "/images/bias_method/%s_%s.png" % (bias_method, n_stress_response)
            fig = plt.figure(figsize=(width, height), dpi=180, facecolor='w', edgecolor='k')
            fig.suptitle("Bias method: %s   N stress: %s" % (bias_method, n_stress_response), fontsize=14)
            print("Visualize bias method %s for %s " % (bias_method, n_stress_response))

            for index, model_output in enumerate(model_outputs):
                ax = fig.add_subplot(len(model_outputs), 1, index + 1)

                for c_index, climate_model in enumerate(climate_models):

                    if climate_model == "":
                        input_dir = output_base_dir + "%s/%s/" % (bias_method, n_stress_response)
                    else:
                        input_dir = output_base_dir + "%s/%s/%s/" % (bias_method, climate_model, n_stress_response)

                    print("input dir", input_dir)
                    site_files = get_files_in_directory(input_dir, '')

                    x_values = range(0, len(site_files))
                    x_values = np.array(x_values)
                    x_values = np.add(x_values, (0.08 * c_index - 0.4))
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

                    ax.errorbar(x_values, y_values, yerr=error_bar, fmt='o', label=climate_model)
                    plt.xticks(range(0, len(site_files)), x_label)
                    ax.set_ylabel("%s [%s]" % (model_output, model_output_map[model_output]))
                    ax.set_xlabel("Sites")
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
    visualize_results()
