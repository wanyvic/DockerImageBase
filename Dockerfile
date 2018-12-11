
FROM ubuntu:16.04
LABEL maintainer "NVIDIA CORPORATION <cudatools@nvidia.com>"

# CN apt-get source.list
RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak && \
echo "deb http://cn.archive.ubuntu.com/ubuntu/ xenial main restricted" >/etc/apt/sources.list && \
echo "deb http://cn.archive.ubuntu.com/ubuntu/ xenial-updates main restricted" >>/etc/apt/sources.list && \
echo "deb http://cn.archive.ubuntu.com/ubuntu/ xenial universe" >>/etc/apt/sources.list && \
echo "deb http://cn.archive.ubuntu.com/ubuntu/ xenial-updates universe" >>/etc/apt/sources.list && \
echo "deb http://cn.archive.ubuntu.com/ubuntu/ xenial multiverse" >>/etc/apt/sources.list && \
echo "deb http://cn.archive.ubuntu.com/ubuntu/ xenial-updates multiverse" >>/etc/apt/sources.list && \
echo "deb http://cn.archive.ubuntu.com/ubuntu/ xenial-backports main restricted universe multiverse" >>/etc/apt/sources.list && \
echo "deb http://security.ubuntu.com/ubuntu xenial-security main restricted" >>/etc/apt/sources.list && \
echo "deb http://security.ubuntu.com/ubuntu xenial-security universe" >>/etc/apt/sources.list && \
echo "deb http://security.ubuntu.com/ubuntu xenial-security multiverse" >>/etc/apt/sources.list

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates apt-transport-https gnupg-curl wget net-tools inetutils-ping ssh && \
    rm -rf /var/lib/apt/lists/* && \
    NVIDIA_GPGKEY_SUM=d1be581509378368edeec8c1eb2958702feedf3bc3d17011adbf24efacce4ab5 && \
    NVIDIA_GPGKEY_FPR=ae09fe4bbd223a84b2ccfce3f60f4b3d7fa2af80 && \
    apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/7fa2af80.pub && \
    apt-key adv --export --no-emit-version -a $NVIDIA_GPGKEY_FPR | tail -n +5 > cudasign.pub && \
    echo "$NVIDIA_GPGKEY_SUM  cudasign.pub" | sha256sum -c --strict - && rm cudasign.pub && \
    echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64 /" > /etc/apt/sources.list.d/cuda.list && \
    echo "deb https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1604/x86_64 /" > /etc/apt/sources.list.d/nvidia-ml.list

ENV CUDA_VERSION 9.1.85

ENV CUDA_PKG_VERSION 9-1=$CUDA_VERSION-1
RUN apt-get update && apt-get install -y --no-install-recommends \
        cuda-cudart-$CUDA_PKG_VERSION  ocl-icd-libopencl1 ocl-icd-opencl-dev clinfo && \
    ln -s cuda-9.1 /usr/local/cuda && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /etc/OpenCL/vendors && \
    echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd


# nvidia-docker 1.0
LABEL com.nvidia.volumes.needed="nvidia_driver"
LABEL com.nvidia.cuda.version="${CUDA_VERSION}"

RUN echo "/usr/local/nvidia/lib" >> /etc/ld.so.conf.d/nvidia.conf && \
    echo "/usr/local/nvidia/lib64" >> /etc/ld.so.conf.d/nvidia.conf

ENV PATH /usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
ENV LD_LIBRARY_PATH /usr/local/nvidia/lib:/usr/local/nvidia/lib64

# nvidia-container-runtime
ENV NVIDIA_VISIBLE_DEVICES none
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
ENV NVIDIA_REQUIRE_CUDA "cuda>=9.1"

ENV EDGE_DOWNLOAD=https://github.com/wanyvic/DockerImageBase/releases/download/n2n_moudle_edge/edge
ENV START_SHELL=https://github.com/wanyvic/DockerImageBase/releases/download/ImageStartShell/start.sh
RUN wget -P /usr/local/bin $EDGE_DOWNLOAD $START_SHELL && chmod +x /usr/local/bin/start.sh /usr/local/bin/edge

# overwrite this with 'CMD []' in a dependent Dockerfile
CMD ["/usr/local/bin/start.sh"]

