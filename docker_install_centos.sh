#!/bin/bash
sudo yum update
sudo yum install kernel* pciutils -y
sudo yum install epel-release -y && sudo yum install --enablerepo=epel dkms -y     # kernel source
#sudo mv /boot/initramfs-$(uname -r).img /boot/initramfs-$(uname -r).img.bak
#sudo dracut /boot/initramfs-$(uname -r).img $(uname -r)
sudo yum install -y yum-utils \
  device-mapper-persistent-data \
  lvm2
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum update
sudo yum install docker-ce-18.06.1.ce-3.el7 -y
sudo docker volume ls -q -f driver=nvidia-docker | xargs -r -I{} -n1 docker ps -q -a -f volume={} | xargs -r docker rm -f
sudo yum remove nvidia-docker

# Add the package repositories
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.repo | \
  sudo tee /etc/yum.repos.d/nvidia-docker.repo

# Install nvidia-docker2 and reload the Docker daemon configuration
sudo yum install -y nvidia-docker2-2.0.3-1.docker18.06.1.ce
sudo pkill -SIGHUP dockerd

# Test nvidia-smi with the latest official CUDA image
docker run --runtime=nvidia --rm nvidia/cuda:9.0-base nvidia-smi