#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Program: Pull Learner Engagement
Programmer: Michael Fryar, Training Analytics Associate, EPoD
Date created: January 19, 2018

Purpose: Establish SSH tunnel to edX Analytics API and download learner
engagement data.
"""

# Standard library imports
import csv         # For reading data in comma separated value format
from datetime import datetime    # For timestamping csv files
import os          # For manipulating paths and changing directory
import subprocess  # For spawning ssh tunnel
import time        # For calculating run time

# Third-party imports
import requests                  # "HTTP for Humans"

# Start timer
start_time = time.time()


def ssh():
    """SSH tunnel to EPoDX API"""
    # Change to directory containing configuration files.
    home_dir = os.path.expanduser('~')
    epodx_dir = os.path.join(home_dir, 'Documents/epodx')
    os.chdir(epodx_dir)

    # Establish SHH tunnel in background that auto-closes.
    # -f "fork into background"
    # -F "use configuration file"
    # -o ExistOnForwardFailure=yes "wait until connection and port
    #     forwardings are set up before placing in background"
    # sleep 10 "give Python script 10 seconds to start using tunnel and
    #     close tunnel after python script stops using it"
    # Ref 1: https://www.g-loaded.eu/2006/11/24/auto-closing-ssh-tunnels/
    # Ref 2: https://gist.github.com/scy/6781836

    config = "-F ./ssh-config epodx-analytics-api"
    option = "-o ExitOnForwardFailure=yes"
    ssh = "ssh -f {} {} sleep 10".format(config, option)
    subprocess.run(ssh, shell=True)


# Read secret token needed to connect to API from untracked file.
with open("hks_secret_token.txt", "r") as myfile:
    hks_secret_token = myfile.read().replace('\n', '')


def pull_engagement_data(course):
    """Downloads learner engagement data from EPoDx

    edX stores data on how learners engage with content on EPoDx each week.
    This function downloads engagement data via the API for archiving.

    Args:
        course (str): Three letter course code. Known values are:
            AGG - Aggregating Evidence
            COM - Commissioning Evidence
            CBA - Cost-Benefit Analysis
            DES - Descriptive Evidence
            IMP - Impact Evaluations
            SYS - Systematic Approaches to Policy Decisions

    """
    # Define parameters for extracting learner profile data.
    course_id = "course-v1:epodx+BCURE-{}+2016_v1".format(course)
    learner_profile_report_url = "http://localhost:18100/api/v0/learners/"
    headers = {
        "Authorization": "Token {}".format(hks_secret_token),
        "Accept": "text/csv",
    }
    # The list of fields you've requested.
    # Leave this parameter off to see the full list of fields.
    fields = ','.join(["user_id", "username", "name",
                       "engagements.problems_attempted",
                       "engagements.problems_completed",
                       "engagements.videos_viewed",
                       "engagements.discussion_contributions"])
    params = {
        "course_id": course_id,
        "fields": fields,
        "segments": "highly_engaged,disengaging,struggling"
    }
    # Download learner data.
    with requests.Session() as s:
        download = s.get(
            learner_profile_report_url, headers=headers, params=params)
    # Decode learner data.
    decoded_content = download.content.decode('ascii', 'ignore')
    # Extract data from CSV into list.
    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    learner_profiles = list(cr)
    # Change to directory where engagment files are saved.
    home_dir = os.path.expanduser('~')
    archive_path = (
        'Dropbox (CID)\Training Assessment and Research' +
        '\BCURE Learner Engagement Reports\{}'.format(course)
    )
    archive_dir = os.path.join(home_dir, archive_path)
    os.chdir(archive_dir)
    # Get timestamp to add to file name
    now = datetime.utcnow().strftime("%Y-%m-%d_%H.%M.%S")
    # Write data to csv
    # TODO: Add column with date range and then append
    csvname = '{}_engagement_{}_UTC.csv'.format(course, now)
    with open(csvname, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        try:
            for row in learner_profiles:
                writer.writerow(row)
        except csv.Error as e:
            sys.exit(
                'file {}, line {}: {}'.format(filename, reader.line_num, e)
            )
    print("Engagement data written to {}\{}".format(course, csvname))


if __name__ == '__main__':
    print("Beginning to write engagement data to Dropbox (CID)"
          "\Training Assessment and Research\BCURE Learner Engagement Reports")
    ssh()
    courses = ["AGG", "CBA", "COM", "DES", "IMP", "SYS"]
    for course in courses:
        pull_engagement_data(course)

    total_time = round((time.time() - start_time), 2)
    print("Total run time: {} seconds".format(total_time))
