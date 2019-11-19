#!/user/bin python2
# -*- coding: utf-8 -*-
import argparse
import os,stat
import commands
import sys
import time
import re
import json
import os
try:
    from pynvml import *
except:
    os.system("sudo pip install nvidia-ml-py")
    from pynvml import *

def execCmd(info,realCmd,testExec=False):
    print(info,">",realCmd)
    if testExec != True:
        status,cmt=commands.getstatusoutput(realCmd)
        # print(status,cmt)
        return status
    return 1
def fileExists(filepath,type=1):
    if type == 1:
        return os.access(filepath,os.R_OK)
    elif type ==2:
        return os.access(filepath,os.W_OK)
    else:
        return os.access(filepath,os.X_OK)

def isfiles(files):
     return os.path.isfile(files)

def readfile(filename):
    lists = []
    cin=open(filename,'r')
    for line in cin:
        tmp = []
        for row in line.split('='):
            tmp.append(row)
        lists.append(tmp)
    cin.close()
    return lists
def writetofile(filepath,filename,filecontant,enforce=False):
    print("# %s:: write files %s%s start...!" % (writetofile.__name__,filepath,filename))
    if fileExists(filepath,2) == False:
        print("error:: the %s is Not permission" % filepath)
        return 1
    files=filepath+filename
    if isfiles(files) and  (enforce == True or raw_input("will be cover old file[y/n]?") =="y"):
        with open(files,'w') as f:
            f.write(filecontant)
        f.close()
    else:
        print("not changed")
    return 0
# edit runtime conf.toml 
def checkAndEdit(gpuname=""):
    filepath = "/etc/nvidia-container-runtime/"
    filename = "config.toml"
    res = readfile(filepath+filename)
    if gpuname == "":
        print(filepath,filename)
        for i in res:
            print(i)
        return
    fullname = "DOCKER_RESOURCE_%s" %(gpuname)
    isupdate = False
    strs = ""
    for i in res:
        if len(i)== 1:
            strs = strs + i[0]
        elif len(i) == 2:
            key = i[0]+"="
            value = i[1]
            strs = strs + key
            if len(key)>14 and  key[0]!='#' and key[:14] == "swarm-resource" and value.find("DOCKER_RESOURCE") > 0 and fullname != value[2:len(value)-2]:
                strs = strs + " \"{}\"\n".format(fullname)
                isupdate = True
            else:
                strs = strs + value
    if isupdate:
        if args.ptofile:
            writetofile(filepath,filename,strs,True)
        print(strs)
            
# 重启docker
def startDocker(jointoken):
    cmds="sudo systemctl daemon-reload"
    status=execCmd("reload",cmds,args.test)
    if status == 0:
        print("reload succeeful!")
    else:
        print("failed!",status)

    cmds = "sudo systemctl restart docker.service"
    status=execCmd("restart",cmds,args.test)
    if status ==0:
        print("restart docker.service succeful!")
    else:
        print("failed!",status)
    
    if jointoken is not None and jointoken != "":
        cmds = "sudo docker swarm leave -f"
        status = execCmd("join swarm",cmds,args.test)
        print("join leave",status)
        cmds = "sudo docker swarm join --token %s" %(jointoken)
        status = execCmd("join swarm",cmds,args.test)
        print("join swarm ",status)
        
def setDockerPM():
    cmds ="sudo nvidia-smi -pm 1"
    status=execCmd("set nvidia-smi -pm 1",cmds,args.test)
    if status ==0:
        print("reset nvidia-smi -pm 1 succeful")
    else:
        print("failed!",status)
def getAddress():
    address="M93cBXBGTpXT9XYQejiprWzKpXjhEc5jd8"
    # addr=raw_input("input your MGD wallet address as revenue:")
    # if addr:
    #     address=addr
    return address
def getDataHost():
    host="192.168.2.170"
    return host

