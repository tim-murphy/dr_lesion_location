import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import colors
from matplotlib._cm import _jet_data # hack to get more precision
import numpy as np
import scipy.cluster.vq as scv

import csv
import cv2
import glob
import os
import shutil
import sys

LESION_DIRS = ["EX", "HE", "MA", "SE", "IRMA", "NVE", "NVD", "VB"]

# take our dataset and split it into four subsets based on grading
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage:", sys.argv[0], "<dataset> <grading_csv> [<output_suffix=dataset_>]")
        sys.exit(1)

    dataset = sys.argv[1]
    if not os.path.exists(dataset):
        print("ERROR: dataset directory does not exist:", dataset)
        sys.exit(1)

    grading_csv = sys.argv[2]
    if not os.path.exists(grading_csv):
        print("ERROR: grading CSV file does not exist:", grading_csv)
        sys.exit(1)

    output_suffix = "dataset_"
    if len(sys.argv) > 3:
        output_suffix = sys.argv[3]

    print("copying files...", end="", flush=True)

    # grab all of the files from the grading csv
    # two rows: "file" and "grade"
    grading_data = csv.DictReader(open(grading_csv))
    for grade_row in grading_data:
        filename = grade_row["file"]
        grade = int(grade_row["grade"])

        # move the image first
        outdir = output_suffix + str(grade)
        os.makedirs(outdir, exist_ok=True)

        imgdir = os.path.join(outdir, "image")
        os.makedirs(imgdir, exist_ok=True)
        imgpath = os.path.join(dataset, "image", filename)
        if not os.path.exists(imgpath):
            print("ERROR: image does not exist:", imgpath)
            sys.exit(1)

        shutil.copyfile(imgpath, os.path.join(imgdir, filename))

        for l in LESION_DIRS:
            lesiondir = os.path.join(outdir, "label", l)
            os.makedirs(lesiondir, exist_ok=True)
            lesionfilename = filename.replace(".jpg", ".tif")
            lesionpath = os.path.join(dataset, "label", l, lesionfilename)
            if not os.path.exists(lesionpath):
                print("ERROR: lesion file does not exist:", lesionpath)
                sys.exit(1)

            shutil.copyfile(lesionpath, os.path.join(lesiondir, lesionfilename))

        print(".", end="", flush=True)

    print("done")

# EOF
