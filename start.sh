#!/bin/bash
while getopts ":a:c:l:k:s:" opt 
do 
    case $opt in 
        a) 
        localip=$OPTARG;
        ;; 
        c) 
        name=$OPTARG;
        ;; 
        l) 
        serverip=$OPTARG;
        ;; 
        k) 
        key=$OPTARG; 
        ;; 
        s) 
        ssh_pubkey=$OPTARG;
        ;; 
        ?) 
        echo "error" 
        exit 1;; 
    esac 
done
edge -d n2n -c $name -k $key -a $localip -l $serverip
sed -i 's/^PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config 
service ssh restart ||service sshd restart
mkdir /root/.ssh
echo -e $ssh_pubkey"\n" > /root/.ssh/authorized_keys
ping localhost

