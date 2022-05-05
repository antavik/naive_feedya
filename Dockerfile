#################################################################
####################### BUILD STAGE #############################
#################################################################
FROM snakepacker/python:all as builder

ARG DEV_MODE=false

ENV PIPENV_DEV=$DEV_MODE

RUN python3.9 -m venv /usr/share/python3/app

# Setup python env
COPY ./pipfiles/ /etc/pipfiles/

WORKDIR /etc/pipfiles/

RUN /usr/share/python3/app/bin/pip install -U pip setuptools wheel && \
    /usr/share/python3/app/bin/pip install --no-cache-dir pipenv==2022.4.30 && \
    /usr/share/python3/app/bin/pipenv install --system --skip-lock && \
    /usr/share/python3/app/bin/python3.9 -m spacy download ru_core_news_sm

RUN find-libdeps /usr/share/python3/app > /usr/share/python3/app/pkgdeps.txt

#################################################################
####################### TARGET STAGE ############################
#################################################################
FROM snakepacker/python:3.9

ARG GIT_BRANCH
ARG GITHUB_SHA
ARG DEV_MODE=false
ARG USER=app
ARG APP_NAME=naive_feedya

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEV_MODE=$DEV_MODE
ENV GIT_BRANCH=$GIT_BRANCH
ENV GITHUB_SHA=$GITHUB_SHA

COPY --from=builder /usr/share/python3/app /usr/share/python3/app

RUN cat /usr/share/python3/app/pkgdeps.txt | xargs apt-install

COPY ./app/ /home/$USER/app/

# Setup app env and create cache folder
RUN useradd -U -s /bin/bash $USER && \
    chown -R $USER:$USER /home/$USER/ && \
    mkdir /var/lib/$APP_NAME && \
    chown -R $USER:$USER /var/lib/$APP_NAME

WORKDIR /home/$USER/app

USER $USER

EXPOSE 8008