#!/usr/local/bin/python27
# -*- coding: utf-8 -*-

"""
Program: Write to GSheets
Programmer: Michael Fryar, Research Fellow, EPoD
Date created: January 5, 2017

Purpose: Write to Google Sheets via API.
"""
# Note: Must first establish SSH connection to epodx analytics
import requests
import csv
import os
import httplib2
from apiclient import discovery

import get_credentials

# WARNING: Keep your token secret!
with open ("hks_secret_token.txt", "r") as myfile:
    hks_secret_token=myfile.read().replace('\n', '')

# Course_id for Aggregating Evidence
course_id = "course-v1:epodx+BCURE-AGG+2016_v1"

def write_to_sheet():
    """
    Get learner profile information for course_id from epodx
    """
    # The list of fields you've requested. Leave this parameter off to see the
    # full list of fields.
    fields = ','.join(
                    ["user_id", "username", "name", "email", "language",
                    "location", "year_of_birth", "gender",
                    "level_of_education", "mailing_address", "goals",
                    "enrollment_mode", "segments", "cohort", "city",
                    "country", "enrollment_date", "last_updated"])

    learner_profile_report_url = "http://localhost:18100/api/v0/learners/"

    headers = {
            "Authorization":"Token {}".format(hks_secret_token),
            "Accept": "text/csv",
    }

    params = {
            "course_id": course_id,
            "fields": fields,
    }
    with requests.Session() as s:
        download = s.get(learner_profile_report_url, headers=headers,
                         params=params)

        decoded_content = download.content.decode('ascii', 'ignore')

        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        learner_profiles = list(cr)
    """
    Get problem response information for course_id from epodx
    """
    problem_api_url = ("http://localhost:18100/api/v0/courses/"
                        "{}/reports/problem_response".format(course_id))
    headers = {"Authorization":"Token {}".format(hks_secret_token)}
    problem_data = requests.get(problem_api_url, headers=headers).json()
    problem_download_url = problem_data['download_url']
    # Download the CSV from download_url
    with requests.Session() as s:
        download = s.get(problem_download_url)

    decoded_content = download.content.decode('ascii', 'ignore')

    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    problem_responses = list(cr)
    """
    Building on quickstart template to try to write to Google Sheets.

    Creates a Sheets API service object and writes learner profile
    information to Master Sheet. To open Master sheet go to:
    https://docs.google.com/spreadsheets/d/<spreasheetId>/edit
    plugging in value of <spreadsheetId> below.
    """
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1uMAyKZYtoVLzqpknBxOGbkLjR7-AMqlEEowdFqSc3pw'
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


if __name__ == '__main__':
    credentials = get_credentials.get_credentials()
    write_to_sheet()
