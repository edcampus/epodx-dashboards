#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Program: Update Dashboard
Programmer: Michael Fryar, Research Fellow, EPoD
Date created: January 5, 2017

Purpose: Establish SSH tunnel to edX Analytics API, download learner
data, and write data to Google Sheets via Sheets API.

First time: Must run get_credentials.py first
"""

# Standard library imports
import csv         # For reading data in comma separated value format
import os          # For manipulating paths and changing directory
import subprocess  # For spawning ssh tunnel
import time        # For calculating run time

# Third-party imports
import httplib2                  # "A comprehensive HTTP client library"
import requests                  # "HTTP for Humans"
from apiclient import discovery  # For acessing Google Sheets API

# User-written imports
import secrets                   # Token for edX Analytics API authentication
# For getting OAuth2 credentials to interact with Google Sheets API
from get_credentials import get_credentials

# Start timer
START_TIME = time.time()

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
    command = "ssh -f {} {} sleep 10".format(config, option)
    subprocess.run(command, shell=True)


def write_to_g_sheet(course, partner, data_selection='both'):
    """Downloads learner data from EPoDx and writes to Google Sheets.

    edX stores identifiable information about learners separately from
    problem response data, which is identifiable by user_id only.  This
    function downloads learner data and problem response data via the
    edX Analytics API and then writes this data to a Google Sheet via
    the Sheets API.

    Args:
        course (str): Three letter course code. Known values are:
            AGG - Aggregating Evidence
            COM - Commissioning Evidence
            CBA - Cost-Benefit Analysis
            DES - Descriptive Evidence
            IMP - Impact Evaluations
            SYS - Systematic Approaches to Policy Decisions

        partner (str): Separate dashboards are required for each partner
        because of the static nature of the dashboards means that a single
        dashboard cannot be used by two different partners simultaneously.
        Known values are:
            HKS - Write to master sheet reserved for HKS trainings
            LBSNAA - Write to master sheet reserved for LBSNAA trainings
            NSPP1 - Write to 1st master sheet reserved for NSPP trainings
            NSPP2 - Write to 2nd master sheet reserved for NSPP trainings

        data_selection (str): Specifies whether to download and write only
        learner profiles, only problem responses or both. Known values are:
            both - Download and write both learner profiles & problem responses
            problems - Only download problem responses
            profiles - Only download learner profiles
    """
    course_id = "course-v1:epodx+BCURE-{}+2016_v1".format(course)
    spreadsheetId = secrets.PARTNER_SHEET_KEYS["{}_{}".format(course, partner)]

    if data_selection == "both":
        message_to_print = ("Downloading and writing {} learner profiles and "
                            "problem responses.".format(course)
                            )
        print(message_to_print)

    if data_selection in ("both", "profiles"):
        # Define parameters for extracting learner profile data.
        learner_profile_report_url = "http://localhost:18100/api/v0/learners/"
        headers = {
            "Authorization": "Token {}".format(HKS_SECRET_TOKEN),
            "Accept": "text/csv",
        }
        # The list of fields you've requested.
        # Leave this parameter off to see the full list of fields.
        fields = ','.join(["user_id", "username", "name", "email", "language",
                           "location", "year_of_birth", "gender",
                           "level_of_education", "mailing_address", "goals",
                           "enrollment_mode", "segments", "cohort", "city",
                           "country", "enrollment_date", "last_updated"])
        params = {
            "course_id": course_id,
            "fields": fields,
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
        # TODO: Explore deleting all but specified cohort. Be sure to plan.
    elif data_selection == "problems":
        message_to_print = ("Downloading and writing {} problem responses "
                            "only.".format(course)
                            )
        print(message_to_print)

    if data_selection in ("both", "problems"):
        # Define parameters for extracting problem response data.
        problem_api_url = ("http://localhost:18100/api/v0/courses/"
                           "{}/reports/problem_response".format(course_id))
        headers = {"Authorization": "Token {}".format(HKS_SECRET_TOKEN)}
        problem_data = requests.get(problem_api_url, headers=headers).json()
        problem_download_url = problem_data['download_url']
        # Download the CSV from download_url.
        with requests.Session() as s:
            download = s.get(problem_download_url)
        # Decode problem response data.
        decoded_content = download.content.decode('ascii', 'ignore')
        # Extract data from CSV into list.
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        problem_responses = list(cr)
        # TODO: Explore deleting all responses older than 31 days
    elif data_selection == "profiles":
        message_to_print = ("Downloading and writing {} learner profiles "
                            "only.".format(course)
                            )
        print(message_to_print)

    # This section builds on Google quickstart template.
    # https://developers.google.com/sheets/api/quickstart/python
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    if data_selection in ("both", "profiles"):
        learners_range = 'student_profile_info'
    if data_selection in ("both", "problems"):
        problem_range = 'problem_responses'
    if data_selection == "both":
        data = [
            {
                'range': learners_range,
                'values': learner_profiles
            },
            {
                'range': problem_range,
                'values': problem_responses
            }
        ]
    elif data_selection == "profiles":
        data = [
            {
                'range': learners_range,
                'values': learner_profiles
            }
        ]
    elif data_selection == "problems":
        data = [
            {
                'range': problem_range,
                'values': problem_responses
            }
        ]
    body = {'valueInputOption': 'RAW', 'data': data}
    result = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheetId, body=body).execute()


def tunnel_and_write_to_g_sheet(dashboard):
    """Establish SSH tunnel, download data, and write to Google Sheet"""
    ssh()
    course = dashboard[0]
    partner = dashboard[1]
    if "profiles" in dashboard:
        data_selection = "profiles"
    elif "problems" in dashboard:
        data_selection = "problems"
    else:
        data_selection = "both"

    write_to_g_sheet(course, partner, data_selection)
    print("Upload {} to {} {} master sheet complete".format(
        data_selection, course, partner))


if __name__ == '__main__':
    dashboards = [
        ["SYS", "NSPP1"],
    ]

    for dashboard in dashboards:
        tunnel_and_write_to_g_sheet(dashboard)

    TOTAL_TIME = round((time.time() - START_TIME), 2)
    print("Total run time: {} seconds".format(TOTAL_TIME))
