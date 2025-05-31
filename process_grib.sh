#!/bin/bash

# Set the root directory
root_dir=/root/radar-processing-data

# Get the current UTC time formatted as "YYYY-MM-DD_HH-MM"
folder_name=$(date -u +"%Y-%m-%d_%H-%M")

# Create the full directory path
app_data_path="$root_dir/app_data/$folder_name"
tif_data_path="$root_dir/tif_files/$folder_name"

# Create the directory
mkdir -p "$app_data_path"
mkdir -p "$tif_data_path"

# Step 1: Convert GRIB2 to GeoTIFF
gdal_translate -of GTiff $root_dir/grib_files/*.grib2 $tif_data_path/output.tif

# Step 2: Reproject the GeoTIFF to Web Mercator (EPSG:3857)
gdalwarp -t_srs EPSG:3857 $tif_data_path/output.tif $app_data_path/reprojected.tif

# Step 3: Convert the image to 8-bit format (Byte), scale pixel values from -999 to 255 to the range 0-255
gdal_translate -of VRT -ot Byte -scale 0 255 0 255 $app_data_path/reprojected.tif $app_data_path/temp.vrt

# Step 4: Apply color classification to create grayscale radar image with `--overwrite`
# Set values below 20 to NoData (0) to make them invisible
gdal_calc.py -A $app_data_path/temp.vrt --A_band=1 --outfile=$app_data_path/colored_radar.tif \
  --calc="(A<=0)*0 + logical_and(A>0, A<=5)*0 + logical_and(A>5, A<=10)*10 + logical_and(A>10, A<=15)*15 + logical_and(A>15, A<=20)*20 + logical_and(A>20, A<=30)*30 + \
  logical_and(A>30, A<=40)*40 + logical_and(A>40, A<=50)*50 + logical_and(A>50, A<=60)*60 + \
  logical_and(A>60, A<=80)*80 + logical_and(A>80, A<=100)*100 + logical_and(A>100, A<=150)*150 + \
  logical_and(A>150, A<=200)*200 + logical_and(A>200, A<=255)*255" \
  --type=Byte --NoDataValue=0 --format=GTiff --overwrite

color_file=$root_dir/color_table.txt

# Step 6: Apply color table using gdaldem
gdaldem color-relief $app_data_path/colored_radar.tif $color_file -of GTiff -alpha -b 1 $app_data_path/colored_radar_rgb.tif

# Step 7: Generate Google Maps-compatible tiles using gdal2tiles with TMS layout
gdal2tiles.py --processes=4 -z 3-9 --xyz $app_data_path/colored_radar_rgb.tif $app_data_path

# Clean up the temporary color file and intermediate files
rm $app_data_path/reprojected.tif $app_data_path/temp.vrt $app_data_path/colored_radar.tif $app_data_path/colored_radar_rgb.tif
