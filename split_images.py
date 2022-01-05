from multiprocessing import Process
from pprint import pprint
import time
import spectral.io.envi as envi
from spectral import settings
settings.envi_support_nonlowercase_params = True
import numpy as np
import json
import os
import re


"""


Set split data file path and dont mess with the rest... unless it does not work.


"""
split_data_file_path = "..."
"""


+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
=================================================================================
*********************************************************o***********************
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



"""

verify_paths = True
timestr = time.strftime("%Y%m%d-%H%M%S")

def avg_plot(plot):
    hb = 250    # HEIGHT BUFFER
    wb = 50     # WIDTH BUFFER
    buffered_plot = plot[hb:-hb,wb:-wb, :]
    avg_plot_ = np.average(np.reshape(buffered_plot, (-1, 224) ), axis=0)
    return avg_plot_

def split_file(imageObj, file_type):

    if file_type == "spec":
        full_bands = np.arange(0,224, 1)
        hdr = envi.open(imageObj["out_spectral"]["existing_path"])
        out_path = imageObj["out_spectral"]
    else:
        full_bands = np.arange(0,235, 1)
        hdr = envi.open(imageObj["out_combined"]["existing_path"])
        out_path = imageObj["out_combined"]

    plot = hdr.read_bands(full_bands)

    left_img = plot[:, :imageObj['x_split'], :]
    right_img = plot[:, imageObj['x_split']:, :]


    if file_type == "spec":
        file_output_pathF = imageObj["out_spectral"]["left_path"].split("/Spectral_")[0]
        file_output_path = file_output_pathF + f"/plot_averages{imageObj['timestr']}.csv"
        left_avg = avg_plot(left_img)
        with open(file_output_path, "a")as fh:
            n_ = imageObj["out_spectral"]["left_path"].split("/split_plots/")[1].split(".hdr")[0]
            fh.write(f"{n_}, ")
            for i in range(224):
                v = left_avg[i]
                fh.write(str(v)+", ")
            fh.write("\n")

        right_avg = avg_plot(right_img)
        with open(file_output_path, "a") as fh:
            n_ = imageObj["out_spectral"]["right_path"].split("/split_plots/")[1].split(".hdr")[0]
            fh.write(f"{n_}, ")
            for i in range(224):
                v = right_avg[i]
                fh.write(str(v) + ", ")
            fh.write("\n")

    hdr.metadata["x_split"] = imageObj['x_split']
    hdr.metadata["modified"] = "MSP -v0.1.3"
    envi.save_image(out_path["left_path"], image=left_img, force=True, dtype=np.int16, ext="raw", metadata=hdr.metadata)
    envi.save_image(out_path["right_path"], image=right_img, force=True, dtype=np.int16, ext="raw", metadata=hdr.metadata)



def spec_to_comb(path_:str):

    # replace folder name
    path_ = re.sub("/spectral/", "/combined/", path_)
    # add file extension
    path_ = re.sub("\.hdr", ".cmb.hdr", path_)
    # rename file start
    path_ = re.sub("/Spectral_", "/Combined_", path_)

    if verify_paths and not os.path.isfile(path_):
        raise FileNotFoundError(f"File does not exist, or path creation is bad. {path_}")

    return path_

def comb_to_spec(path_:str):
    # replace folder name
    path_ = re.sub("/combined/", "/spectral/", path_)
    # remove file extension
    path_ = re.sub("\.cmb", "", path_)
    # rename file start
    path_ = re.sub("/Combined_", "/Spectral_", path_)

    if verify_paths and not os.path.isfile(path_):
        raise FileNotFoundError(f"File does not exist, or path creation is bad. {path_}")

    return path_


def make_alt_path(current_path:str):
    spec_path = ""
    comb_path = ""
    if re.search("/spectral/", current_path):
        spec_path = current_path
        comb_path = spec_to_comb(current_path)
    elif re.search("/combined/", current_path):
        comb_path = current_path
        spec_path = comb_to_spec(current_path)
    else:
        raise ValueError("Could not make alt path, as supplied path does not match pattern.")
    return spec_path, comb_path

def make_left_right(path_:str):
    sections = path_.split(".")
    first = sections.pop(0)
    secL = first + "-L."
    secR = first + "-R."

    secL += '.'.join(sections)
    secR += '.'.join(sections)

    secL = re.sub("spectral/Spectral_", "spectral/split_plots/Spectral_", secL)
    secR = re.sub("spectral/Spectral_", "spectral/split_plots/Spectral_", secR)

    secL = re.sub("combined/Combined_", "combined/split_plots/Combined_", secL)
    secR = re.sub("combined/Combined_", "combined/split_plots/Combined_", secR)

    return secL, secR

def make_split_dir(dir_:str):
    if dir_[-1] != "/":
        dir_ += "/"
    comb_ = ''
    spec_ = ''
    if re.search("/spectral/", dir_):
        spec_ = dir_
        comb_ = re.sub("/spectral/", "/combined/", dir_)
    else:
        spec_ = re.sub("/combined/", "/spectral/", dir_)
        comb_ = dir_
    print(spec_)
    comb_ = comb_+"split_plots"
    spec_ = spec_+"split_plots"
    if not os.path.exists(comb_):
        print("Making Combined split_plots directory.")
        os.makedirs(comb_)
    else:
        print(f"{comb_} already exits.")

    if not os.path.exists(spec_):
        print("Making Spectral split_plots directory.")
        os.makedirs(spec_)
    else:
        print(f"{spec_} already exits.")

with open(cd_file, "r") as fh:
    for line in fh.readlines():
        imageObj = json.loads(line)
        path = os.path.join(imageObj["dir"], imageObj["file"])

        make_split_dir(imageObj["dir"])

        spec, comb = make_alt_path(path)
        specL, specR = make_left_right(spec)
        combL, combR = make_left_right(comb)

        imageObj["out_spectral"] = {
            "existing_path": spec,
            "left_path": specL,
            "right_path": specR
        }
        imageObj["out_combined"] = {
            "existing_path": comb,
            "left_path": combL,
            "right_path": combR
        }
        imageObj["timestr"] = timestr

        pprint(imageObj)

        spec_proc = Process(target=split_file, args=(imageObj,"spec"))
        comb_proc = Process(target=split_file, args=(imageObj,"comb"))

        spec_proc.start()
        comb_proc.start()
        spec_proc.join()
        spec_proc.join()




