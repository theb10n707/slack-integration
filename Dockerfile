FROM ubuntu:20.04
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install lsof
RUN apt-get install coreutils
WORKDIR /code
COPY requirements.txt requirements.txt
COPY .env .env
RUN export #(cat .env)
RUN pip install -r requirements.txt
COPY . .
ENV FLASK_APP app