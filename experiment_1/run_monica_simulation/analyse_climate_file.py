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


############################################################################################################
############################################################################################################
############################################################################################################

def visualize_individual_climate_file():
    climate_variables = ["iso-date", "tmin", "tavg","tmax", "precip", "globrad", "wind", "relhumid"]

    # directory for the output files
    climate_file = "D:/Eigene Dateien specka/ZALF/devel/github/AgMIP_BADJAM/experiment_1/data/run_monica_simulation/climate/PIK_ISIMIP3/PIK_ISIMIP3_NOAAGFDL_39.txt"
    filename = os.path.splitext(os.path.basename(climate_file))[0]
    print("Filename", filename)


    output_base_dir = "monica_results/2019-12-10/"
    width = 12
    height = 5 * len(climate_variables) + 1
    png_filename = output_base_dir + "/images/climate_files/" + filename + ".png"
    fig = plt.figure(figsize=(width, height), dpi=180, facecolor='w', edgecolor='k')
    fig.suptitle(filename, fontsize=14)
    date_parser = pd.to_datetime

    df = pd.read_csv(open(climate_file, 'rb'), delimiter=';', header=0, na_values="NA", date_parser=date_parser, parse_dates=[0])

    for output_index, climate_variable in enumerate(climate_variables):

        # skip isodate column
        if output_index == 0:
            continue

        ax = fig.add_subplot(len(climate_variables), 1, output_index + 1)
        df.plot(kind='line', x='iso-date', y=climate_variable, ax=ax)

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
    visualize_individual_climate_file()
