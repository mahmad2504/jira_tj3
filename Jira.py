from requests.auth import HTTPBasicAuth
from termcolor import colored
import requests
import urllib3
import json
import os
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
                self.jirauser = settings["jirauser"]
                self.jiratoken = settings["jiratoken"]
                f.close()
        else:
            self.url = jiraurl
            self.jirauser = jirauser
            self.jiratoken = jiratoken
        self.auth = HTTPBasicAuth(self.jirauser, self.jiratoken)
        self.headers = {
              "Accept": "application/json",
              "Content-Type": "application/json",
            }
        self.fields=fields
    
    
                    
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
        