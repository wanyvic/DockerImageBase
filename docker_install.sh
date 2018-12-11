#!/bin/bash
sudo apt-get update
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get update
sudo apt-get install -y docker-ce=18.06.1~ce~3-0~ubuntu
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | \
  sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update

# Install nvidia-docker2 and reload the Docker daemon configuration
sudo apt-get install -y nvidia-docker2=2.0.3+docker18.06.1-1
sudo pkill -SIGHUP dockerd
wget https://github.com/wanyvic/DockerImageBase/releases/download/docker-ce-16.04.1/nvidia-container-runtime-hook_1.4.0-1_amd64.deb \
https://github.com/wanyvic/DockerImageBase/releases/download/docker-ce-16.04.1/nvidia-container-runtime_2.0.0+docker18.06.1-1_amd64.deb
sudo dpkg -i nvidia-container-runtime-hook_1.4.0-1_amd64.deb nvidia-container-runtime_2.0.0+docker18.06.1-1_amd64.deb

    