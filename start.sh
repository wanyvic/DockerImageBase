#!/bin/bash
sed -i 's/^PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config 
service ssh restart ||service sshd restart
mkdir /root/.ssh
echo -e $SSH_PUBKEY"\n" > /root/.ssh/authorized_keys
edge -d n2n -c $N2N_NAME -a $N2N_SERVERIP -l $N2N_SNIP -f > /var/log/edge.log

