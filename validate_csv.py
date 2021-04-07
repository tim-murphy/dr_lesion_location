# Simple script to do some basic validation of the CSV data

import csv
import os
import sys

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print("Usage: " + sys.argv[0] + " <csv_file>")
        sys.exit(1)

    cli_args_valid = True
    coords_csv = os.path.abspath(sys.argv[1])
    if (not os.path.exists(coords_csv)):
        print("ERROR: coordinates_csv file \"" + coords_csv + "\" does not exist")
        cli_args_valid = False

    if (not cli_args_valid):
        sys.exit(1)

    print("Using CSV file \"" + coords_csv + "\"")

    rows_tested = 0
    file_errors = 0

    tested_images = list()
    if (os.path.exists(coords_csv)):
        with open(coords_csv) as csvfile:
            coords_data = csv.reader(csvfile, delimiter=',')
            for index, row in enumerate(coords_data):
                # ignore the first row - header
                if (index == 0):
                    continue

                rows_tested += 1

                if (row[0] in tested_images):
                    print("ERROR: image found multiple times in outfile (ignoring): " + row[0])
                    file_errors += 1
                    continue

                tested_images.append(row[0])

                # if the nerve and mac positions are the same, this was
                # probably due to a double click.
                if (row[1] == row[3] and row[2] == row[4]):
                    print("ERROR: nerve and macular position are the same (double click?): " + row[0])
                    file_errors += 1

    print("== Total rows checked:", rows_tested, "==")
    print("== Total errors found:", file_errors, "==")

    sys.exit(file_errors)