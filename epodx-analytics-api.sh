#!/bin/bash

# Change directory to folder with ssh configuration files
cd ~/Documents/epodx

# Establish ssh tunnel in background that auto-closes
# -f "fork into background", -F "use configuration file"
# -o ExistOnForwardFailure=yes "wait until connection and port 
#	forwardings are set up before placing in background"
# sleep 10 "give python script 10 seconds to start using tunnel and 
#	close tunnel after python script stops using it"
# Ref 1: https://www.g-loaded.eu/2006/11/24/auto-closing-ssh-tunnels/
# Ref 2: https://gist.github.com/scy/6781836
configfile="./ssh-config epodx-analytics-api"
ssh -f -F $configfile -o ExitOnForwardFailure=yes sleep 10

# Run python script
cd ~/Documents/epodx-dashboards
python27 write_to_gsheets_AGG.py


