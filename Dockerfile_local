FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv python3-dev git curl wget unzip libegl1 libgl1\
    libosmesa6-dev patchelf libglfw3 libglew-dev libgl1-mesa-dev libglu1-mesa xvfb libglib2.0-0 \
    libxrandr2 libxcursor1 libxinerama1 libxi6 mesa-utils\
    && rm -rf /var/lib/apt/lists/*

# MuJoCo 설치
RUN mkdir -p /root/.mujoco && \
    wget https://mujoco.org/download/mujoco210-linux-x86_64.tar.gz && \
    tar -xvzf mujoco210-linux-x86_64.tar.gz -C /root/.mujoco && \
    rm mujoco210-linux-x86_64.tar.gz

ENV MUJOCO_PY_MUJOCO_PATH=/root/.mujoco/mujoco210
ENV LD_LIBRARY_PATH=/root/.mujoco/mujoco210/bin:${LD_LIBRARY_PATH}
#ENV MUJOCO_GL=osmesa
ENV MUJOCO_GL=egl
# Python 패키지 설치 (Ubuntu 24.04 대응: PEP 668 우회)
RUN pip3 install --break-system-packages robosuite==1.5.1 mujoco stable-baselines3 numpy h5py tensorboard imageio

# 작업 디렉토리 설정
WORKDIR /workspace
COPY . /workspace