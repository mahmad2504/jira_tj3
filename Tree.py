class Row:
     def __init__(self,row):
        self.id=row["id"]
        self.rowid=row["rowid"]
        self.level=row["level"]
        self.itemtype=row["itemtype"]
        self.itemname=row["itemname"]
        self.itemdesc=row["itemdesc"]
        self.data=None
        
        pass

class Tree():
    head=None
    tree={}
    parents={}
    
    def __init__(self,obj):
        self.id=obj.id
        self.head = Row({"rowid":0, "level":0, "id":"root", "issue": None,"itemtype":'head',"itemname":obj.name,"itemdesc":""})
        self.parents[str(self.head.level)]=self.head
        self.head.children=[]
        self.tree[self.head.id]=self.head
        
    def addrow(self, row):
        
        row.level=int(row.level)+1
        parent_level=row.level-1
        self.parents[str(row.level)]=row
        
        rowparent=self.parents[str(parent_level)]
        #print(rowparent)
     
        #if not hasattr(rowparent, 'children'):
        #   rowparent.children=[]
            
        
        rowparent.children.append(row)
        row.children=[]
        self.tree[row.id]=row
        pass
        
    def getrow(self, id):
       return self.tree[id]
       pass
    def get(self):
        return self.head
        pass
    def getrows(self):
        #print(self.head)
        return self.tree
        

