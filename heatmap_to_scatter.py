# Take a CSV file representing a heatmap and create an X,Y scatter CSV.
# Useful for clustering.

import csv
import os
import sys

def printUsage():
    print("Usage: " + sys.argv[0] + " <heatmap_csv> <outfile> [<threshold>]")

if __name__ == '__main__':
    if len(sys.argv) not in [3,4]:
        printUsage()
        sys.exit(1)

    heatmap_csv = sys.argv[1]
    if not os.path.exists(heatmap_csv):
        print("Error: heatmap_csv does not exist: " + heatmap_csv)
        sys.exit(1)

    outfile = sys.argv[2]

    threshold = 1
    if (len(sys.argv) > 3):
        threshold = int(sys.argv[3])

    print("Processing", end='', flush=True)
    with open(outfile, 'w') as out:
        print("x,y", file=out)
        with open(heatmap_csv, 'r') as csvfile:
            data = csv.reader(csvfile, delimiter=',')
            for y, row in enumerate(data):
                for x, count in enumerate(row):
                    # adjust counts based on threshold
                    count_adj = int(count) - (threshold - 1)
                    for z in range(count_adj):
                        print(str(x) + "," + str(y), file=out)
                        print(".", end='', flush=True)

    print("done")
