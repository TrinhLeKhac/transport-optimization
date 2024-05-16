#!/bin/bash
# This scripts is used to run multiple python script to preprocessing,
# transform and ingest all data to database, that servers for SuperAI project
# There are 3 arguments
# $1 run mode (init | daily) --mode|-m
# $2 type of get data (excel | api) --get-data|-g
# $3 run date (2024-01-15 | None) --run-date|-r

for argument in "$@"
do
  key=$(echo $argument | cut --fields 1 --delimiter='=')
  value=$(echo $argument | cut --fields 2 --delimiter='=')

  case "$key" in
    --mode|-m)        mode="$value" ;;
    --get-data|-g)    get_data="$value" ;;
    --run-date|-r)    run_date="$value" ;;
    *)
  esac
done

if [ -z "$3" ]
  then
    run_date=$(date +%F)
fi

# Change cwd to the project's directory
cd ~/superai

# Active virtual environment
source ./venv/bin/activate &&

# Stop module supervisord for updating data
#sudo systemctl stop supervisord &&

# Run script processing data
python ./scripts/processing/total_processing.py --mode $get_data --run_date $run_date &&

# Run script out data for API
python ./scripts/output/out_data_api.py --run_date $run_date &&

# Run script out data for visualization
python ./scripts/output/out_data_final.py --run_date $run_date &&

# Run script out data query database
python ./scripts/output/out_data_query_db.py --mode $mode &&

# Run script ingest data to database
python ./scripts/database/ingest_data.py --mode $mode --run_date $run_date &&

# Start again module supervisord after updating data
#sudo systemctl start supervisord &&

# Call python module to alert SUCCESS to telegram group
python -c "from scripts.utilities.helper import *; telegram_bot_send_success_message()"