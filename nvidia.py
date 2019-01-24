#!/user/bin python
# -*- coding: utf-8 -*-
import argparse
import os,stat
import commands
import time
import re
import json
from pynvml import *
import os

def execCmd(info,realCmd,testExec=False):
    print info,">",realCmd
    if testExec != True:
        status,cmt=commands.getstatusoutput(realCmd)
        print status,cmt
        return cmt
    return ""
def fileExists(filepath,type=1):
    if type == 1:
        return os.access(filepath,os.R_OK)
    elif type ==2:
        return os.access(filepath,os.W_OK)
    else:
        return os.access(filepath,os.X_OK)

def isfiles(files):
     return os.path.isfile(files)
def writetofile(filepath,filename,filecontant):
    print "# %s:: write files %s %s start...!" % (writetofile.__name__,filepath,filename)
    if fileExists(filepath,2) == False:
        print "error:: the %s is Not permission" % filepath
        return 1
    files=filepath+filename
    if isfiles(files) and  raw_input("Mandatory coverage[y/n]?") =="y":
        with open(files,'w') as f:
            f.write(filecontant)
        f.close()
    else:
        print "not changed"
    return 0
# pip install pynvml-
def getAddress():
    return "address=bbb"
def getGpu(log=False):
    nvmlInit()
    version=nvmlSystemGetDriverVersion()
    if log ==True:
        print version
    devicecount=nvmlDeviceGetCount()
    tmpstr=""
    for i in range(devicecount):
        handler=nvmlDeviceGetHandleByIndex(i)
        gpuname=nvmlDeviceGetName(handler).replace('-','_')
        if ' ' in gpuname:
            gpuname=gpuname.replace(' ','_')
            gpuname=gpuname.replace('GeForce_GTX_','')
        if log ==True:
            print gpuname
        gpuuuid=nvmlDeviceGetUUID(handler)
        if log==True:
            print gpuuuid[0:11]
        nvidia="NVIDIA_GPU"+gpuname+"="+gpuuuid[0:11]
        if log==True:
            print nvidia
        tmpstr=tmpstr+"\""+nvidia+"\""
        if i<devicecount-1:
            tmpstr=tmpstr+","
    return tmpstr
def getModel():
    str="{\"labels\":[\"%s\"],\"default-runtime\":\"nvidia\",\"storage-driver\":\
    \"devicemapper\",\"storage-opts\":[\"dm.directlvm_device=/dev/sda4\",\"dm.thinp_percent=95\",\
    \"dm.thinp_metapercent=2\",\"dm.directlvm_device_force=true\",\"dm.basesize=20G\"],\
    \"node-generic-resources\":[%s],\"runtimes\":{\"nvidia\":{\"path\":\"nvidia-container-runtime\",\
    \"runtimeArgs\":[]}}}" %(getAddress(),getGpu())
    return str

if __name__ =='__main__':
    '''init
    sudo pip install nvidia-ml-py
    sudo systemctl daemon-reload
    sudo systemctl restart docker.service
    '''
    parser=argparse.ArgumentParser(description="this is a help message description!")
    parser.add_argument('-log',"--logprint",action="store_true",default=False,help="[-log] print param info")
    parser.add_argument('-gpu',"--getgpu",action="store_true",default=False,help="[-log] get gpu info")
    parser.add_argument('-start',"--start",action="store_true",default=False,help="[-start] restart service")
    parser.add_argument('-all',"--all",action="store_true",default=False,help="[-all] all")
    parser.add_argument('-test',"--test",action="store_true",default=False,help="[-log] test cmd")
    parser.add_argument('-pf',"--ptofile",action="store_true",default=False,help="[-log] print to file")
    args = parser.parse_args()

    if os.geteuid()!=0:
        print "use root to exec!"
        sys.exit(1)
    # 获取gpu信息
    if args.getgpu ==True:
        getGpu(args.logprint)
    elif args.all == True:
        dockerjson=getModel()
        d1= json.loads(dockerjson)
        d2 = json.dumps(d1,sort_keys=True,indent=4)
        if args.ptofile ==True:# 写入文件
            writetofile("/etc/docker/","daemon.json",d2)
        else:
            print d2
    #重启 docker
    if args.all == True or args.start:
        cmds="sudo systemctl daemon-reload"
        status=execCmd("reload",cmds,args.test)
        print cmds,status

        cmds="sudo systemctl restart docker.service"
        status=execCmd("restart",cmds,args.test)
        print cmds,status