def getGpu(log=False):
    # print("get nvidia gpu infomation")
    try:
        nvmlInit()
    except:
        print("nvidia driver failed!")
        sys.exit(1)
    version=nvmlSystemGetDriverVersion()
    if log ==True:
        print("nvidia: ",version)
    devicecount=nvmlDeviceGetCount()
    tmplist=[]
    gpulist=[]
    for i in range(devicecount):
        handler=nvmlDeviceGetHandleByIndex(i)
        if i==0:
            meminfo = nvmlDeviceGetMemoryInfo(handler)
            gpu_mem=int(meminfo.total/1024.0/1024.0/1024.0+0.5)
        gpuname=nvmlDeviceGetName(handler).replace('-','_')
        gputype=gpuname
        if ' ' in gpuname:
            gpu_model = gpuname.split(' ')
            gpuname=gpu_model[2]+"_"+gpu_model[3]
            gputype=gpu_model[1]+gpuname
        gpuuuid=nvmlDeviceGetUUID(handler)
        gpuname="nvidia_"+gputype.lower()
        if gpuname[-2:] == "gb":
            gpuname=gpuname[:-1]
        else:
            gpuname=gpuname+"_"+str(gpu_mem)+"g"
        gpuname=gpuname.upper()
        nvidia=gpuname+"="+gpuuuid[0:11]
        if args.old:
            nvidia="NVIDIA_GPUP104_100="+gpuuuid[0:11]
        tmplist.append(nvidia)
        if log==True:
            print(gpuname,gpuuuid[0:11],gpu_mem)
            print(nvidia)
    gpu_count = "GPUCOUNT="+str(devicecount)
    gpu_type = "GPUTYPE="+ str(gpuname)
    
    # update toml 文件
    checkAndEdit(gpuname)
    
    gpulist.append(gpu_count)
    gpulist.append(gpu_type)
    nvmlShutdown()
    return tmplist,gpulist
def getCpu(log=False):
    cpulist=[]
    num = 0
    with open('/proc/cpuinfo') as fd:
        for line in fd:
            if line.startswith('processor'):
                num += 1
            if line.startswith('model name'):
                cpu_model = line.split(':')[1].strip().split()
                cpu_model_info = cpu_model[0] + ' ' + cpu_model[2] + ' ' + cpu_model[-1]
    if log:
        print("cpu num:",num,"model:",cpu_model_info)
    if "Intel" in cpu_model[0]:
        cpu_m=cpu_model[2].split('-')[0].strip().split()
        cpu_type="CPUTYPE="+"Intel_"+cpu_m[0]
        cpu_count="CPUTHREAD="+str(num)
        cpulist.append(cpu_count)
        cpulist.append(cpu_type)
        # print(cpu_type,cpu_count)
    return cpulist
def getMem(log=False):
    memlist=[]
    with open('/proc/meminfo') as fd:
        for line in fd:
            if line.startswith('MemTotal'):
                mem = int(line.split()[1].strip())
                break
    memsize = '%d' % (mem / 1000/1000+0.5)
    if log:
        print("mem:",memsize,mem)
    mem_n="MEMORYCOUNT="+str(memsize)
    mem_m="MEMORYTYPE=ddr"
    memlist.append(mem_n)
    memlist.append(mem_m)
    return memlist
def getIp():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def getCurrDaemonJson():
    with open("/etc/docker/daemon.json",'r') as load_f:
        load_dict = json.load(load_f)
        result = json.dumps(load_dict,sort_keys=True,indent=4)
        print(result)

def mgdminer(miner_addr="MTzzXdhT3NDyfFLUL42bVYeewYpt8JSqAm"):
    ipaddr = "127.0.0.1"
    ipaddr = getIp()
    ipaddr = "mgd" + ipaddr[ipaddr.rfind(".")+1:]
    minerlist=[]
    mineraddr="MINER_ADDRESS=%s" %(miner_addr)
    minerworker="MINER_WORKER=" + ipaddr
    minerpool="MINER_POOL1=mgd.vvpool.com:5630"
    minertype="MINER_TYPE=MGD"
    minerlist.append(mineraddr)
    minerlist.append(minerpool)
    minerlist.append(minerworker)
    minerlist.append(minertype)
    return minerlist

