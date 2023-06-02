import os 
import json
import argparse

p={
"image_name":"jira_tj3",
"branch":"main",
"docker_registry":"harbor.xcr.svcs01eu.prod.eu-central-1.kaas.sws.siemens.com/eps",
"code_repository":"https://github.com/mahmad2504/jira_tj3.git"
}


try:
    f = open('parameters.json')
    p = json.load(f)
except:
    with open('parameters.json', 'w') as f:
        json.dump(p, f)


# Construct the argument parser and parse the arguments
arg_desc = '''\
        This program Generates Sprint Reports!
        --------------------------------
        
        '''
        
parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,description= arg_desc)
parser.add_argument('target',   help='build, release, generate, info, version')
parser.add_argument('--structure',   help='structure name required for generate command')
parser.add_argument('--verbose',   action='store_true', help='')
parser.add_argument('--dev',   action='store_true', help='')


args = parser.parse_args()


def mprint(message,force=0):
    if force:
         print(message)
    else:
        if args.verbose: 
            print(message)

source_code=0
if os.path.isfile("Dockerfile"):
   source_code=1
        
branch=p["branch"]         
code_repository=p["code_repository"]
docker_registry=p["docker_registry"]
image_name=p["image_name"]

if args.target=='build':
        if source_code==0:
            mprint("Source code not available. Unable to run this command",1)
            sys.exit()
            
        cmd=f'git rev-parse --verify HEAD'
        mprint(cmd)
        commit=os.popen(cmd).read()
        commit=commit.replace("\n","")
        
        cmd=f'git rev-parse --abbrev-ref HEAD'
        mprint(cmd)
        branch=os.popen(cmd).read()
        branch=branch.replace("\n","")
       
        mprint(f"Packaging for branch {branch} and commit {commit}",1)
        cmd=f'git show -s --format=%B {commit}'
        mprint(cmd)
        os.system(cmd)
        
        cmd=f'docker   build . --build-arg COMMIT={commit} --build-arg BRANCH={branch}  --build-arg CODE_REPOSITORY={code_repository} -t {image_name}'
        mprint(cmd)
        os.system(cmd)
if args.target=='release':
        if source_code==0:
            mprint("Source code not available. Unable to run this command",1)
            sys.exit()
        
        cmd=f'git rev-parse --verify HEAD'
        mprint(cmd)
        commit=os.popen(cmd).read()
        commit=commit.replace("\n","")
        
        cmd=f'git rev-parse --abbrev-ref HEAD'
        mprint(cmd)
        branch=os.popen(cmd).read()
        branch=branch.replace("\n","")
       
        mprint(f"Packaging for branch {branch} and commit {commit}",1)
        cmd=f'git show -s --format=%B {commit}'
        mprint(cmd)
        os.system(cmd)
       
        cmd=f'docker   build . --build-arg COMMIT={commit} --build-arg BRANCH={branch} --build-arg CODE_REPOSITORY={code_repository} --no-cache -t {image_name}'
        mprint(cmd)
        os.system(cmd)
        
        cmd=f'docker tag {image_name}:latest {docker_registry}/{image_name}:latest'
        mprint(cmd)
        os.system(cmd)
        cmd=f'docker push {docker_registry}/{image_name}:latest'
        os.system(cmd)
        
        #cmd=f'python -m PyInstaller app.py --onefile --name jira_tj3'
        #mprint(cmd)
        #os.system(cmd)
        
        p["commit"]=commit
        p["branch"]=branch
        with open('parameters.json', 'w') as f:
            json.dump(p, f)
           
if args.target=='version':
        if args.dev:
            if source_code==0:
                mprint("Source code not available. Unable to run this command",1)
                sys.exit()
            cmd1=f'docker run -it --rm -w /app -v {os.getcwd()}:/app {image_name}:latest git rev-parse --verify HEAD'
            cmd2=f'docker run -it --rm -w /app -v {os.getcwd()}:/app {image_name}:latest git rev-parse --abbrev-ref HEAD'
        else:
            cmd1=f'docker run -it --rm -w /src  {docker_registry}/{image_name}:latest git rev-parse --verify HEAD'
            cmd2=f'docker run -it --rm -w /src -v {os.getcwd()}:/app {image_name}:latest git rev-parse --abbrev-ref HEAD'
            
        mprint(cmd1)
        commit=os.popen(cmd1).read()
        commit=commit.replace("\n","")
        print(f'Commit:{commit}')
        
        mprint(cmd2)
        branch=os.popen(cmd2).read()
        branch=branch.replace("\n","")
        print(f'Branch:{branch}')
            
if args.target=='generate':
        if args.structure:
            if args.dev:
                if source_code==0:
                    mprint("Source code not available. Unable to run this command",1)
                    sys.exit()
                else:
                    cmd=f'docker run -it --rm -w /app -v {os.getcwd()}:/app -v {os.getcwd()}/projects:/projects {image_name}:latest  python3 main.py "{args.structure}"'
                    mprint(cmd)
                    os.system(cmd)
            else:
                cmd=f'docker run -it --rm -w /src  -v {os.getcwd()}/projects:/projects {docker_registry}/{image_name}:latest python3 main.py "{args.structure}"'
                mprint(cmd)
                os.system(cmd)
        else:
            mprint("structure name is missing ",1)
if args.target=='terminal':
        if args.dev:
            if source_code==0:
                mprint("Source code not available. Unable to run this command",1)
                sys.exit()
            else:
                cmd=f'docker run -it --rm -w /app -v {os.getcwd()}:/app -v {os.getcwd()}/projects:/projects {image_name}:latest sh'
        else:
            cmd=f'docker run -it --rm -w /src  -v {os.getcwd()}/projects:/projects {docker_registry}/{image_name}:latest sh'
        mprint(cmd)
        os.system(cmd)
       

