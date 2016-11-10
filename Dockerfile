FROM ubuntu:latest

MAINTAINER Horia Coman <horia141@gmail.com>

# Install global packages.

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
            build-essential \
            libffi-dev \
            libpq-dev \
            libssl-dev \
            python3 \
            python3-dev \
            python3-pip \
            python3-setuptools && \
    apt-get clean

# Setup directory structure.

RUN mkdir /ocelot-saas
RUN mkdir /ocelot-saas/pack
RUN mkdir /ocelot-saas/var

# Setup users and groups.

RUN groupadd ocelot-saas && \
    useradd -ms /bin/bash -g ocelot-saas ocelot-saas

# Install package requirements.

COPY requirements.txt /ocelot-saas/pack/requirements.txt
RUN cd /ocelot-saas/pack && pip3 install -r requirements.txt

# Copy source code.

COPY . /ocelot-saas/pack

# Setup the runtime environment for the application.

ENV ENV LOCAL
ENV ADDRESS 0.0.0.0
ENV PORT 10000
ENV MASTER_DOMAIN ocelot.com
ENV IDENTITY_SERVICE_DOMAIN ocelot-saas-identity:10000
ENV MIGRATIONS_PATH /ocelot-saas/pack/migrations
ENV DATABASE_URL postgresql://ocelot-saas:ocelot-saas@ocelot-saas-postgres:5432/ocelot-saas
ENV CLIENTS localhost:10000
ENV PYTHONPATH /ocelot-saas/pack/src

RUN chown -R ocelot-saas:ocelot-saas /ocelot-saas
VOLUME ["/ocelot-saas/pack/src"]
VOLUME ["/ocelot-saas/var/secrets.json"]
WORKDIR /ocelot-saas/pack/src
EXPOSE 10000
USER ocelot-saas
ENTRYPOINT ["gunicorn", "--config", "inventory/config.py", "inventory.server:app"]
