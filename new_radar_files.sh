rm /root/radar-processing-data/grib_files/*; \
python3 /root/radar-processing-data/download_grib.py && \
/root/radar-processing-data/process_grib.sh && \
python3 /root/radar-processing-data/purge_app_data.py
