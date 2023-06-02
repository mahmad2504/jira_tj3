FROM alpine:3.13.2
MAINTAINER Mumtaz Ahmad <mumtaz.ahmad@siemens.com>

ARG BRANCH=defaultValue
ARG COMMIT=defaultValue
ARG CODE_REPOSITORY=defaultValue

RUN echo "Building for $COMMIT"

RUN apk add --no-cache tzdata
RUN apk add --no-cache python3 py3-pip
RUN pip3 install --upgrade pip
RUN pip install termcolor
RUN pip install lxml
RUN pip install python-dateutil
RUN pip install pyinstaller
RUN pip install openpyxl

RUN apk add --no-cache ruby 
RUN gem install taskjuggler --version 3.7.2 --no-document --clear-sources

RUN apk add git
RUN mkdir -p /src
RUN git clone $CODE_REPOSITORY --depth=1 --branch $BRANCH --single-branch src
RUN git config --global --add safe.directory /app



