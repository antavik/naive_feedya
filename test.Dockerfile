FROM python:3.9-slim

ARG USER=app
ARG APP_NAME=naive_feedya

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    apt-utils && \
    apt-get clean && \
    apt-get autoclean && \
    rm -rf /var/cache/* && \
    rm -rf /var/lib/apt/lists/*

# Setup python env
COPY ./pipfiles/Pipfile-test /etc/pipfiles/Pipfile

WORKDIR /etc/pipfiles/

RUN pip install --no-cache-dir pipenv==2020.8.13 && \
    pipenv install --system --dev --skip-lock

# Setup app env and create cache folder
RUN useradd -m -U -s /bin/bash $USER && \
    chown -R $USER:$USER /home/$USER/ && \
    mkdir /var/lib/$APP_NAME && \
    chown -R $USER:$USER /var/lib/$APP_NAME/

COPY ./app/ /home/$USER/app/

WORKDIR /home/$USER/app

USER $USER

EXPOSE 8008