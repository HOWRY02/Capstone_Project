
FROM ubuntu:22.04

RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get update && apt-get -y install tzdata && apt-get -y clean

RUN apt-get update && apt-get install -y --no-install-recommends apt-utils && apt-get -y clean

RUN apt-get -y update && apt-get -y upgrade && apt-get -y clean
RUN apt -y install curl libsane && apt-get -y clean

COPY ./brscan3-0.2.13-1.amd64.deb /tmp
COPY ./brscan-skey-0.3.2-0.amd64.deb /tmp

RUN dpkg -i --force-all ./tmp/brscan3-0.2.13-1.amd64.deb && rm ./tmp/brscan3-0.2.13-1.amd64.deb
RUN dpkg -i --force-all ./tmp/brscan-skey-0.3.2-0.amd64.deb && rm ./tmp/brscan-skey-0.3.2-0.amd64.deb

RUN brsaneconfig3 -a name=mq model=MFC-795CW ip=192.168.1.8
RUN brscan-skey

EXPOSE 3000

