from django.shortcuts import render
import os
from django.conf import settings
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import hashlib
import json
import base64
global livetime
livetime = {}
home = Path.home()
env_path = home / '.env'
print(env_path)
jsoncheckpath = os.path.join(settings.MEDIA_ROOT,"version.json")
if not os.path.exists(jsoncheckpath):
    with open(jsoncheckpath,"w",encoding="utf-8") as g:
        json.dump({},g,ensure_ascii=False)
load_dotenv(env_path)
def file_hash(path, algo='sha256', bufsize=1<<20):
    h = hashlib.new(algo)
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(bufsize), b''):
            h.update(chunk)
    return h.hexdigest()
# Create your views here.
def index(request):
    return render(request=request,template_name="index.html")

def check_acess(token):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d--%H%M")
    last = timestamp[-1]
    passwd = os.getenv("BPCODE")
    if passwd is None:
        passwd = "12345678"
    timestamps=[]
    for i in [-1,0,1]:
        timestamps.append(hashlib.sha256((timestamp[:-1] + str(int(last)+i)+passwd).encode()).hexdigest())
    if token in timestamps:
        return True
    else:
        return False

@csrf_exempt
def login(request):
    token=request.POST.get("token")
    timestamp = datetime.utcnow().strftime("%Y-%m-%d--%H%M")
    last = timestamp[-1]
    passwd = os.getenv("BPCODE")
    if passwd is None:
        passwd = "12345678"
    timestamps=[]
    for i in [-1,0,1]:
        timestamps.append(hashlib.sha256((timestamp[:-1] + str(int(last)+i)+passwd).encode("utf-8")).hexdigest())
    if token in timestamps:
        return JsonResponse({"allow":True})
    else:
        return JsonResponse({"allow":False})
    
@csrf_exempt
def basedir(request):
    token=request.POST.get("token")
    if check_acess(token):
        folder_path=request.POST.get("dirs")
        save_path = os.path.join(os.getenv("BPATH"), folder_path)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        return JsonResponse({"sucess":True})
    else:
        return JsonResponse({"sucess":False})
@csrf_exempt 
def hashCheck(request):
    token=request.POST.get("token")
    if check_acess(token):
        filelist=json.loads(request.POST.get("data"))
        currentdir = request.POST.get("currentdir")
        save_path = os.path.join(os.getenv("BPATH"),currentdir)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        files=os.listdir(save_path)
        hashfiledict = {}
        for file in files:
            if os.path.isfile(file):
                hashfiledict[file]=file_hash(os.path.join(currentdir, file))
        namelist=[]
        for name,hashname in filelist.items():
            if hashfiledict.get(name,"") != hashname:
                namelist.append(name)
        return JsonResponse({"namelist":namelist})
    else:
        return JsonResponse({"namelist":[]})

@csrf_exempt
def dirs(request):
    token = request.POST.get("token")
    if check_acess(token):
        dirs=eval(request.POST.get("dirs"))
        currentdir = request.POST.get("currentdir")
        save_path = os.path.join(os.getenv("BPATH"),currentdir)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        if dirs:
            for dir in dirs:
                newdir=os.path.join(save_path,dir)
                if not os.path.exists(newdir):
                    os.makedirs(newdir)
            return JsonResponse({"sucess":True})
        else:
            return JsonResponse({"sucess":True})
    else:
        return JsonResponse({"sucess":False})

@csrf_exempt
def uploadfile(request):
    currentdir = request.POST.get("currentdir")
    save_path=os.path.join(os.getenv("BPATH"),currentdir)
    file = request.FILES["file"]
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    filepath=os.path.join(save_path,file.name)
    with open(filepath,"wb") as f:
        for chunk in file.chunks():
            f.write(chunk)
    return JsonResponse({"message":"ok"})

