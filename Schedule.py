from termcolor import colored
from datetime import datetime
import subprocess
import os
import json
from lxml import etree
import lxml.html

class Schedule:
    tjp = [] 
    inprogress_priority=1000
    open_priority=800
    resources= {'unknown':{'self':'', 'name': 'unknown', 'key': 'unknown', 'emailAddress': '','displayName': 'unknown','timeZone': 'Asia/Karachi'}}
    tree=None
    task_header=[]
    country_code={
    'Asia/Karachi':'PK',
    'Etc/GMT-5':'PK',
    'Asia/Kolkata':'IN',
    'America/Chicago':'US',
    'Europe/Dublin':'EU',
    'America/Denver':'US',
    'Europe/London':'EU',
    'America/New_York':'US',
    'Europe/Moscow':'EU',
    'Africa/Johannesburg':'AF'
    }
    allissues={}
    def ProcessIssue(self,issue):
    
        s = """<table>
  <tr><th>Event</th><th>Start Date</th><th>End Date</th></tr>
  <tr><td>a</td><td>b</td><td>c</td></tr>
  <tr><td>d</td><td>e</td><td>f</td></tr>
  <tr><td>g</td><td>h</td><td>i</td></tr>
</table>
"""     
        issue.tables={}
        if issue.itemdesc!= None:
            #print(issue.itemdesc)
            #print(etree.HTML(issue.itemdesc))
            if etree.HTML(issue.itemdesc) != None:
                root = etree.HTML(issue.itemdesc).find("body")
                tables=root.findall('.//table')
                
                for table in tables:
                    itable=[]
                    rows=table.findall('.//tr')
                    header=0
                    hdr=[]
                    print("Gggg")
                    for row in rows:
                        headers=row.findall('.//th')
                        
                        if len(hdr) == 0:
                            for cell in headers:
                                hdr.append(cell.text)
                         
                        cells=row.findall('.//td')
                        values=[]
                        for cell in cells:
                            values.append(cell.text)
                            
                        if(len(values)>0):
                            itable.append(values) 
                    print("fff",len(hdr))
                    if len(hdr) > 0 and len(itable)>1: 
                        issue.tables[hdr[0].lower()]=itable
                        
                        #issue.tables.append(itable)
                        
                
                  
                #print(len(tables))
                #for child in root:
                #    for schild in child:
                #        print(etree.tostring(schild, pretty_print=True, method="html"))
                #        data=child.xpath('//tr/td//text()')
                     

                #result = etree.tostring(root, pretty_print=True, method="html")
                #print(result)
        #print(json.loads(issue.data["description"]))
        print(issue.tables)
        if "key" in issue.tables:
            for keyvalue in issue.tables["key"]:
                setattr(issue, keyvalue[0], keyvalue[1])
                #print(keyvalue[0])
                #print(keyvalue[1])
                #issue[keyvalue[0]] = keyvalue[1]
                #print(row)
                
        if "key" in issue.tables:
            print(issue.project_start)
            print(issue.project_end)
        
        if(issue.data != None):
            if(issue.data["assignee"] == None):
                issue.data["assignee"]=self.resources['unknown']
                
            self.resources[issue.data["assignee"]["name"]]=issue.data["assignee"]
        issue.parent=None
        issue.isparent=False
        for sissue in issue.children:
            issue.isparent=True
            self.ProcessIssue(sissue)
            sissue.parent=issue
        
        self.allissues[issue.id]=issue
            
    def __init__(self,tree,start_constraint_field):
        self.id=tree.id
        self.tree=tree
        self.start_constraint_field=start_constraint_field
       
        
        os.makedirs(str(tree.id),exist_ok=True)
    def Generate(self):
         
        head=self.tree.get()
        self.GenerateProjectHeader(head)
        
        self.ProcessIssue(head)
        self.GenerateResourceHeader(self.resources)
        
        self.GenerateTaskHeader(head)
        self.GenerateReportHeader()
        
        self.tjp_file = open(str(self.id)+"/project.tjp", "w")
        
        for line in self.tjp:
            self.tjp_file.write(line) 
            self.tjp_file.write("\n") 
        self.tjp_file.close()
       
        os.system(f'tj3 {str(self.id)}"/project.tjp" -o {str(self.id)}')
        #subprocess.call(["tj3", "project.tjp", "-o" ,"output"])
        
    def GenerateProjectHeader(self,head):
        
        self.tjp.append(f'project your_project_id "{head.itemname}" 2023-05-01 +8m {{')
        self.tjp.append(f'timezone "America/Chicago"')
        self.tjp.append(f'timeformat "%Y-%m-%d"')
        self.tjp.append(f'numberformat "-" "" "," "." 1')
        self.tjp.append(f'currencyformat "(" ")" "," "." 0')
        self.tjp.append(f'currency "USD"')
        self.tjp.append(f'scenario plan "Plan" {{}}')
        self.tjp.append(f'extend task {{ text Jira "Jira"')
        self.tjp.append(f'              text Status "Status"')
        self.tjp.append(f'}}}}')
        
        self.tjp.append(" ")
        return self.tjp
        
    def GenerateResourceHeader(self, resources):
        
        self.tjp.append(f'resource all "Developers" {{')
        
        for resource in resources.values():
            timezone=resource["timeZone"]
            name=resource["name"]
            country_code=self.country_code[timezone]
            code=name+"_"+country_code
            self.tjp.append(f'resource {name} "{code}" {{')
            self.tjp.append(f' limits {{ weeklymax  40h}} }}')
        
        self.tjp.append(" ")
        self.tjp.append(f'}}')
        
        return self.tjp
        
    def GenerateReportHeader(self):
        
        self.tjp.append(f'taskreport monthreporthtml "monthreporthtml" {{')
        self.tjp.append(f'formats html')
        self.tjp.append(f'columns bsi, name, start, end, effort,resources, complete,Jira, Status, priority, monthly')
        self.tjp.append(f'timeformat "%a %Y-%m-%d"')
        self.tjp.append(f'loadunit hours')
        self.tjp.append(f'hideresource @all }}')
        
        
        self.tjp.append(f'resourcereport resourcegraphhtm "resourcehtml" {{')
        self.tjp.append(f'formats html')
        self.tjp.append(f'headline "Resource Allocation Graph"')
        self.tjp.append(f'columns no, name, effort, weekly')
        self.tjp.append(f'loadunit shortauto')
        self.tjp.append(f'hidetask ~(isleaf() & isleaf_())')
        self.tjp.append(f'sorttasks plan.start.up}}')
     
         
        return self.tjp
    
    def GetDependsOn(self,issue):
        
        blockedon={};
        if "issuelinks" in issue:
            for issuelink in issue["issuelinks"]:
                #print(issuelink)
                if issuelink['type']['name'] == 'Dependency':
                    
                    #if "inwardIssue" in issuelink and issuelink['type']['inward']=='blocks':
                    #    print("inward  blocks ",issuelink['inwardIssue']['key'])
                        
                    if "outwardIssue" in issuelink and issuelink['type']['outward']=='depends on':
                        #print("outward depends on",issuelink['outwardIssue']['key'])
                        blockedon[issuelink['outwardIssue']['key']]=issuelink['outwardIssue']['key']
                        
        return blockedon.values()
        
    def GetDependencyTag(self,issue):
        #print(issue["key"])
        dependencies=self.GetDependsOn(issue)
        #if len(dependencies)>0:
        #    print("Depends on")
        
        deli=''
        dependency_tag=''
        for dependency in dependencies:
            #print(dependency)
            
            if dependency in self.allissues:
                i=self.allissues[dependency]
                parent_ids=self.GetParents(i);
                for parent_id in parent_ids:
                    dependency_tag=dependency_tag+deli+str(parent_id)
                    deli='.'
                    
                dependency_tag=dependency_tag+deli+str(dependency)
                dependency_tag=dependency_tag.replace("-","_")
                #print(dependency_tag)
            else:
                print(colored(f'dependency {dependency} for {issue["key"]}  not part of structure','red'))
            #print(dependency)
            #print(parent_ids)
        return dependency_tag
                
    def GetParents(self, issue):
        parent_ids=[]
        parent=issue.parent
        while parent != None:
            parent_ids.append(parent.id)
            parent=parent.parent
        parent_ids = parent_ids[::-1] #reversing using list slicing
        return parent_ids
        
    def GenerateTaskHeader(self,issue):
        spaces=""
      
        for x in range(int(issue.level)):
            spaces=spaces+"    "
            
        summary=issue.itemname
        key=issue.id    
        if issue.data != None:
            summary=issue.data["summary"]
            key=issue.data["key"]
        
        
        nkey=key.replace("-","_")
        print(isinstance(nkey, int))
        
        nsummary=summary.replace("$","_")
        nsummary=nsummary.replace('"',"_")
        if issue.data == None:   
            self.tjp.append(f'{spaces}task {nkey} "{summary}" {{')
        else:
            dependency_tag=self.GetDependencyTag(issue.data)
            estimate=0
            remainingestimate=0
            timespent=0
            
            #if "originalEstimateSeconds" in issue.data["timetracking"]:
            #    estimate=issue.data["timetracking"]["originalEstimateSeconds"]
            if "remainingEstimateSeconds" in issue.data["timetracking"]:
                remainingestimate=issue.data["timetracking"]["remainingEstimateSeconds"]
           
            if issue.data["timespent"] != None:
                timespent=issue.data["timespent"]
            
            estimate=remainingestimate+timespent
            progress=0
            if timespent>0:
                progress=estimate/timespent*100
                
            remainingestimate=remainingestimate/60
            if remainingestimate < 60:
                remainingestimate=60
            
            
            #summary=issue.data["summary"]
            status=issue.data["status"]["name"]
            statuscategory=issue.data["status"]["statusCategory"]["name"]
            
            #print(nkey,estimate,timespent,status,statuscategory,estimate,remainingestimate,timespent)
            self.tjp.append(f'{spaces}task {nkey} "{nsummary}" {{')
            self.tjp.append(f'{spaces}    Jira "{key}"')
            self.tjp.append(f'{spaces}    Status "{status}"')
            if(issue.isparent==False):
                
                if statuscategory=='In Progress':
                    self.tjp.append(f'{spaces}    priority {self.inprogress_priority}')
                    self.inprogress_priority=self.inprogress_priority-1
                    
                if statuscategory=='To Do':
                    self.tjp.append(f'{spaces}    priority {self.open_priority}')
                    self.open_priority=self.open_priority-1
                   
                if statuscategory=='Done':
                    self.tjp.append(f'{spaces}    complete 100')
                    self.tjp.append(f'{spaces}    priority 0')
                else:
                    self.tjp.append(f'{spaces}    effort {remainingestimate}min')
                    self.tjp.append(f'{spaces}    complete 0')
                    
                    self.tjp.append(f'{spaces}    allocate {issue.data["assignee"]["name"]}')
            
            if issue.data[self.start_constraint_field] != None:
                start_constraint = datetime.strptime(issue.data[self.start_constraint_field], "%Y-%m-%d")
                #print(start_constraint)
                if start_constraint.date() > datetime.now().date():
                    self.tjp.append(f'{spaces}    start {issue.data[self.start_constraint_field]}')
            
            if dependency_tag != '':
                    self.tjp.append(f'{spaces}    depends {dependency_tag}')          
        for sissue in issue.children:
            self.GenerateTaskHeader(sissue)
        self.tjp.append(f'{spaces}}}')
       