def ethminer(miner_addr="0x21e7DC2eb03ae57F1d81F2cb566C7780D11c7DAf"):
    ipaddr = "127.0.0.1"
    ipaddr = getIp()
    ipaddr = "eth"+ipaddr[ipaddr.rfind(".")+1:]
    minerlist=[]
    # mineraddr="miner_address=0x44df6dffad1cc0738233dbd024fdd46cf14c2c4c"
    mineraddr="MINER_ADDRESS=%s" % (miner_addr)
    minerworker="MINER_WORKER="+ipaddr
    minerpool="MINER_POOL1=eth.f2pool.com:8080"
    minertype="MINER_TYPE=ETH"
    minerlist.append(mineraddr)
    minerlist.append(minerpool)
    minerlist.append(minerworker)
    minerlist.append(minertype)
    return minerlist

def getMiner(minertype,address,log=False):
    if minertype == "eth":
        minerlist=ethminer(address)
    else:
        minerlist=mgdminer(address)
    if log:
        print(minerlist)
    return minerlist

def getModel(tmplist,gpulist,cpulist,memlist,minerlist,device_name,revenue_ddr):
    localip="LOCALIP="+getIp()
    ipaddress="REVENUE_ADDRESS="+revenue_ddr
    nfsip="NFSIP="+getDataHost()
    label_list=[localip,ipaddress,nfsip]
    for k in cpulist:label_list.append(k)
    for k in memlist:label_list.append(k)
    for k in gpulist:label_list.append(k)
    for k in minerlist:label_list.append(k)
    directlvm_device = "dm.directlvm_device=/dev/%s" %(device_name)
    storge_list=[directlvm_device,"dm.thinp_percent=95","dm.thinp_metapercent=2","dm.directlvm_device_force=true","dm.basesize=40G"]
    ddaemonJson = {
        "labels": label_list,
        "default-runtime": "nvidia",
        "node-generic-resources": tmplist,
        "runtimes":{"nvidia":{"path":"nvidia-container-runtime","runtimeArgs":[]}}
    }
    return ddaemonJson
if __name__ =='__main__':
    '''init
    sudo pip install nvidia-ml-py
    sudo pip installl psutil
    sudo systemctl daemon-reload
    sudo systemctl restart docker.service
    '''
    parser=argparse.ArgumentParser(description="this is a help message description!")
    parser.add_argument('-log',"--logprint",action="store_true",default=False,help="[-log] print more information")
    parser.add_argument('-gpu',"--getgpu",action="store_true",default=False,help="[-gpu] get gpu infomation")
    parser.add_argument('-cpu',"--getcpu",action="store_true",default=False,help="[-cpu] get cpu infomation")
    parser.add_argument('-mem',"--getmem",action="store_true",default=False,help="[-mem] get mem infomation")
    parser.add_argument('-dev',"--device",nargs="?",default="/dev/sda4",type=str,help="[-device] get device name")
    parser.add_argument('-miner',"--getminer",nargs="?",default="",type=str,help="[-miner] miner type")
    parser.add_argument('-addr',"--address",nargs="?",default="",type=str,help="[-address] miner address")
    parser.add_argument('-join',"--jointoken",nargs="?",default="",type=str,help="[-address] miner address")
    parser.add_argument('-revenue',"--revenue",nargs="?",default="",type=str,help="[-miner] revenue address")

    parser.add_argument('-start',"--start",action="store_true",default=False,help="[-start] restart service")
    parser.add_argument('-toml',"--toml",action="store_true",default=False,help="[-start] check and edit the toml")
    parser.add_argument('-all',"--getall",action="store_true",default=False,help="[-all] get all of gpu,cpu,mem infomation")
    parser.add_argument('-test',"--test",action="store_true",default=False,help="[-test] test cmd,just for restart docker")
    parser.add_argument('-pf',"--ptofile",action="store_true",default=False,help="[-pf] print to file")
    parser.add_argument('-s',"--silent",action="store_true",default=False,help="[-pf] print to file with silent")
    parser.add_argument('-old',"--old",action="store_true",default=False,help="[-load] get currency daemon.json content")
    parser.add_argument('-load',"--load",action="store_true",default=False,help="[-load] get currency daemon.json content")
    parser.add_argument('-ip',"--ipaddr",action="store_true",default=False,help="[-ip] get local ip address")
    args = parser.parse_args()

    if os.geteuid()!=0:
        print("use root to exec!")
        sys.exit(1)
    # run-time config.toml
    if args.toml == True:
        checkAndEdit()

    # get currency docker.json content
    if args.load == True:
        getCurrDaemonJson()

    jointoken = args.jointoken
    # restart docker
    if args.start == True:
        startDocker(jointoken)

    # get local ip
    if args.ipaddr ==True:
        print("localip:",getIp())

    # get gpu infomation
    if args.getgpu == True:
        getGpu(args.logprint)

    # get cpu information
    if args.getcpu == True:
        getCpu(args.logprint)

    # get mem information
    if args.getmem == True:
        getMem(args.logprint)
    
    # get mem information
    if args.getminer != "":
        getMiner(args.getminer,args.address,args.logprint)
    
    # get all message
    if args.getall == True:
        tmplist,gpulist=getGpu(args.logprint)
        cpulist=getCpu(args.logprint)
        memlist=getMem(args.logprint)
        minerlist=getMiner(args.getminer,args.address,args.logprint)
        device_name = args.device
        revenue_ddr = args.revenue
        dockerjson=getModel(tmplist,gpulist,cpulist,memlist,minerlist,device_name,revenue_ddr)
        
        setDockerPM()
        # template= json.loads(dockerjson)
        result = json.dumps(dockerjson,sort_keys=True,indent=4)
        # write to file
        if args.ptofile == True:
            writetofile("/etc/docker/","daemon.json",result,args.silent)
            startDocker(jointoken)
        else:
            print(result)
    if len(sys.argv)<2:
        print("Please Usage: sudo python %s -h (for more help)" %(sys.argv[0]))

