FROM ubuntu:latest

MAINTAINER Horia Coman <horia141@gmail.com>

# Install global packages.

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
            python3 \
            python3-pip \
            python3-dev \
            build-essential \
            libffi-dev \
	    libpq-dev \
            libssl-dev && \
    apt-get clean

RUN pip3 install setuptools

# Setup directory structure.

RUN mkdir /ocelot
RUN mkdir /ocelot/pack
RUN mkdir /ocelot/pack/inventory
RUN mkdir /ocelot/var
RUN mkdir /ocelot/var/db
RUN mkdir /ocelot/var/db/inventory

# Setup users and groups.

RUN groupadd ocelot && \
    useradd -ms /bin/bash -g ocelot ocelot

# Install package requirements.

COPY requirements.txt /ocelot/pack/inventory/requirements.txt
RUN cd /ocelot/pack/inventory && pip3 install -r requirements.txt

# Copy source code.

COPY . /ocelot/pack/inventory

# Setup the runtime environment for the application.

ENV ENVIRON LOCAL

RUN chown -R ocelot:ocelot /ocelot
VOLUME ["/ocelot/pack/inventory/src"]
WORKDIR /ocelot/pack/inventory/src
EXPOSE 10000
USER ocelot
ENTRYPOINT ["gunicorn", "--config", "inventory/config.py", "inventory.server:app"]
