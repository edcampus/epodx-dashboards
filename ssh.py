#!/usr/bin/env python

"""Program: SSH from Python
Programmer: Michael Fryar, Research Fellow, EPoD
Date created: August 28, 2017

Purpose: Establish SSH tunnel using python rather than bash
"""

import os
import subprocess

import get_credentials
from write_to_gsheets_AGG import write_to_sheet

# Change to directory containing configuration files
home_dir = os.path.expanduser('~')
epodx_dir = os.path.join(home_dir, 'Documents/epodx')
dashboards_dir = os.path.join(home_dir, 'Documents/epodx-dashboards')
os.chdir(epodx_dir)

# Establish ssh tunnel in background that auto-closes
# -f "fork into background", -F "use configuration file"
# -o ExistOnForwardFailure=yes "wait until connection and port
#   forwardings are set up before placing in background"
# sleep 10 "give python script 10 seconds to start using tunnel and
#   close tunnel after python script stops using it"
# Ref 1: https://www.g-loaded.eu/2006/11/24/auto-closing-ssh-tunnels/
# Ref 2: https://gist.github.com/scy/6781836

config = "-F ./ssh-config epodx-analytics-api"
option = "-o ExitOnForwardFailure=yes"
ssh = "ssh -f {} {} sleep 10".format(config, option)
subprocess.run(ssh)

# Write to Google Sheets
if __name__ == '__main__':
    credentials = get_credentials.get_credentials()
    write_to_sheet()
