# split coordinates file into NoDR, PDR and NPDR files

import csv
import os
import sys

def printUsage():
    print("Usage: " + sys.argv[0] + " <coords_csv> <grading_csv>")

if __name__ == '__main__':
    if (len(sys.argv) != 3):
        printUsage()
        sys.exit(1)

    cmd_args_valid = True

    coords_csv = sys.argv[1]
    grading_csv = sys.argv[2]
    for f in [coords_csv, grading_csv]:
        if (not os.path.exists(f)):
            print("Error: csv file does not exist: " + f)
            cmd_args_valid = False

    if (not cmd_args_valid):
        printUsage()
        sys.exit(1)

    # pull out grading information first
    grading = {}
    with open(grading_csv, 'r') as csvfile:
        csv_data = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(csv_data):
            # ignore header row
            if (i == 0): continue

            grading[row[0]] = row[1]

    # CSV data (stored as full CSV string)
    csv_header = "file,onX,onY,macX,macY"
    pdr = [csv_header]
    npdr = [csv_header]
    nodr = [csv_header]
    with open(coords_csv, 'r') as csvfile:
        csv_data = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(csv_data):
            # ignore header row
            if (i == 0): continue

            filename = row[0]
            if (not filename in grading):
                print("WARN: no grading information for file (ignoring): " +\
                      filename)
                continue

            grade = grading[filename]
            if (grade == "4"):
                pdr.append(",".join(row))
            elif (grade in ["1","2","3"]):
                npdr.append(",".join(row))
            elif (grade == "0"):
                nodr.append(",".join(row))

    # write the files
    for tup in [("nodr", nodr), ("npdr", npdr), ("pdr", pdr)]:
        label = tup[0]
        strings = tup[1]
        outfile = "coords_" + label + ".csv"
        with open(outfile, 'w') as of:
            for s in strings:
                print(s, file=of)

    print("Finished!")

# EOF
