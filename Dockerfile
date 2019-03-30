FROM python:3

RUN apt-get update \
 && apt-get install -y \
    httrack \
    sudo \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
ADD . /usr/src/app

ENV TARGET_DIR=/terrasync
ENV URL="https://dream.t3r.de/fgscenery/"
ENV PUID=1000
ENV PGID=1000
ENV REMOVE_ORPHANS=false
ENV CONNECTION_COUNT=20

VOLUME $TARGET_DIR

ENTRYPOINT ["./entrypoint.sh"]
