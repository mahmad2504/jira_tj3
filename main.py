from requests.auth import HTTPBasicAuth
from termcolor import colored
from datetime import datetime
import subprocess
import requests
import urllib3
import json
import os
import sys
from Jira import Jira
from Structure import Structure,Row
from Schedule import Schedule
import pickle
from Worklogs import Worklogs
from Report import Report

start_constraint_field="customfield_11642"

if len(sys.argv)!=2:
    print(colored("The syntax of the command is incorrect", 'red'))
    print('(jira_tj3 "structure name")')
    exit()
    
#project_id=12397

structure_name=sys.argv[1]

j=Jira(fields=["summary","assignee","status","timespent","timetracking","issuelinks","description","updated",start_constraint_field],jiraurl="https://jira.alm.mentorg.com",jirauser="aGltcA==",jiratoken="aG1pcA==")
s=Structure(j)

s.Get(structure_name)
tree=s.Populate()

Worklogs(j,tree).Get()

sched=Schedule(tree,start_constraint_field)
sched.Generate()


report=Report(tree)

exit()
#print(rows(

    
#s.CreateMemoUnder(0,'test','test-html')
#s.Get("Spencer SOW 10622")
#s.Get("Renesas RZ/A1H StarterKit BSP")
#s.Get("NGC SOW-5002 Phase II & III")
#s.Get('tst_jira_structure')


wlg_data=[]
if os.path.isfile(f'projects/{str(tree.id)}/worklogs'):
    file = open(f'projects/{str(tree.id)}/worklogs', 'r')
    wlg_data=json.load(file)


ids_to_update=[]
for id in rows:
    if rows[id].data != None:
        if id in wlg_data:
            wlgs=wlg_data[id]
            wlg=wlgs[0]
            #print(wlg)
            if(rows[id].data['updated'] != wlg["updated"]):
               ids_to_update.append(id)
            #print(rows[id].data['updated'])
        else:
            ids_to_update.append(id)
            
print(ids_to_update)
worklogs={}
for id in ids_to_update:
    if rows[id].data != None:
        wlg_data[id]=[]
        wlgs=j.Worklogs(id)
        for wlg in wlgs:
            worklogs[id].append({"id":id,"key":rows[id].data['key'],"author":wlg['author']['name'],"timeSpentSeconds":wlg['timeSpentSeconds'],'started':wlg['started'].split("T")[0],'updated':rows[id].data['updated']})
       

file = open(f'projects/{str(tree.id)}/worklogs', 'w+')
json.dump(wlg_data, file)


#rows=tree.getrows()
#print(rows['325713'].data['timetracking'])

#wlgs=j.Worklogs(325713)
#for wlg in wlgs:
#    print(wlg['author']['name'])
#    print(wlg['timeSpentSeconds'])
#    print(wlg['started'].split("T")[0])
    #print(wlg)
#for id in rows:
#    if rows[id].data != None:
#        print(id, rows[id].data['key'])


#SaveTree(tree)
#sched=Schedule(tree,start_constraint_field)
#sched.Generate()


