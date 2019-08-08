#!/bin/bash
sed -i 's/^PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config 
service ssh restart ||service sshd restart
mkdir /root/.ssh
echo -e $SSH_PUBKEY"\n" > /root/.ssh/authorized_keys
if [ ! -n "$N2N_NAME" ]; then
N2N_NAME='massgridn2n'
fi
if [ ! -n "$N2N_NETMASK" ]; then
N2NNETMASK=''
else
N2NNETMASK="-s $N2N_NETMASK"
fi
edge -d n2n -c $N2N_NAME -r -a $N2N_SERVERIP $N2NNETMASK -l $N2N_SNIP -f > /var/log/edge.log

