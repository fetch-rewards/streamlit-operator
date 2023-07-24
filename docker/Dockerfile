FROM python:3.9-slim

WORKDIR /launch

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    inotify-tools \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install streamlit

ADD launch.sh /launch/launch.sh

EXPOSE 80

HEALTHCHECK CMD curl --fail http://localhost:80/_stcore/health

ENTRYPOINT ["/launch/launch.sh"]