'''
sudo vim /etc/nvidia-container-runtime/config.toml
'''


'''
# 初始化配置
sudo python nvidia.py -all -pf -miner "mgd" -addr "MTzzXdhT3NDyfFLUL42bVYeewYpt8JSqAm"  -revenue "MTzzXdhT3NDyfFLUL42bVYeewYpt8JSqAm" \
-join "SWMTKN-1-0uau6cvrqjv90wx0ka4h5g04bqwe0t0lmy25secg8i81rg15uj-dcoko0h4rlfdnkw9kd5z7vsn4 49.234.37.252:2377"

-all 获取所有数据(gpu ,mem,cpu)
-pf 强制写入文件

# 查看当前 daemon.json 内容
sudo python nvidia.py -load

# 查看当前 config.toml 内容
sudo python nvidia.py -load

# 重启 docker
sudo python nvidia.py -start
'''

'''
{
    "default-runtime": "nvidia", 
    "labels": [
        "LOCALIP=192.168.122.100", 
        "REVENUE_ADDRESS=MTzzXdhT3NDyfFLUL42bVYeewYpt8JSqAmASDFASDF", 
        "NFSIP=192.168.2.170", 
        "CPUTHREAD=2", 
        "CPUTYPE=Intel_CPU", 
        "MEMORYCOUNT=3", 
        "MEMORYTYPE=ddr", 
        "GPUCOUNT=3", 
        "GPUTYPE=NVIDIA_P102_100_5G", 
        "MINER_ADDRESS=MTzzXdhT3NDyfFLUL42bVYeewYpt8JSqAm", 
        "MINER_POOL1=mgd.vvpool.com:5630", 
        "MINER_WORKER=mgd100", 
        "MINER_TYPE=MGD"
    ], 
    "node-generic-resources": [
        "NVIDIA_P102_100_5G=GPU-7af8456", 
        "NVIDIA_P102_100_5G=GPU-eeae24e", 
        "NVIDIA_P102_100_5G=GPU-87af86f"
    ], 
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime", 
            "runtimeArgs": []
        }
    }
}

'''
