FROM python:3

RUN apt-get update \
 && apt-get install -y sudo \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
ADD . /usr/src/app

ENV TARGET_DIR=/terrasync
ENV PUID=1000
ENV PGID=1000
ENV PERMISSIONS_MASK=755
ENV SET_STICKY_BIT=true
ENV REMOVE_ORPHANS=false

VOLUME $TARGET_DIR

ENTRYPOINT ["./entrypoint.sh"]
