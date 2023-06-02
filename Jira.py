from requests.auth import HTTPBasicAuth
from termcolor import colored
import requests
import urllib3
import json
import os
import base64

class Jira:
    def __init__(self,fields=["summary"],jiraurl=None,jirauser=None,jiratoken=None):
        os.system('color >/dev/null 2>&1')
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 
        if jiraurl==None:   
            file_name='settings.json'
            print(colored('Reading settings from '+file_name, 'yellow'))
            with open(file_name) as f:
                data = f.read()
                settings = json.loads(data)
                self.url = settings["jiraurl"]
                self.jirauser =  self.Decode(settings["jirauser"])
                self.jiratoken = self.Decode(settings["jiratoken"])
                f.close()
        else:
            self.url = jiraurl
            self.jirauser = self.Decode(jirauser)
            self.jiratoken = self.Decode(jiratoken)
        self.auth = HTTPBasicAuth(self.jirauser, self.jiratoken)
        self.headers = {
              "Accept": "application/json",
              "Content-Type": "application/json",
            }
        self.fields=fields
    def Decode(self,base64_message):
        base64_bytes = base64_message.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode('ascii')
        return message
                
    def Encode(self,message):
       
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        return base64_message
    def Worklogs(self,issueIdOrKey):
        
        startAt=0
        maxResults=500
        url = self.url+f"/rest/api/latest/issue/{issueIdOrKey}/worklog?startAt=100"
        #print(url)
        worklogs=[]
        while(1):
            response = requests.request(
                "GET",
                url,
                headers=self.headers,
                params={
                    "issueIdOrKey" : issueIdOrKey,
                    "startAt": startAt,
                    "maxResults": maxResults,
                },
                auth=self.auth,
                verify=False,
                
            )
            
            startAt=startAt+maxResults;
            data=json.loads(response.text)
            #print(data)
            for d in data["worklogs"]:
                worklogs.append(d)
                
            if len(worklogs)==data['total']:
                break
        return worklogs
        
                    
    def Search(self,jql,fields=None):

        if fields==None:
            fields=self.fields
        
        startAt=0
        maxResults=500
        url = self.url+"/rest/api/latest/search"
        issues=[]
        while(1):
            payload = json.dumps( 
                {
                    "jql": jql,
                    "startAt": startAt,
                    "maxResults": maxResults,
                    "fields": fields
                }
            )
            response = requests.request(
                "POST",
                url,
                headers=self.headers,
                data=payload,
                auth=self.auth,
                verify=False
            )
            startAt=startAt+maxResults;
            data=json.loads(response.text)
            #print(data)
            #print(len(data["issues"]))
            for d in data["issues"]:
                issues.append(d)
                
            if len(data["issues"])==0:
                break
                        
        return issues
        