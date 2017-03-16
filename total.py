#!/usr/bin/env python
import signal
import sys
import argparse
import logging
import os
import requests
import time
import pytz
from dateutil import parser
from datetime import datetime, timedelta

import json

from time import gmtime, strftime
import datetime
import calendar
import dateutil.parser
from dateutil.parser import parse

utc = pytz.UTC

# Script config
BASE_URL = 'https://review-api.udacity.com/api/v1'
CERTS_URL = '{}/me/certifications.json'.format(BASE_URL)
ME_URL = '{}/me'.format(BASE_URL)
ME_REQUEST_URL = '{}/me/submission_requests.json'.format(BASE_URL)
CREATE_REQUEST_URL = '{}/submission_requests.json'.format(BASE_URL)
DELETE_URL_TMPL = '{}/submission_requests/{}.json'
GET_REQUEST_URL_TMPL = '{}/submission_requests/{}.json'
PUT_REQUEST_URL_TMPL = '{}/submission_requests/{}.json'
REFRESH_URL_TMPL = '{}/submission_requests/{}/refresh.json'
ASSIGNED_COUNT_URL = '{}/me/submissions/assigned_count.json'.format(BASE_URL)
ASSIGNED_URL = '{}/me/submissions/assigned.json'.format(BASE_URL)

REVIEW_URL = 'https://review.udacity.com/#!/submissions/{sid}'
REQUESTS_PER_SECOND = 1 # Please leave this alone.

WAIT_URL = '{}/submission_requests/{}/waits.json'
SUBMITED_URL= '{}/me/submissions/completed'.format(BASE_URL)

# Get a list of contacts
project = {}


logging.basicConfig(format='|%(asctime)s| %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

headers = None

def request_reviews(token):
    global headers
    headers = {'Authorization': token, 'Content-Length': '0'}
    
    year = input("What year? ")
    month = input("What month? (Input 0 if you want for the whole year)")
    
    now = datetime.datetime.now()
    # year = now.year
    # month = now.month
    if month == 0:    
        lastdayofmonth = calendar.monthrange(year,12)[1]
        start_date = datetime.datetime(year, 1, 1, 00, 00, 00, 000001).isoformat()    
        end_date = datetime.datetime(year, 12, lastdayofmonth, 23, 59, 59, 999999).isoformat()        
        params = {'start_date':start_date,'end_date':end_date}
    else:
        lastdayofmonth = calendar.monthrange(year,month)[1]
        start_date = datetime.datetime(year, month, 1, 00, 00, 00, 000001).isoformat()    
        end_date = datetime.datetime(year, month, lastdayofmonth, 23, 59, 59, 999999).isoformat()        
        params = {'start_date':start_date,'end_date':end_date}
    
    me_req_resp = requests.get(SUBMITED_URL, headers=headers,params=params)
    me_req_resp.raise_for_status()
    subs = me_req_resp.json()
    ###

    ###
    total=0
    projectsTotal={}
    projectsTime={}
    
    for p in subs:
        projectsTotal[p["project"]["name"]] = 0
        projectsTime[p["project"]["name"]] = 0

    for p in subs:
        total = total + float(p["price"])
        projectsTotal[p["project"]["name"]] += 1
        time = (parse(p["completed_at"]) - parse(p["assigned_at"])).total_seconds()/3600
        
        projectsTime[p["project"]["name"]] += time
    print("--------------")
    print("Total Projects:")
    print("--------------")
    allprojects = 0        
    for key,value in projectsTotal.iteritems():    
        allprojects += value
        print(key + " : "+ str(value))
    
    print("Total: " + str(allprojects))
        
    alltimes = 0
    totalTime = 0
    for key,value in projectsTime.iteritems():    
        alltimes += value/projectsTotal[key]
        totalTime += value 
        print(key + " : "+ str(value/projectsTotal[key]))
        
    # print("--------------")
    # print("Total Average Time:")
    # print("--------------")
    # print(str(alltimes) + " Hours")

    if month == 0:
        print("--------------")
        print("Total Time/Project:")
        print("--------------")
        print(str(totalTime/allprojects) + " hours/project")

        print("--------------")
        print("Total Time:")
        print("--------------")
        print(str(totalTime) + " Hours")

                
    print("--------------")
    if month == 0:
        print("Total Earnings" + " Year: " + str(year))
    else:    
        print("Total Earnings(" + datetime.date(1900, month, 1).strftime('%B') + ")")
    print("--------------")
    print(str(total) + "$")
    
def day(start,end,token):
    headers = {'Authorization': token, 'Content-Length': '0'}
    params = {'start_date':start,'end_date':end}
    me_req_resp = requests.get(SUBMITED_URL, headers=headers,params=params)
    me_req_resp.raise_for_status()
    subs = me_req_resp.json()
    total = 0
    for p in subs:
        total = total + float(p["price"])
    return total    

def perDay(token):
    now = datetime.datetime.now()
    year = now.year
    month = now.month    
    lastdayofmonth = calendar.monthrange(year,month)[1]    
    for d in range(1,lastdayofmonth+1):
        start = datetime.datetime(year, month, d, 00, 00, 00, 000001).isoformat()
        end = datetime.datetime(year, month, d, 23, 59, 59, 999999).isoformat()
        print(d,day(start,end,token))
            


if __name__ == "__main__":
    cmd_parser = argparse.ArgumentParser(description =
	"Reviews Statistics (total, average times)"
    )
    cmd_parser.add_argument('--auth-token', '-T', dest='token',
	metavar='TOKEN', type=str,
	action='store', default=os.environ.get('UDACITY_AUTH_TOKEN'),
	help="""
	    Your Udacity auth token. To obtain, login to review.udacity.com, open the Javascript console, and copy the output of `JSON.parse(localStorage.currentUser).token`.  This can also be stored in the environment variable UDACITY_AUTH_TOKEN.
	"""
    )
    cmd_parser.add_argument('--debug', '-d', action='store_true', help='Turn on debug statements.')
    args = cmd_parser.parse_args()

    if not args.token:
        cmd_parser.print_help()
        cmd_parser.exit()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    request_reviews(args.token)

