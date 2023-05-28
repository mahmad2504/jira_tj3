from requests.auth import HTTPBasicAuth
from termcolor import colored
import subprocess
import requests
import urllib3
import json
import os
from Jira import Jira
from Structure import Structure,Row
from Schedule import Schedule

start_constraint_field="customfield_11642"


#project_id=12397

j=Jira(fields=["summary","assignee","status","timespent","timetracking","issuelinks","description",start_constraint_field])
s=Structure(j)
s.Get('tst_jira_structure')
#s.CreateMemoUnder(0,'test','test-html')
#s.Get("Spencer SOW 10622")
#s.Get("Renesas RZ/A1H StarterKit BSP")
#s.Get("NGC SOW-5002 Phase II & III")
s.Get('tst_jira_structure')

tree=s.Populate()
sched=Schedule(tree,start_constraint_field)
sched.Generate()


