FROM python:3.5.1

RUN apt-get update
RUN curl -sL https://deb.nodesource.com/setup_4.x | bash -
RUN apt-get install -qqy nodejs
RUN apt-get install -qqy build-essential

COPY . src

WORKDIR src

RUN pip install -e .
RUN pip install -e .[test]

ENTRYPOINT bash
