FROM python:3.8-slim-buster

RUN apt-get update && apt install -y zip

WORKDIR /pears-orchard

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

WORKDIR app/static/spaces

RUN unzip -o english.dm.zip

WORKDIR /pears-orchard

CMD [ "python3", "run.py"]
