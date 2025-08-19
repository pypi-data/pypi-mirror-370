import requests
import os
import hashlib
from datetime import datetime
import base64
from dotenv import load_dotenv
from pathlib import Path
import time
import json
home = Path.home()
envpath = os.path.join(home,".env")#确认已经配置环境变量
load_dotenv(envpath)
jsoncheckpath = os.path.join(os.getenv("BPATH"), "project.json")
if not os.path.exists(jsoncheckpath):
    with open(jsoncheckpath,"w",encoding="utf-8") as g:
        json.dump({},g,ensure_ascii=False)
def login(passwd,weburl):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d--%H%M")
    acesstoken=timestamp+passwd
    url=weburl+":8888/login/"
    try:
        response=requests.post(url,data={"token":hashlib.sha256(acesstoken.encode('utf-8')).hexdigest()}).json()
    except:
        raise ValueError("passwd or url is wrong")
    if response["allow"]:
        return True
    else:
        raise ValueError("passwd is wrong")
def getfilelist(host, dir):
    filelist=requests.post(f"http://{host}:8888/clientgetdirs/"+dir.replace('\\','/')).json()
    return filelist
def down(root,host):
    dirs = getfilelist(host, root)
    if dirs['isdir']:
        for dir,isdir in list(dirs['dirs'].items()):
            if isdir:
                path=os.path.join(root, dir)
                print(path)
                rroot = os.path.join(os.getenv("BPATH"), root,dir)
                os.mkdir(rroot)
                down(path, host)
            else:
                nroot = os.path.join(os.getenv("BPATH"), root, dir)
                savepath=os.path.join(root, dir)
                with open(nroot, 'wb') as f:
                    f.write(base64.b64decode(requests.post(f"http://{host}:8888/clientgetdirs/"+savepath.replace('\\','/'),timeout=6000).json()["file"]))
                    f.flush()
                    os.fsync(f.fileno())

def searchserver(weburl):
    url=weburl+":8888/ping/"
    try:
        response=requests.get(url).json()
    except:
        response={"status":False}
    return response["status"]

def write_log(message):
    with open(os.path.join(os.getenv("BPATH"), "bpnas_log.txt"), "a",encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {message}\n")

def get_projectlist(host):
    url = f"http://{host}:8888/projectlist/"
    try:
        response = requests.get(url).json()
    except:
        response = None
    return response

def create_index(project,name,version,timestamp):
    jsonpath = os.path.join(os.getenv("BPATH"), "project.json")
    if not os.path.exists(jsonpath):
        with open(jsonpath, "w",encoding="utf-8") as f:
            json.dump({}, f,ensure_ascii=False)
    else:
        with open(jsonpath,"r",encoding="utf-8") as g:
            versionlist=json.load(g)
        versionlist[project]={"name":name,"version":version,"timestamp":timestamp}
        with open(jsonpath,"w",encoding="utf-8") as f:
            json.dump(versionlist,f,ensure_ascii=False)
    return True

def readjson():
    jsonpath = os.path.join(os.getenv("BPATH"), "project.json")
    with open(jsonpath,"r",encoding="utf-8") as g:
        versionlist=json.load(g)
    return versionlist

def main():
    host = os.getenv("BPHOST")
    if not os.path.exists(os.getenv("BPATH")):
        write_log("路径不存在")
        return
    if not searchserver(f"http://{host}"):
        write_log("服务器连接失败")
        return
    login(os.getenv("BPCODE"), f"http://{host}")
    while True:
        projectlist = get_projectlist(host)
        if projectlist is None:
            write_log("获取项目列表失败")
            break
        projects = projectlist["projects"]
        localjson = readjson()
        for project,projectdir in projects.items():
            name = projectdir["name"]
            version = projectdir["version"]
            timestamp = projectdir["timestamp"]
            localdict = localjson.get(project, {})
            if localdict.get("version") == version and localdict.get("timestamp") == timestamp and name == localdict.get("name"):
                continue
            if not os.path.exists(os.path.join(os.getenv("BPATH"), name+str(version))):
                os.mkdir(os.path.join(os.getenv("BPATH"), name+str(version)))
            localversion = localdict.get("version", 1)
            for v in range(localversion,version+1):
                down(name+str(v), host)
            create_index(project,name,version,timestamp)
        time.sleep(60)

if __name__ == "__main__":
    main()