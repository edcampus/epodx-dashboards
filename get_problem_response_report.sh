#!/usr/bin/env bash
# Must pass unit abbreviation when calling from command line
# E.g. "./get_problem_response_report.sh IMP"
# 'IMP' becomes $1

# Get ANALYTICS_API_AUTH_TOKEN
source secrets.sh

curl --get \
    --header 'Accept: text/csv' \
    --header 'Authorization: Token '$ANALYTICS_API_AUTH_TOKEN'' \
    http://127.0.0.1:18100/api/v0/learners/ \
    --data-urlencode "course_id=course-v1:epodx+BCURE-$1+2016_v1" \
    > ~/Downloads/$1.csv
