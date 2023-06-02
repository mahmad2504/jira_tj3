from datetime import datetime
from dateutil.relativedelta import relativedelta
import collections
import json
import os
class Worklogs:
    
    def __init__(self,jira,tree):
        min=''
        max=''
        worklogs={}
        if os.path.isfile(f'projects/{str(tree.id)}/worklogs'):
            file = open(f'projects/{str(tree.id)}/worklogs', 'r')
            worklogs=json.load(file)

      
        rows=tree.getrows()  
        for id in rows:
            reload=0
            row=rows[id]
            
            if row.data != None:
                last_updated=row.data["updated"]
                if id in worklogs:
                    if worklogs[id][0]['updated'] != last_updated:
                        reload=1
                else:
                    reload=1
                #print(row.data["key"])
                if(reload):
                    #print(f'Reading worklog for {row.data["key"]}')
                    wlgs=jira.Worklogs(id)
                    worklogs[id]=[]
                    worklogs[id].append({"id":id,"key":row.data['key'],"author":"","timeSpentSeconds":0,'started':'','updated':last_updated})
       
                    for wlg in wlgs:
                        worklogs[id].append({"id":id,"key":row.data['key'],"author":wlg['author']['name'],"timeSpentSeconds":wlg['timeSpentSeconds'],'started':wlg['started'].split("T")[0]})
            if row.data != None:
                row.worklogs={}
                for worklog in worklogs[id]:
                    if worklog['started'] != '':
                        started=datetime.strptime(worklog['started'], '%Y-%m-%d')
                        
                        if(min==''):
                            min=started
                        if(max==''):
                            max=started
                        if(started<min):
                            min=started
                        if(started>max):
                            max=started
                            
                        label=started.strftime("%Y-%m")
                        if label in row.worklogs:
                            row.worklogs[label]=row.worklogs[label]+worklog['timeSpentSeconds']/(60*60)
                        else:
                            row.worklogs[label]=worklog['timeSpentSeconds']/(60*60)
                
                #row.data['worklogs']=worklogs[id]
         
        labels=[]
        labels.append(min.strftime("%Y-%m"))
        while min<max:
            min=min+relativedelta(months=1)
            if(min<max):
                labels.append(min.strftime("%Y-%m"))
            else:
                labels.append(max.strftime("%Y-%m"))
         
        for id in rows:
            row=rows[id]
            if row.data != None:
                for label in labels:
                    if label in row.worklogs:
                        #print(row.worklogs[label])
                        pass
                    else:
                        row.worklogs[label]=0
                row.worklogs = dict(sorted(row.worklogs.items()))
             
            
        file = open(f'projects/{str(tree.id)}/worklogs', 'w+')
        json.dump(worklogs, file)
        
        self.worklogs=worklogs
    def Get(self):
        return self.worklogs
        
        