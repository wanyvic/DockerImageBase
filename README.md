# DockerImageBase
Massgrid docker image base

```
sudo docker pull wany/cuda9.1-base:2.0

sudo docker run -it --device=/dev/net:/dev/net:r --cap-add=NET_ADMIN wany/cuda9.1-base:2.0 /bin/bash
```
