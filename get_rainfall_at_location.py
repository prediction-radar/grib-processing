import rasterio
from rasterio.warp import transform
from rasterio.enums import Resampling
import os
import json
import argparse

def get_data_from_tiff_folders(lat, lon):
    """
    Retrieve data values from 'output.tif' files in date-labeled subdirectories for a specific latitude and longitude.
    
    Parameters:
    - root_folder (str): Path to the root folder containing date-labeled subdirectories with 'output.tif' files.
    - lat (float): Latitude of the desired location.
    - lon (float): Longitude of the desired location.
    
    Returns:
    - list: A list of dictionaries with each dictionary containing 'date' and 'dbz' values.
    """
    data_list = []
    root_folder = "/root/radar-processing-data/tif_files"

    # Adjust longitude to -180 to 180 if needed
    if lon > 180:
        lon -= 360

    # Iterate through each date-named subdirectory
    for date_folder in os.listdir(root_folder):
        date_folder_path = os.path.join(root_folder, date_folder)
        
        # Check if the path is a directory
        if os.path.isdir(date_folder_path):
            # Define the path to the 'output.tif' file within the date folder
            tiff_file_path = os.path.join(date_folder_path, 'output.tif')
            
            # Ensure the 'output.tif' file exists
            if os.path.exists(tiff_file_path):
                try:
                    with rasterio.open(tiff_file_path) as src:
                        # Print the bounds of the GeoTIFF to verify coverage
                        bounds = src.bounds
                        
                        # Check if the specified coordinates fall within the bounds
                        if not (bounds.left <= lon <= bounds.right and bounds.bottom <= lat <= bounds.top):
                            print(f"Coordinates ({lat}, {lon}) out of bounds for {tiff_file_path}")
                            data_list.append({"date": date_folder, "dbz": None})
                            continue  # Skip to the next file if out of bounds

                        # Transform the latitude and longitude to the GeoTIFF's CRS
                        dst_crs = src.crs
                        transformed_coords = transform({'init': 'EPSG:4326'}, dst_crs, [lon], [lat])
                        
                        # Get the row and column of the nearest pixel to the specified coordinates
                        row, col = src.index(transformed_coords[0][0], transformed_coords[1][0])
                        
                        # Double-check row and col are within raster bounds
                        if 0 <= row < src.height and 0 <= col < src.width:
                            # Read the data at that pixel
                            data_value = src.read(1, window=((row, row + 1), (col, col + 1)), resampling=Resampling.nearest)[0][0]
                            data_list.append({"date": date_folder, "dbz": data_value})
                        else:
                            print(f"Transformed coordinates out of raster bounds for {tiff_file_path}")
                            data_list.append({"date": date_folder, "dbz": None})  # Mark out-of-bounds as None

                except Exception as e:
                    print(f"Error processing {tiff_file_path} in {date_folder}: {e}")
                    data_list.append({"date": date_folder, "dbz": None})  # Handle error by setting value to None

    # Convert the list of dictionaries to a JSON string
    data_json = json.dumps(data_list, indent=2)
    return data_json

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Extract data from GeoTIFF files based on latitude and longitude.")
    parser.add_argument("latitude", type=float, help="Latitude of the location.")
    parser.add_argument("longitude", type=float, help="Longitude of the location.")
    args = parser.parse_args()

    # Run the function with provided arguments
    result = get_data_from_tiff_folders(args.latitude, args.longitude)
    print(result) 
