# SPDX-FileCopyrightText: 2022 PeARS Project, <community@pearsproject.org> 
#
# SPDX-License-Identifier: AGPL-3.0-only

FROM python:3.8-slim-buster

RUN apt-get update

WORKDIR /pears-orchard

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

WORKDIR /pears-orchard

CMD [ "python3", "run.py"]
