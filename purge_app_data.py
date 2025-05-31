import os
import shutil
from datetime import datetime, timedelta, timezone

# Set the paths to your folders
app_data_folder = "/root/radar-processing-data/app_data"
tif_data_folder = "/root/radar-processing-data/tif_files"

# Get the current UTC time
now = datetime.now(timezone.utc)

# Define the time threshold (2 hours ago)
time_threshold = now - timedelta(hours=2)

# Function to delete old folders
def delete_old_folders(folder_path):
    for folder_name in os.listdir(folder_path):
        folder_full_path = os.path.join(folder_path, folder_name)

        # Check if the item is a directory and matches the date format
        if os.path.isdir(folder_full_path) and len(folder_name) == 16:
            try:
                # Parse the folder name as a datetime object in UTC
                folder_date = datetime.strptime(folder_name, "%Y-%m-%d_%H-%M")
                folder_date = folder_date.replace(tzinfo=timezone.utc)

                # Check if the folder is older than the threshold
                if folder_date < time_threshold:
                    # Delete the folder
                    shutil.rmtree(folder_full_path)
                    
            except ValueError:
                # Skip any folders that don't match the date format
                print(f"Skipped folder (invalid date format): {folder_name}")

# Delete old folders in both app_data_folder and tif_data_folder
delete_old_folders(app_data_folder)
delete_old_folders(tif_data_folder)
