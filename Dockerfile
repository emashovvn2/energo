FROM python:3.8

WORKDIR /usr/src/app

COPY ./config.py /usr/src/app
COPY ./db.db /usr/src/app
COPY ./energoopros.py /usr/src/app
COPY ./findHome.py /usr/src/app
COPY ./sqlighter.py /usr/src/app
RUN pip install requests
RUN pip install aiogram
RUN pip install bs4
RUN pip install lxml
