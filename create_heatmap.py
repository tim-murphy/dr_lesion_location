import csv
import cv2
import math
import numpy as np
import os
from PIL import Image
import sys

# constants
RIGHT_EYE = 0
LEFT_EYE = 1
BOTH_EYES = 2

# distance (in pixels) from the optic nerve to the macular in each scaled image
NERVE_MAC_DIST = 250

# Vertical distance (in pixels) from the optic nerve to the macular in each
# scaled image. Used to rotate each image to the same orientation.
MAC_DROP = int(float(NERVE_MAC_DIST) * 0.1)
MAC_ANGLE = math.degrees(math.atan(float(MAC_DROP) / float(NERVE_MAC_DIST)))

# the (x,y) coordinate of the optic nerve on the heatmap canvas
# note: (NERVE_COORD, NERVE_COORD) is the coordinate to use.
# note: this canvas will be necessarily huge because the photos have large
#       borders which cannot be stripped until after processing is finished
NERVE_COORD = 1000

# trim - the resulting image will have large black borders, so cut this
# much off each side (measured in pixels)
SUPERIOR=0
NASAL=1
INFERIOR=2
TEMPORAL=3
TRIM = [450, 600, 450, 300]

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

            coords.append(CoordsData(os.path.join(image_dir, IMAGE_SUBDIR, row[0]),
                          (int(row[1]), int(row[2])),
                          (int(row[3]), int(row[4]))))

    return coords

def printUsage():
    print("Usage: " + sys.argv[0] + " <coordinates_csv> <image_dir>")

def addText(image, position, text):
    cv2.putText(image, text, position, cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,255), 2)
    return image

# Scale the image such that the distance between the nerve
# and macula is NERVE_MAC_DIST. Return the scaled (x,y) position
# of the nerve in the scaled image, as well as the scaling factor
# and rotation required.
# @param image_data CoordsData object
def scaleImage(image_data):
    # Calculate the distace from the nerve to the mac. Ye Olde Pythagoras.
    x = abs(image_data.nerve_xy[0] - image_data.mac_xy[0])
    y = abs(image_data.nerve_xy[1] - image_data.mac_xy[1])
    orig_dist = int(math.sqrt((x*x) + (y*y)))

    if (orig_dist == 0):
        print("ERROR: invalid tagging for image (ignoring): " + image_data.filename)
        return None, None

    # Calculate the angle from the nerve to the mac
    angle = math.degrees(math.atan(float(y) / float(x)))

    # Image rotation required (in degrees)
    rotation = MAC_ANGLE - angle

    scaling_factor =  float(NERVE_MAC_DIST) / float(orig_dist)

    side = "(right)"
    if (rightOrLeft(image_data) == LEFT_EYE):
        side = "(left)"

    print(os.path.basename(image_data.filename),\
          side,\
          "- scaling factor", scaling_factor,\
          "- rotation", rotation)

    new_nerve_xy = (int(float(image_data.nerve_xy[0]) * scaling_factor),
                    int(float(image_data.nerve_xy[1]) * scaling_factor))

    return new_nerve_xy, scaling_factor, rotation

