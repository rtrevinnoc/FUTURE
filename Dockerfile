FROM ubuntu
MAINTAINER Roberto Treviño <rtrevinnoc@wearebuildingthefuture.com>
ENV DEBIAN_FRONTEND=noninteractive 
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y pkg-config python3-icu libicu-dev wget unzip git python3 python3-pip python-is-python3
RUN ln -s /usr/bin/pip3 /usr/bin/pip
WORKDIR opt
RUN mkdir FUTURE
WORKDIR FUTURE
COPY . .
RUN ./bootstrap.sh
