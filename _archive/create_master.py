#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Program: Create Master
Programmer: Michael Fryar, Training Analytics Associate, EPoD
Date created: February 16, 2018

Purpose: Create a master file of engagement data and append previous enagement
records to this file. Going forward, new data will be appended to this file.
"""

# Standard library imports
import csv         # For reading data in comma separated value format
import os          # For manipulating paths and changing directory
from os import walk             # For getting list of existing files
from datetime import datetime   # For timestamping csv files


def create_master(course):
    """Creates a master file and appends previously downloaded data.

    Args:
        course (str): Three letter course code. Known values are:
            AGG - Aggregating Evidence
            COM - Commissioning Evidence
            CBA - Cost-Benefit Analysis
            DES - Descriptive Evidence
            IMP - Impact Evaluations
            SYS - Systematic Approaches to Policy Decisions
    """
    # Change to directory where engagment files are saved.
    home_dir = os.path.expanduser('~')
    archive_path = (
        'EPoD/Dropbox (CID)/Training Assessment and Research' +
        '/BCURE Learner Engagement Reports/{}'.format(course)
    )
    archive_dir = os.path.join(home_dir, archive_path)
    os.chdir(archive_dir)

    # Get list of existing files
    for (dirpath, dirnames, filenames) in walk(archive_dir):
        files = [f for f in filenames if not f[0] == '.']
        break

    # Create master file with column headers
    headers = ['user_id', 'username', 'name', 'engagements.problems_attempted',
               'engagements.problems_completed', 'engagements.videos_viewed',
               'engagements.discussion_contributions', 'download_datetime_UTC']
    mastername = '{}_engagement_master.csv'.format(course)
    with open(mastername, 'w', newline='') as masterfile:
        writer = csv.writer(masterfile)
        writer.writerow(headers)

    # Append data from existing files to new master file
    for file in files:
        timestamp = file[15:34].replace('_', ' ').replace('.', ':')
        with open(file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            engagement_data = list(reader)
        with open(mastername, 'a', newline='') as masterfile:
                writer = csv.writer(masterfile)
                for row in engagement_data[1:]:
                    row.append(timestamp)
                    writer.writerow(row)


if __name__ == '__main__':
    courses = ["AGG", "CBA", "COM", "DES", "IMP", "SYS"]
    for course in courses:
        create_master(course)
