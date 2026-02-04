FROM python:3.9
WORKDIR /re2bench

COPY ./requirements.txt /re2bench/requirements.txt

RUN apt-get update


RUN pip3 install -r /re2bench/requirements.txt

COPY ./analysis /re2bench/analysis
COPY ./dataset /re2bench/dataset
COPY ./scripts /re2bench/scripts