# @param image_data CoordsData object
def rightOrLeft(image_data):
    if (image_data.nerve_xy[0] > image_data.mac_xy[0]):
        return RIGHT_EYE
    return LEFT_EYE

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
    heatmap_data = np.zeros((3, NERVE_COORD * 2, NERVE_COORD * 2), dtype=np.uint16)

    for record in coords_data:
        if (not os.path.exists(record.filename)):
            print("ERROR: image does not exist (ignoring): " + record.filename)
            continue

        side = rightOrLeft(record)

        # Calculate the scaling factor and scaled nerve position. This determines
        # how to scale the lesion coordinates, and how far to translate them to
        # make sure everything lines up.
        nerve_xy_scaled, scaling_factor, rotation = scaleImage(record)

        if (nerve_xy_scaled == None or scaling_factor == None):
            print("ERROR: ignoring file: " + record.filename)
            continue

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

            # ...convert to binary (for ease of processing)...
            np.where(lesion_orig > 0, 1, 0)

            # ...scale it...
            lesion_scaled = cv2.resize(lesion_orig, None,
                                       fx=scaling_factor,
                                       fy=scaling_factor)

            # ...rotate it...
            rot_matrix = cv2.getRotationMatrix2D(nerve_xy_scaled, rotation, 1.0)
            img_dims = (len(lesion_scaled[0]), len(lesion_scaled))
            lesion_scaled = cv2.warpAffine(lesion_scaled, rot_matrix, img_dims)

            # ...and mark it in our heatmap matrix
            y_from = NERVE_COORD - nerve_xy_scaled[1]
            y_to = y_from + len(lesion_scaled)
            x_from = NERVE_COORD - nerve_xy_scaled[0]
            x_to = x_from + len(lesion_scaled[0])

            if (x_from < 0 or y_from < 0 or x_to > len(heatmap_data[side]) or y_to > len(heatmap_data[side][0])):
                print("ERROR:", lesion, "mapping outside of bounds (ignoring):", os.path.basename(record.filename))
                continue

            heatmap_data[side][y_from:y_to, x_from:x_to] += lesion_scaled

            # add data to our composite heatmap as well - represented as right side,
            # so need to mirror left data.
            if (side == LEFT_EYE):
                lesion_scaled = np.fliplr(lesion_scaled)
                x_from = NERVE_COORD - len(lesion_scaled[0]) + nerve_xy_scaled[0]
                x_to = x_from + len(lesion_scaled[0])
            heatmap_data[BOTH_EYES][y_from:y_to, x_from:x_to] += lesion_scaled

    # We now have a giant array with count values. Convert to a uint8 array with
    # normalised values.
    heatmap_image = np.zeros((3, NERVE_COORD * 2, NERVE_COORD * 2), dtype=np.uint8)
    for side in [RIGHT_EYE, LEFT_EYE, BOTH_EYES]:
        print("Generating " + ("right", "left", "composite")[side] + " heatmap")
        heatmap_scale = 255.0 / float(max(1, heatmap_data[side].max()))
        heatmap_image[side] = heatmap_data[side] * heatmap_scale

        # add the optic nerve visualisation
        cv2.circle(heatmap_image[side], (NERVE_COORD, NERVE_COORD), 45, (255), 2)
        cv2.circle(heatmap_image[side], (NERVE_COORD, NERVE_COORD), 30, (255), 2)
        cv2.circle(heatmap_image[side], (NERVE_COORD, NERVE_COORD), 15, (255), 2)

        # and the macula
        cv2.circle(heatmap_image[side],
                   (NERVE_COORD - ((1, -1, 1)[side] * NERVE_MAC_DIST),
                    NERVE_COORD + MAC_DROP),
                   25, (255), 2)

    # trim the black edges from the images
    orig_x_len = len(heatmap_image[0])
    orig_y_len = len(heatmap_image[0][0])
    x_len = orig_x_len - TRIM[NASAL] - TRIM[TEMPORAL]
    y_len = orig_y_len - TRIM[SUPERIOR] - TRIM[INFERIOR]

    trimmed = np.zeros((3, x_len, y_len), dtype=np.uint8)
    trimmed[RIGHT_EYE] = heatmap_image[RIGHT_EYE][TRIM[SUPERIOR]:orig_x_len-TRIM[INFERIOR],\
                                                  TRIM[TEMPORAL]:orig_y_len-TRIM[NASAL]]
    trimmed[LEFT_EYE] = heatmap_image[LEFT_EYE][TRIM[SUPERIOR]:orig_x_len-TRIM[INFERIOR],\
                                                TRIM[NASAL]:orig_y_len-TRIM[TEMPORAL]]
    trimmed[BOTH_EYES] = heatmap_image[BOTH_EYES][TRIM[SUPERIOR]:orig_x_len-TRIM[INFERIOR],\
                                                  TRIM[TEMPORAL]:orig_y_len-TRIM[NASAL]]

    # add some descriptive text
    addText(trimmed[RIGHT_EYE], (30,50), "A: Right Eye")
    addText(trimmed[LEFT_EYE], (30,50), "B: Left Eye")
    addText(trimmed[BOTH_EYES], (30,50), "C: Combined")

    stack = np.hstack((trimmed[RIGHT_EYE], trimmed[LEFT_EYE], trimmed[BOTH_EYES]))

    cv2.imwrite("heatmap.png", stack)

    ## TESTING ##
    stack = cv2.resize(stack, (1500, 500))
    cv2.imshow("heatmap", stack)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# EOF