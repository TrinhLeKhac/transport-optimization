#!/bin/bash
# This scripts is used to run multiple python script to preprocessing, transform and ingest all data to database, that servers for SuperAI project
# There are 2 arguments
# $1 mode get data (init | daily)
# $2 mode run (excel | api)

# Change cwd to the project's directory
cd ~/superai

# Active virtual environment
source ./venv/bin/activate &&

# Stop module supervisord for updating data
sudo systemctl stop supervisord &&

# Run script processing data
python ./scripts/processing/total_processing.py --mode $2 &&

# Run script out data for API
python ./scripts/output/out_data_api.py &&

# Run script out data for visualization
python ./scripts/output/out_data_final.py &&

# Run script out data query database
python ./scripts/output/out_data_query_db.py --mode $1 &&

# Run script ingest data to database
python ./scripts/database/ingest_data.py --mode $1 &&

# Start again module supervisord after updating data
sudo systemctl start supervisord
