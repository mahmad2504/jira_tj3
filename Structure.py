from requests.auth import HTTPBasicAuth
from termcolor import colored
import requests
import urllib3
import json
import os
from Tree import Tree,Row

class Structure:
    def __init__(self,jira):
        self.headers = {
              "Accept": "application/json",
              "Content-Type": "application/json",
            }
        self.jira=jira
        
    def Get(self,name):
        try:
            int(name)
            url = self.jira.url+"/rest/structure/2.0/structure/"+str(name)
        except:
            url = self.jira.url+"/rest/structure/2.0/structure?name="+str(name)
        #print(url)
        response = requests.request(
            "GET",
            url,
            headers=self.headers,
            auth=self.jira.auth,
            verify=False
        )
        response=json.loads(response.text)
        
        if "structures" in response:
            if len(response["structures"])==0:
                return None
            else:
                self.name=response["structures"][0]["name"]
                self.id=response["structures"][0]["id"]
                self.description=response["structures"][0]["description"]
                self.isArchived=response["structures"][0]["isArchived"]
                return response["structures"][0]
        else:
            self.name=response["name"]
            self.id=response["id"]
            self.description=response["description"]
            self.isArchived=response["isArchived"]
            return response
            
    def Populate(self):
        
        url = self.jira.url+'/rest/structure/2.0/forest/latest?s={"structureId":'+str(self.id)+'}'
        response = requests.request(
            "GET",
            url,
            headers=self.headers,
            auth=self.jira.auth,
            verify=False
        )
        forest=json.loads(response.text)
        #print(forest)
        items=forest["formula"].split(",")
        itemTypes=forest["itemTypes"]
        
        query="issue in ("
        deli=""
        #tree={}
        tree=Tree(self)
        
        for item in items:
            if item=='':
                break;
            
            parts=item.split(":")
            rowid = parts[0]
      
            level = parts[1]
            taskid=parts[2].split("/")
            
            if(len(taskid))==2:
                #print(item)
                itemtype=itemTypes[taskid[0]]   
                taskid="_"+taskid[1]
                response=self.__GetAttributeValues(rowid)
                
                itemname=response[0]['values'][0]
                itemdesc=response[1]['values'][0]
                
            else:
                itemtype='jira.issue'
                itemname="jira.issue"
                itemdesc="jira.issue"
                taskid=parts[2]
                query=query+deli+taskid
                deli=","
            row = Row({"rowid":rowid, "level":level, "id":taskid, "issue": None,"itemtype":itemtype,"itemname":itemname,"itemdesc":itemdesc})
            tree.addrow(row)
        query=query+")"
        issues=[]
        if deli!='':
            issues=self.jira.Search(query)
        
        for issue in issues:
            row=tree.getrow(issue["id"])
            
            data=issue['fields']
            data["key"]=issue['key']
            data["id"]=issue['id']
            row.itemname=data['summary']
            row.itemdesc=data['description']
            row.id=issue['key']
            row.data=data
            
           
            
            #tree[issue["id"]].data=issue['fields']
            #tree[issue["id"]].data["key"]=issue['key']
            #tree[issue["id"]].data["id"]=issue['id']
            
        #print(issue["row"])
        return tree;
        
    def __GetAttributeValues(self,rowid,attributes=[{"id": "summary","format": "text"},{"id": "description","format": "html"}]):
        url = self.jira.url+'/rest/structure/2.0/value'
        payload = json.dumps( {
            "requests": [
                {
                  "forestSpec": {
                    "structureId": self.id
                  },
                  "rows": [
                    rowid
                  ],
                  "attributes": attributes
                }
            ]
        } )
        response = requests.request(
            "POST",
            url,
            headers=self.headers,
            data=payload,
            auth=self.jira.auth,
            verify=False
        )
        response=json.loads(response.text)
        return(response["responses"][0]["data"]);
        
    def Create(self,name):
        url = self.jira.url+"/rest/structure/2.0/structure"
        payload = json.dumps( {
            "name":name
        } )
        response = requests.request(
            "POST",
            url,
            headers=self.headers,
            data=payload,
            auth=self.jira.auth,
            verify=False
        )
        return json.loads(response.text)
        
    def CreateIssueUnder(self,under_rowid,in_projectid,summary,timetracking=["10h"],labels=["new_label"]):
        url = self.jira.url+'/rest/structure/2.0/item/create'
        payload = json.dumps( 
        {
          "item": {
              "type": "com.almworks.jira.structure:type-issue",
              "values": {
                "issue": {
                  "summary": summary,
                  
                },
                "pid":in_projectid,
                "issuetype": "3",
                "mode": "new",
              }
            },
          "forest": {
            "spec": {"structureId": self.id},
            "version": {
              "signature": 0,
              "version": 0
            }
          },
          "items": {
            "version": {
              "signature": 0,
              "version": 0
            }
          },
          "rowId": -100,
          "under": under_rowid,
          "parameters": {}
        })
        payload = json.loads(payload)
       
        if( len(labels)>0):
            payload["item"]["values"]["issue"]["labels"]=labels
        if( len(timetracking)>0):
            payload["item"]["values"]["issue"]["timetracking"]=timetracking
       
        payload = json.dumps(payload)
       
        response = requests.request(
            "POST",
            url,
            headers=self.headers,
            data=payload,
            auth=self.jira.auth,
            verify=False
        )
        
        response=json.loads(response.text)
        #print(response)
        return(response["newRowIds"][0])
    def CreateMemoUnder(self,under_rowid,name,description):
        url = self.jira.url+'/rest/structure/2.0/item/create'
        payload = json.dumps( 
            {
              "item": {
                "type": "com.almworks.jira.structure:type-memo",
                "values": { "summary": name,"description":description}
              },
              "forest": {
                "spec": { "structureId": self.id },
                "version": {
                  "signature": 0,
                  "version": 0
                }
              },
              "items": {
                "version": {
                  "signature": 0,
                  "version": 0
                }
              },
              "rowId": -100,
              "under": under_rowid,
              "parameters": {}
            })  
        response = requests.request(
            "POST",
            url,
            headers=self.headers,
            data=payload,
            auth=self.jira.auth,
            verify=False
        )
        response=json.loads(response.text)
        return(response["newRowIds"][0])
    def CreateFolderUnder(self,under_rowid,foldername):
        url = self.jira.url+'/rest/structure/2.0/item/create'
        payload = json.dumps( 
            {
              "item": {
                "type": "com.almworks.jira.structure:type-folder",
                "values": { "summary": foldername }
              },
              "forest": {
                "spec": { "structureId": self.id },
                "version": {
                  "signature": 0,
                  "version": 0
                }
              },
              "items": {
                "version": {
                  "signature": 0,
                  "version": 0
                }
              },
              "rowId": -100,
              "under": under_rowid,
              "parameters": {}
            })  
        response = requests.request(
            "POST",
            url,
            headers=self.headers,
            data=payload,
            auth=self.jira.auth,
            verify=False
        )
        response=json.loads(response.text)
        return(response["newRowIds"][0])

  


