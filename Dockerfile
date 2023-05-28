FROM alpine:3.13.2
MAINTAINER Mumtaz Ahmad <mumtaz.ahmad@siemens.com>

RUN apk add --no-cache tzdata
RUN apk add --no-cache python3 py3-pip
RUN pip install termcolor
RUN apk add --no-cache ruby && \
    adduser -u 54123 -g 54123 -D -g tj3 -h /tj3 tj3 

RUN gem install taskjuggler --version 3.7.2 --no-document --clear-sources

VOLUME /app
WORKDIR /app
USER tj3