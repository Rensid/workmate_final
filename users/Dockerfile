FROM python:3.12

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ADD requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ADD . /app

