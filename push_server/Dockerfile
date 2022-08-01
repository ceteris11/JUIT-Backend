
FROM ubuntu:18.04

WORKDIR /app

# change apt-get repo
RUN sed -i 's@archive.ubuntu.com@mirror.kakao.com@g' /etc/apt/sources.list

RUN apt-get update
RUN apt-get install -y software-properties-common
RUN apt-get install -y --no-install-recommends python3.8 python3-dev python3-pip python3-setuptools python3-wheel gcc
RUN apt-get install nano
RUN apt-get install vim -y
RUN apt-get install wget -y
RUN apt-get install curl -y
RUN apt-get install tzdata -y

RUN mkdir config; mkdir db; mkdir fcmpush;

COPY requirements.txt /app
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY config/* /app/config
COPY db/* /app/db
COPY fcmpush/* /app/fcmpush
COPY main.py /app

WORKDIR /app

ENV TZ="Asia/Seoul"

CMD ["python3", "main.py"]
