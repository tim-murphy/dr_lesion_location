## Data Preparation

This project uses the data from the [DDR](https://github.com/nkicsl/DDR-dataset)
dataset by Li and colleagues. We need to do some preparation first before we can
do any analysis.

### Zip File Extraction

The DDR dataset comprises of multiple zip files, however all of the annotations
are in the *DDR-dataset.zip.010.zip* file. Download this file and unzip it
somewhere - I'll assume it's in your Downloads folder. This should create a
file called *DDR-dataset.zip.010*. Rename this to *DDR-dataset.zip.010.zip* (add
*.zip* to the end of the filename) and unzip it again. Again, I'll assume this
is in your Downloads folder. This should create a folder called *DDR-dataset*,
which contains all the data we need To use it, but it's stored in a bunch of
sub-directories, so we need to consolidate it into one directory. To do this,
run the following python script (included in this repository):

> `python ./extract_images.py <unzipped_dir> <output_dir>`

For example, if the data is in your Downloads folder:

> `python ./extract_images.py "${USERPROFILE}/Downloads/DDR-dataset" dataset`

This will put all of the images and annotations into the *dataset* folder.
