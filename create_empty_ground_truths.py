import cv2
import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

IMAGEDIR = "image"
LESIONDIR = "label"
LESIONS = ["EX", "HE", "MA", "SE", "IRMA", "VB", "NVD", "NVE"]

def printUsage():
    print("Usage:", sys.argv[0], "<dataset>")

# for every image in the dataset
# for all the new lesions
# if the ground truth map doesn't exist
# create an empty one

if __name__ == "__main__":
    if len(sys.argv) < 2:
        printUsage()
        sys.exit(1)

    dataset = sys.argv[1]

    if not os.path.exists(dataset):
        print("ERROR: dataset does not exist:", dataset)
        sys.exit(1)

    # loop through every image in the dataset
    for img in glob.glob(os.path.join(dataset, IMAGEDIR, "*.jpg")):
        imgname = os.path.split(img)[1][:-4]

        # check each lesion
        for lesion in LESIONS:
            lesionfile = imgname + ".tif"
            lesionpath = os.path.join(dataset, LESIONDIR, lesion, lesionfile)

            if not os.path.exists(lesionpath):
                print("Lesion file does not exist - creating a blank file:", lesionpath, " ... ", end="")
                imgdata = plt.imread(img)
                lesionmask = np.zeros((imgdata.shape[0], imgdata.shape[1]), dtype=np.uint8)
                cv2.imwrite(lesionpath, lesionmask)
                print("done")

            print(".", end="")

# EOF
