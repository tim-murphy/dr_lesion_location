import csv
import cv2
import numpy as np
import os
from PIL import Image
import sys

# constants
RIGHT_EYE = 0
LEFT_EYE = 1

# horizontal distance (in pixels) from the optic nerve to
# the macular in each scaled image
NERVE_MAC_DIST = 250

# the (x,y) coordinate of the optic nerve on the heatmap canvas
# note: (NERVE_COORD, NERVE_COORD) is the coordinate to use
NERVE_COORD = 1000

# directory structure for images
IMAGE_SUBDIR = "image"
LESION_SUBDIR = "label"
LESION_TYPES = [ "EX", "HE", "MA", "SE" ]

class CoordsData:
    filename = None
    nerve_xy = None
    mac_xy = None

    def __init__(self, filename, nerve_xy, mac_xy):
        self.filename = filename
        self.nerve_xy = nerve_xy
        self.mac_xy = mac_xy

    def showImage(self):
        image = cv2.imread(self.filename)
        cv2.imshow(self.filename, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def __repr__(self):
        return "[filename=" + self.filename + \
               ", nerve_xy=(" + str(self.nerve_xy) + ")" + \
               ", mac_xy=(" + str(self.mac_xy) + ")]"

def parseCoordsFile(filename, image_dir):
    coords = list()

    with open(filename) as csvfile:
        coords_data = csv.reader(csvfile, delimiter=',')
        for index, row in enumerate(coords_data):
            # ignore the first row - header
            if (index == 0):
                continue

            coords.append(CoordsData(image_dir + "/" + IMAGE_SUBDIR + "/" + row[0],
                          (int(row[1]), int(row[2])),
                          (int(row[3]), int(row[4]))))

    return coords

def printUsage():
    print("Usage: " + sys.argv[0] + " <coordinates_csv> <image_dir>")

# Scale the image such that the distance between the nerve
# and macula is NERVE_MAC_DIST. Return the scaled (x,y) position
# of the nerve in the scaled image, as well as the scaling factor.
# @param image_data CoordsData object
def scaleImage(image_data):
    orig_dist = abs(image_data.nerve_xy[0] - image_data.mac_xy[0])
    scaling_factor =  float(NERVE_MAC_DIST) / float(orig_dist)

    print("Current distance: " + str(orig_dist) + " - scaling factor " + str(scaling_factor))
    new_nerve_xy = (int(float(image_data.nerve_xy[0]) * scaling_factor),
                    int(float(image_data.nerve_xy[1]) * scaling_factor))

    return new_nerve_xy, scaling_factor

# @param image_data CoordsData object
def rightOrLeft(image_data):
    return (RIGHT_EYE, LEFT_EYE)[image_data.nerve_xy[0] > image_data.mac_xy[0]]
    
if __name__ == '__main__':
    if (len(sys.argv) != 3):
        printUsage()
        sys.exit(1)

    cli_args_valid = True

    coords_csv = os.path.abspath(sys.argv[1])
    if (not os.path.exists(coords_csv)):
        print("ERROR: coordinates_csv file \"" + coords_csv + "\" does not exist")
        cli_args_valid = False
    
    image_dir = os.path.abspath(sys.argv[2])
    if (not os.path.exists(image_dir)):
        print("ERROR: image_dir path \"" + image_dir + "\" does not exist")
        cli_args_valid = False

    if (not cli_args_valid):
        sys.exit(1)

    print("Using CSV file \"" + coords_csv + "\"")
    print("with image dir \"" + image_dir + "\"")

    coords_data = parseCoordsFile(coords_csv, image_dir)

    # Initialise the data array (nerve at (NERVE_COORD,NERVE_COORD) which
    # is the middle of our matrix
    heatmap_data = np.zeros((2, NERVE_COORD * 2, NERVE_COORD * 2), dtype=np.uint16)

    for record in coords_data:
        if (not os.path.exists(record.filename)):
            print("ERROR: image does not exist (ignoring): " + record.filename)
            continue

        # Calculate the scaling factor and scaled nerve position. This determines
        # how to scale the lesion coordinates, and how far to translate them to
        # make sure everything lines up.
        nerve_xy_scaled, scaling_factor = scaleImage(record)

        # Load the lesion file(s)
        for lesion in LESION_TYPES:
            lesion_image_path = os.path.join(image_dir, LESION_SUBDIR, lesion, os.path.split(record.filename)[1])

            # lesion files are .tif, not .png, so we need to replace the extension
            lesion_image_path = os.path.splitext(lesion_image_path)[0] + ".tif"

            if (not os.path.exists(lesion_image_path)):
                print("ERROR: lesion file does not exist (ignoring): " + lesion_image_path)
                continue

            # load the image...
            lesion_orig = np.array(Image.open(lesion_image_path))
            # ...scale it...
            lesion_scaled = cv2.resize(lesion_orig, None,
                                       fx=scaling_factor,
                                       fy=scaling_factor)
            # ...and mark it in our heatmap matrix
            for x, vx in enumerate(lesion_scaled):
                for y, vy in enumerate(vx):
                    if (lesion_scaled[x][y] > 0):
                        heatmap_data[rightOrLeft(record)]\
                                    [x + NERVE_COORD - nerve_xy_scaled[1]]\
                                    [y + NERVE_COORD - nerve_xy_scaled[0]] += 1

    # We now have a giant array with count values. Convert to a uint8 array with
    # normalised values.
    heatmap_image = np.zeros((2, NERVE_COORD * 2, NERVE_COORD * 2), dtype=np.uint8)
    for side in [RIGHT_EYE, LEFT_EYE]:
        print(("Right", "Left")[side] + " eye")
        largest_value = 1
        for x, vx in enumerate(heatmap_data[side]):
            for y, vy in enumerate(vx):
                if (vy > largest_value):
                    largest_value = vy
                    print("New largest: " + str(largest_value))

        heatmap_scale = 255.0 / float(largest_value)
        for x, vx in enumerate(heatmap_data[side]):
            for y, vy in enumerate(vx):
                heatmap_image[side][x][y] = int(float(vy) * heatmap_scale)

        # add the optic nerve visualisation
        cv2.circle(heatmap_image[side], (NERVE_COORD, NERVE_COORD), 45, (255), 2)
        cv2.circle(heatmap_image[side], (NERVE_COORD, NERVE_COORD), 30, (255), 2)
        cv2.circle(heatmap_image[side], (NERVE_COORD, NERVE_COORD), 15, (255), 2)

        # and the macula
        cv2.circle(heatmap_image[side],
                   (NERVE_COORD - ((-1, 1)[side] * NERVE_MAC_DIST),
                    NERVE_COORD + int(NERVE_MAC_DIST * 0.1)),
                   25, (255), 2)

    stack = np.hstack((heatmap_image[RIGHT_EYE], heatmap_image[LEFT_EYE]))

    ## TESTING ##
    stack = cv2.resize(stack, (1500, 750))

    cv2.imshow("heatmap", stack)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# EOF