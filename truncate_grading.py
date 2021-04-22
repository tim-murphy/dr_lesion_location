import csv
import os
import sys

grading_csv = "grading.csv.orig"
coords_csv = "coordinates.csv"
outfile = "grading.csv"

for f in [grading_csv, coords_csv]:
    if (not os.path.exists(f)):
        print("ERROR: file does not exist: " + f)
        sys.exit(1)

grading_orig = {}
with open(grading_csv) as csvfile:
    data = csv.reader(csvfile, delimiter=',')
    for row in data:
        if (len(row) < 2):
            print("WARN: invalid row: " + row)
            continue
        grading_orig[row[0]] = row[1]

grading_trunc = []
with open(coords_csv) as csvfile:
    data = csv.reader(csvfile, delimiter=',')
    for i, row in enumerate(data):
        if (i == 0): continue # skip the first row

        if (len(row) < 2):
            print("WARN: invalid row: " + row)
            continue
        filename = row[0]
        if (filename in grading_orig):
            grading_trunc.append((filename, grading_orig[filename]))
        else:
            print("ERROR: could not find file: " + filename)

# header first
with open(outfile, 'w') as of:
    print("file,grade", file=of)

# and the rest of the data
with open(outfile, 'a') as of:
    for row in grading_trunc:
        print(row[0] + "," + row[1], file=of)

# EOF
