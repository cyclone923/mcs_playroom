# MCS Playroom Docker container
#
# docker build --tag mcs-playroom:0.0.6 .
# docker build --tag mcs-playroom:0.0.x --build-arg mcsversion=0.0.x .
#
# Allow X session connection
# xhost +si:localuser:root
#
# Run interactive bash shell
# docker run -it --rm --gpus all -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw mcs-playroom:0.0.6
#

FROM nvidia/opengl:1.0-glvnd-runtime-ubuntu18.04

ARG DEBIAN_FRONTEND=noninteractive

ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES},display

# --build-arg mcsversion=0.0.x to override default in docker build command
ARG mcsversion=0.0.6

WORKDIR /mcs

RUN apt-get update -y && \
    apt-get install -y git python3.8 python3-pip && \
    python3.8 -m pip install --upgrade pip setuptools wheel && \
    python3.8 -m pip install git+https://github.com/NextCenturyCorporation/MCS@${mcsversion}

# add ai2thor/unity resources
ADD https://github.com/NextCenturyCorporation/MCS/releases/download/${mcsversion}/MCS-AI2-THOR-Unity-App-v${mcsversion}.x86_64 /mcs
ADD https://github.com/NextCenturyCorporation/MCS/releases/download/${mcsversion}/MCS-AI2-THOR-Unity-App-v${mcsversion}_Data.tar.gz /mcs
RUN tar -xzvf /mcs/MCS-AI2-THOR-Unity-App-v${mcsversion}_Data.tar.gz -C /mcs && \
    chmod a+x /mcs/MCS-AI2-THOR-Unity-App-v${mcsversion}.x86_64 && \
    rm /mcs/MCS-AI2-THOR-Unity-App-v${mcsversion}_Data.tar.gz