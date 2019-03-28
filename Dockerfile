FROM python:3

RUN apt-get update \
 && apt-get install -y sudo \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
ADD . /usr/src/app

ENV TARGET_DIR=/terrasync
ENV UID=1000
ENV GID=1000

VOLUME $TARGET_DIR

ENTRYPOINT ["./entrypoint.sh"]
