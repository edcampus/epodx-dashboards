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
import requests    # "HTTP for Humans"

# User-written imports
import secrets     # Token for edX Analytics API authentication

# Start timer
start_time = time.time()

# Get token for edX Analytics API authentication
HKS_SECRET_TOKEN = secrets.HKS_SECRET_TOKEN


def ssh():
    """SSH tunnel to EPoDX API"""
    # Change to directory containing configuration files.
    home_dir = os.path.expanduser('~')
    epodx_dir = os.path.join(home_dir, 'EPoD/epodx')
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
    if course == "DTA":
        course_id = "course-v1:epodx+BCURE-{}+2018_v1".format(course)
    else:
        course_id = "course-v1:epodx+BCURE-{}+2016_v1".format(course)
    learner_profile_report_url = "http://localhost:18100/api/v0/learners/"
    headers = {
        "Authorization": "Token {}".format(HKS_SECRET_TOKEN),
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
        "ignore_segments": "inactive"
    }
    # Download engagement data.
    with requests.Session() as s:
        download = s.get(
            learner_profile_report_url, headers=headers, params=params)
    download_reader = csv.reader(download.text.splitlines(), delimiter=',')
    engagement_data = list(download_reader)
    # Check if there is any new engagement data
    if len(engagement_data):
        # Add timestamp to engagement data
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        for row in engagement_data[1:]:
            row.append(now)

        # Change to directory where engagment files are saved.
        home_dir = os.path.expanduser('~')
        archive_path = (
            'EPoD/Dropbox (CID)/Training Assessment and Research' +
            '/BCURE Learner Engagement Reports/{}'.format(course)
        )
        archive_dir = os.path.join(home_dir, archive_path)
        os.chdir(archive_dir)

        # Append data to master file
        mastername = '{}_engagement_master.csv'.format(course)
        with open(mastername, 'a', newline='') as masterfile:
            writer = csv.writer(masterfile)
            try:
                for row in engagement_data[1:]:
                    writer.writerow(row)
            except csv.Error as e:
                sys.exit(
                    'file {}, line {}: {}'.format(filename, reader.line_num, e)
                )
        print("Engagement data written to {}/{}".format(course, mastername))
    else:
        print("No new engagement data for {}".format(course))


if __name__ == '__main__':
    print("Beginning to write engagement data to Dropbox (CID)"
          "/Training Assessment and Research/BCURE Learner Engagement Reports")
    ssh()
    courses = ["AGG", "CBA", "COM", "DES", "DTA", "IMP", "SYS"]
    for course in courses:
        pull_engagement_data(course)

    total_time = round((time.time() - start_time), 2)
    print("Total run time: {} seconds".format(total_time))