@csrf_exempt
def checkversion(request):
    basedirs= request.POST.get("basedir")
    timestamp=request.POST.get("timestamp")
    jsonpath=os.path.join(settings.MEDIA_ROOT,"version.json")
    with open(jsonpath,"r",encoding="utf-8") as f:
        versionlist=json.load(f)
    version = versionlist.get(basedirs,None)
    if version is None:
        versionlist[basedirs]={"name":basedirs,"version":1,"timestamp":timestamp}
        with open(jsonpath,"w") as f:
            json.dump(versionlist,f,ensure_ascii=False)
        return JsonResponse({"version":1})
    else:
        oldtimestamp=version.get("timestamp")
        versions = version.get("version")
        if oldtimestamp == timestamp:
            return JsonResponse({"version":versions})
        else:
            versions+=1
            version["timestamp"]=timestamp
            version["version"]=versions
            versionlist[basedirs]=version
            with open(jsonpath,"w") as f:
                json.dump(versionlist,f,ensure_ascii=False)
            return JsonResponse({"version":versions})
@csrf_exempt
def weblogin(request):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"message": "invalid json"}, status=400)

        token = data.get("password")
        passwd = os.getenv("BPCODE") or "12345678"
        if token == passwd:
            return JsonResponse({"success": True, "cookie": hashlib.sha256((timestamp).encode("utf-8")).hexdigest()})
        else:
            return JsonResponse({"message": "error"}, status=401)

    return JsonResponse({"message": "method not allowed"}, status=405)

@csrf_exempt
def webensure(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"message": "invalid json"}, status=400)
    cookie = data.get("cookie")
    if cookie:
        if cookie == hashlib.sha256((datetime.utcnow().strftime("%Y-%m-%d")).encode("utf-8")).hexdigest():
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False})
    else:
        return JsonResponse({"success": False})

@csrf_exempt
def getdirs(request, path=""):
    # 如果path为空字符串，则为根目录
    
    dir_path = os.path.join(os.getenv("BPATH"), path)
    if not os.path.exists(dir_path):
        return JsonResponse({"dirs": {"nodirs":True}}, status=404)
    if os.path.isdir(dir_path):
        dirs = {d: True if os.path.isdir(os.path.join(dir_path, d)) else False for d in os.listdir(dir_path)}
        return JsonResponse({"dirs": dirs, "isdir": True}, status=200)
    else:
        with open(dir_path, 'r',encoding="utf-8") as f:
            content = f.read()
            return JsonResponse({"file":content,"isdir":False}, status=200)


@csrf_exempt
def clientgetdirs(request, path=""):
    # 如果path为空字符串，则为根目录
    
    dir_path = os.path.join(os.getenv("BPATH"), path)
    if not os.path.exists(dir_path):
        return JsonResponse({"dirs": {"nodirs":True}}, status=404)
    if os.path.isdir(dir_path):
        dirs = {d: True if os.path.isdir(os.path.join(dir_path, d)) else False for d in os.listdir(dir_path)}
        return JsonResponse({"dirs": dirs, "isdir": True}, status=200)
    else:
        with open(dir_path, 'rb') as f:
            content = f.read()
            return JsonResponse({"file":base64.b64encode(content).decode("utf-8"),"isdir":False}, status=200)

@csrf_exempt
def ping(request):
    return JsonResponse({"status":True})

@csrf_exempt
def projectlist(request):
    if request.method == 'GET':
        global livetime
        livetime["time"] = datetime.utcnow()
        jsonpath=os.path.join(settings.MEDIA_ROOT,"version.json")
        with open(jsonpath,"r",encoding="utf-8") as f:
            versionlist=json.load(f)
        return JsonResponse({"projects": versionlist})
    
@csrf_exempt
def islive(request):
    global livetime
    if livetime.get("time"):
        # 返回当前时间
        nowtime = datetime.utcnow()
        if (nowtime - livetime["time"]).total_seconds() < 65:
            return JsonResponse({"status": True})
        return JsonResponse({"status": False})
    else:
        return JsonResponse({"status": False})