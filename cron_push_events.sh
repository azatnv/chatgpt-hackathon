#!/bin/bash
app_dir=/root/itmo-events/chatgpt-hackathon

cd $app_dir

source .venv/bin/activate

python push_events.py > $app_dir/cronlogs 2>&1

deactivate

echo "PUSHED" >> $app_dir/cronlogs
