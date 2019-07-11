#!/bin/bash
sudo docker swarm leave -f
sudo docker swarm join $1
sudo docker info |grep -A 5 Swarm
