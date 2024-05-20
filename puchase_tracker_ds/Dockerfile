# This shouldn't be needed but the official image for asyncapi/clu doesn't work
FROM node:22.0.0-slim AS mqtt_docs_gen
RUN npm install -g @asyncapi/cli@1.9.2
RUN npm install -g @asyncapi/html-template@2.3.5
RUN apt-get update && apt-get install git -y


FROM python:3.11
# Set environment variables to prevent Python from writing pyc files to disc and buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./code/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt && rm -f /requirements.txt
WORKDIR /app
ADD ./code /app/
