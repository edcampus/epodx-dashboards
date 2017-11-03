#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Program: Write to G Sheet
Programmer: Michael Fryar, Research Fellow, EPoD
Date created: January 5, 2017

Purpose: Write to Google Sheets via API.
"""
# Note: Must first establish SSH connection to epodx analytics
# Standard library imports
import csv         # For reading data in comma separated value format
import os          # For manipulating paths and changing directory
import subprocess  # For spawning ssh tunnel

# Third-party imports
import httplib2                  # "A comprehensive HTTP client library"
import requests                  # "HTTP for Humans"
from apiclient import discovery  # For acessing Google Sheets API
# To install apiclient 'pip install --upgrade google-api-python-client'

# User-written imports
from get_credentials import get_credentials
# For getting OAuth2 credentials to interact with Google Sheets API


def ssh():
    """SSH tunnel to EPoDX API"""
    # Change to directory containing configuration files
    home_dir = os.path.expanduser('~')
    epodx_dir = os.path.join(home_dir, 'Documents/epodx')
    os.chdir(epodx_dir)

    # Establish SHH tunnel in background that auto-closes
    # -f "fork into background"
    # -F "use configuration file"
    # -o ExistOnForwardFailure=yes "wait until connection and port
    #     forwardings are set up before placing in background"
    # sleep 10 "give python script 10 seconds to start using tunnel and
    #     close tunnel after python script stops using it"
    # Ref 1: https://www.g-loaded.eu/2006/11/24/auto-closing-ssh-tunnels/
    # Ref 2: https://gist.github.com/scy/6781836

    config = "-F ./ssh-config epodx-analytics-api"
    option = "-o ExitOnForwardFailure=yes"
    ssh = "ssh -f {} {} sleep 10".format(config, option)
    subprocess.run(ssh, shell=True)


# Read secret token needed to connect to API from untracked file
with open("hks_secret_token.txt", "r") as myfile:
    hks_secret_token = myfile.read().replace('\n', '')


def write_to_g_sheet(course):
    """Downloads learner data from EPoDx and writes to Google Sheets.

    edX stores identifiable information about learners separately from
    problem response data, which is identifiable by user_id only. This
    function downloads learner data and problem response data via the
    EPoDx API and then writes this data to a Google Sheet.

    Args:
        course (str): Three letter course code. Known values are
            AGG - Aggregating Evidence
            COM - Commissioning Evidence
            CBA - Cost-Benefit Analysis
            DES - Descriptive Evidence
            IMP - Impact Evaluations
            SYS - Systematic Approaches to Policy Decisions
    """
    course_id = "course-v1:epodx+BCURE-{}+2016_v1".format(course)
    if course == "AGG":
        spreadsheetId = "1uMAyKZYtoVLzqpknBxOGbkLjR7-AMqlEEowdFqSc3pw"
    elif course == "COM":
        spreadsheetId = "1z6xR_xspemndfyQ_hOoYKwBZAjEEA2nqItG__plOgmU"
    elif course == "CBA":
        spreadsheetId = "1-b-1r5CJIWEmGZ0R_vOVJLnmAvCntL88HXPle4XaiJ0"
    elif course == "DES":
        spreadsheetId = "1Yh3MQVz8AddovX1hKYNTwQ23C7OnDmJ9v0T39-lUvPU"
    elif course == "IMP":
        spreadsheetId = "1HUDWhXwr4Ekcs4lsqyGE6qoT4OsPaigH42zbsiY39NE"
    elif course == "SYS":
        spreadsheetId = "1h_RW5_-BduGg9__3wO9HZj7A0ch0DAqY5IQrZlI9Ow4"
    else:
        raise NameError("Module abbreviation not recognized.")

    # Extract learner data first. Start by defining parameters.
    learner_profile_report_url = "http://localhost:18100/api/v0/learners/"
    headers = {
        "Authorization": "Token {}".format(hks_secret_token),
        "Accept": "text/csv",
    }
    # The list of fields you've requested
    # Leave this parameter off to see the full list of fields
    fields = ','.join(["user_id", "username", "name", "email", "language",
                       "location", "year_of_birth", "gender",
                       "level_of_education", "mailing_address", "goals",
                       "enrollment_mode", "segments", "cohort", "city",
                       "country", "enrollment_date", "last_updated"])
    params = {
        "course_id": course_id,
        "fields": fields,
    }
    # Download learner data
    with requests.Session() as s:
        download = s.get(
            learner_profile_report_url, headers=headers, params=params)
    # Decode learner data
    decoded_content = download.content.decode('ascii', 'ignore')
    # Extract data from CSV into list
    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    learner_profiles = list(cr)

    # Extract problem response data. Start by defining parameters
    problem_api_url = ("http://localhost:18100/api/v0/courses/"
                       "{}/reports/problem_response".format(course_id))
    headers = {"Authorization": "Token {}".format(hks_secret_token)}
    problem_data = requests.get(problem_api_url, headers=headers).json()
    problem_download_url = problem_data['download_url']
    # Download the CSV from download_url
    with requests.Session() as s:
        download = s.get(problem_download_url)
    # Decode problem response data
    decoded_content = download.content.decode('ascii', 'ignore')
    # Extract data from CSV into list
    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    problem_responses = list(cr)
    # Next section builds on Google quickstart template to write to Sheets
    # https://developers.google.com/sheets/api/quickstart/python
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    learners_range = 'student_profile_info'
    problem_range = 'problem_responses'
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
    body = {'valueInputOption': 'RAW', 'data': data}
    result = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheetId, body=body).execute()


def tunnel_and_write_to_g_sheet(course):
    """Establish SSH tunnel and write to Google Sheet"""
    ssh()
    write_to_g_sheet(course)

if __name__ == '__main__':
    courses = ["AGG", "COM", "CBA", "DES", "IMP", "SYS"]
    for course in courses:
        tunnel_and_write_to_g_sheet(course)
