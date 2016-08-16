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

ENV ENV LOCAL
ENV ADDRESS 0.0.0.0
ENV PORT 10000
ENV MIGRATIONS_PATH /ocelot/pack/inventory/migrations
ENV IDENTITY_SERVICE_DOMAIN ocelot-identity:10000
ENV DATABASE_URL postgresql://ocelot:ocelot@ocelot-postgres:5432/ocelot
ENV CLIENTS localhost:10000
ENV PYTHONPATH /ocelot/pack/inventory/src

RUN chown -R ocelot:ocelot /ocelot
VOLUME ["/ocelot/pack/inventory/src"]
WORKDIR /ocelot/pack/inventory/src
EXPOSE 10000
USER ocelot
ENTRYPOINT ["gunicorn", "--config", "inventory/config.py", "inventory.server:app"]
