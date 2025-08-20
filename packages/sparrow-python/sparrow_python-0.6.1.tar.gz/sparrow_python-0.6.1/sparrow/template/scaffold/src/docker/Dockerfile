ARG PYTHON_VERSION=3.12
ARG CONDA_DIR=/opt/conda

FROM ubuntu:22.04
LABEL maintainer="placeholer"
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shangha
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
WORKDIR /home
RUN mv /etc/localtime /etc/localtime.bak && \
    ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    sed -i "s@http://.*archive.ubuntu.com@https://mirrors.tuna.tsinghua.edu.cn@g" /etc/apt/sources.list && \
    sed -i "s@http://.*security.ubuntu.com@https://mirrors.tuna.tsinghua.edu.cn@g" /etc/apt/sources.list && \
    apt update && \
    apt install -y build-essential
