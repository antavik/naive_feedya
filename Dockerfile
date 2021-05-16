FROM python:3.9.3-slim

ARG USER=app
ARG APP_NAME=naive_feedya
ARG DEV_MODE=false

ENV PYTHONUNBUFFERED 1
ENV PIPENV_DEV=$DEV_MODE

RUN apt-get update && apt-get install -y \
    apt-utils && \
    apt-get clean && \
    apt-get autoclean && \
    rm -rf /var/cache/* && \
    rm -rf /var/lib/apt/lists/*

# Setup python env
COPY ./pipfiles/ /etc/pipfiles/

WORKDIR /etc/pipfiles/

RUN pip install --no-cache-dir pipenv==2020.8.13 && \
    pipenv install --system --ignore-pipfile

# Setup app env and create cache folder
RUN useradd -m -U -s /bin/bash $USER && \
    chown -R $USER:$USER /home/$USER/ && \
    mkdir /var/lib/$APP_NAME && \
    chown -R $USER:$USER /var/lib/$APP_NAME

COPY ./app/ /home/$USER/app/

WORKDIR /home/$USER/app

USER $USER

EXPOSE 8008