import os 
import json
import argparse

p={
"image_name":"sprint_report",
"commit":"main",
"docker_registry":"harbor.xcr.svcs01eu.prod.eu-central-1.kaas.sws.siemens.com/eps",
"code_repository":"https://github.com/mahmad2504/sprint_report.git"
}

#docker build . --build-arg COMMIT=%commit%  -t %image_name%

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
parser.add_argument('--sprint',   help='sprint name required for generate command')
parser.add_argument('--board',   help='board  required for generate  command')
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
        
commit=p["commit"]         
code_repository=p["code_repository"]
docker_registry=p["docker_registry"]
image_name=p["image_name"]

match args.target:
    case 'build':
        if source_code==0:
            mprint("Source code not available. Unable to run this command",1)
            sys.exit()
        cmd=f'docker   build . --build-arg COMMIT=main --build-arg CODE_REPOSITORY={code_repository} -t {image_name}'
        mprint(cmd)
        os.system(cmd)
    case 'release':
        if source_code==0:
            mprint("Source code not available. Unable to run this command",1)
            sys.exit()
        
        cmd=f'git rev-parse --verify HEAD'
        mprint(cmd)
        commit=os.popen(cmd).read()
        commit=commit.replace("\n","")
        mprint(f"Packaging for commit {commit}",1)
        cmd=f'git show -s --format=%B {commit}'
        mprint(cmd)
        os.system(cmd)
        print(code_repository)
        cmd=f'docker   build . --build-arg COMMIT={commit} --build-arg CODE_REPOSITORY={code_repository} --no-cache -t {image_name}'
        mprint(cmd)
        os.system(cmd)
        
        cmd=f'docker tag {image_name}:latest {docker_registry}/{image_name}:latest'
        mprint(cmd)
        os.system(cmd)
        cmd=f'docker push {docker_registry}/{image_name}:latest'
        os.system(cmd)
        
        cmd=f'python -m PyInstaller app.py --onefile --name sprint_report'
        mprint(cmd)
        os.system(cmd)
        
        p["commit"]=commit
        with open('parameters.json', 'w') as f:
            json.dump(p, f)
            
    case 'info':
        if source_code==0:
            mprint("Source code not available. Unable to run this command",1)
            sys.exit()
        cmd=f'git rev-parse --verify HEAD'
        mprint(cmd)
        commitid=os.popen(cmd).read()
        print(commitid)
        cmd=f'git show -s --format=%B {commitid}'
        mprint(cmd)
        os.system(cmd)
    case 'version':
        if args.dev:
            f = open('parameters.json')
            p = json.load(f)
            print(f'Commit:{commit}')
            cmd=f'git show -s --format=%B {commit}'
            mprint(cmd)
            os.system(cmd)
        else:
            cmd=f'docker run -it --rm -w /src {docker_registry}/{image_name}:latest git rev-parse --verify HEAD'
            mprint(cmd)
            commit=os.popen(cmd).read()
            commit=commit.replace("\n","")
            print(f'Commit:{commit}')
            cmd=f'git show -s --format=%B {commit}'
            mprint(cmd)
            os.system(cmd)
            
    case 'generate':
        if args.sprint and args.board:
            if args.dev:
                if source_code==0:
                    mprint("Source code not available. Unable to run this command",1)
                    sys.exit()
                else:
                    cmd=f'docker run -it --rm -w /app -v {os.getcwd()}:/app {image_name}:latest python3 main.py "{args.sprint}" {args.board}'
                    mprint(cmd)
                    os.system(cmd)
            else:
                cmd=f'docker run -it --rm -w /src  {docker_registry}/{image_name}:latest python3 main.py "{args.sprint}" {args.board}'
                mprint(cmd)
                os.system(cmd)
        else:
            mprint("sprint or boardid  missing",1)


