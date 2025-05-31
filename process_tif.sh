#!/bin/bash

# Set the root directory
root_dir=/root/radar-processing-data

# Get the current UTC time formatted as "YYYY-MM-DD_HH-MM"
folder_name=$(date -u +"%Y-%m-%d_%H-%M")

# Create the full directory path
tif_data_path="$root_dir/tif_files/$folder_name"

# Create the directory
mkdir -p "$tif_data_path"

# Step 1: Convert GRIB2 to GeoTIFF
gdal_translate -of GTiff $root_dir/grib_files/*.grib2 $tif_data_path/output.tif
