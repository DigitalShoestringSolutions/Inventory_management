# This shouldn't be needed but the official image for asyncapi/clu doesn't work
FROM node:22.0.0-slim AS mqtt_docs_gen
RUN npm install -g @asyncapi/cli@1.9.2
RUN npm install -g @asyncapi/html-template@2.3.5
RUN apt-get update && apt-get install git -y


FROM digitalshoestring/shoestring-django-rest:v0.0.1
COPY ./code/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt && rm -f /requirements.txt
WORKDIR /app
ADD ./code /app/
