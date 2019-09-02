FROM python:3.7.4
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
COPY requirements/base.txt /app/
RUN pip install -r base.txt
COPY . /app/
