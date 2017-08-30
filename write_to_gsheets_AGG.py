#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Program: Write to GSheets
Programmer: Michael Fryar, Research Fellow, EPoD
Date created: January 5, 2017

Purpose: Write to Google Sheets via API.
"""
# Note: Must first establish SSH connection to epodx analytics
import csv
import os

import httplib2
import requests
from apiclient import discovery

import get_credentials

# WARNING: Keep your token secret!
with open("hks_secret_token.txt", "r") as myfile:
    hks_secret_token = myfile.read().replace('\n', '')

# Course_id for Aggregating Evidence
course_id = "course-v1:epodx+BCURE-AGG+2016_v1"


def write_to_sheet():
    """Downloads learner data from EPoDx and writes to Google Sheets.

    edX stores identifiable information about learners separately from
    problem response data, which is identifiable by user_id only. This
    function downloads learner data and problem response data via the
    EPoDx API and then writes this data to a Google Sheet.
    """
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
