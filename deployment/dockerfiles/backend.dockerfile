# pull official base image
#FROM ubuntu:22.04
FROM python:3.13-slim

RUN apt update -y > /dev/null &&  \
    apt upgrade -y > /dev/null && \
    apt install apt-utils -y > /dev/null

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="/:$PYTHONPATH"
ENV PYTHONPATH="/backend:$PYTHONPATH"
ENV POSTGRES_USER: ${POSTGRES_USER}
ENV POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
ENV POSTGRES_DB: ${POSTGRES_DB}
ENV POSTGRES_HOSTNAME: ${POSTGRES_HOSTNAME}
ENV POSTGRES_PORT: ${POSTGRES_PORT}

# Setup arguments
ARG VIRTUAL_ENV_PATH
ARG APP_FOLDER
ARG ENTRYPOINT_PATH

# Setup virtual environment
ENV VIRTUAL_ENV=$VIRTUAL_ENV_PATH
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python3 -m venv $VIRTUAL_ENV_PATH
COPY $APP_FOLDER/requirements.txt /$APP_FOLDER/requirements.txt
RUN pip3 --require-virtualenv install  -r /$APP_FOLDER/requirements.txt --quiet

# copy entrypoint
COPY $ENTRYPOINT_PATH $ENTRYPOINT_PATH
RUN chmod +x $ENTRYPOINT_PATH

# copy backend data
ENV PATH="$APP_FOLDER/api:$PATH"
COPY $APP_FOLDER /$APP_FOLDER



