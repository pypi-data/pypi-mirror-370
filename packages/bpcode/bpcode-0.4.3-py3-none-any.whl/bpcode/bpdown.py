import requests
import argparse
import os
import hashlib
from datetime import datetime
import base64
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
                os.mkdir(path)
                down(path, host)
            else:
                savepath=os.path.join(root, dir)
                with open(savepath, 'wb') as f:
                    f.write(base64.b64decode(requests.post(f"http://{host}:8888/clientgetdirs/"+savepath.replace('\\','/'),timeout=6000).json()["file"]))
                    f.flush()
                    os.fsync(f.fileno())
def main():
    parser = argparse.ArgumentParser(description="命令行参数")
    parser.add_argument('--name', type=str, required=True, help='请输入参数')
    parser.add_argument('--version', type=int, required=True, help='请输入参数')
    parser.add_argument('--password', type=str, required=True, help='请输入参数')
    parser.add_argument('--host', type=str, required=True, help='请输入参数')
    args = parser.parse_args()
    login(args.password, f"http://{args.host}")
    if not os.path.exists(args.name+str(args.version)):
        os.mkdir(args.name+str(args.version))
    root=args.name+str(args.version)
    down(root,args.host)
if __name__ == "__main__":
    main()