#!/bin/bash
edge -d n2n -c $N2N_NAME -k $N2N_KEY -a $N2N_LOCALIP -l $N2N_SERVERIP
sed -i 's/^PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config 
service ssh restart ||service sshd restart
mkdir /root/.ssh
echo -e $SSH_PUBKEY"\n" > /root/.ssh/authorized_keys
ping localhost

