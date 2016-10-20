#!/usr/bin/env python3

import time

from yoyo import read_migrations, get_backend
import psycopg2

import inventory.config as config


def main():
    """Migrations script entry point."""
    
    retries = 0
    while retries < 10:
        try:
            backend = get_backend(config.DATABASE_URL)
            break
        except psycopg2.OperationalError:
            retries += 1
            time.sleep(1.0)
    else:
        raise Exception('Could not connect to the database')
    
    migrations = read_migrations(config.MIGRATIONS_PATH)
    backend.apply_migrations(backend.to_apply(migrations))


if __name__ == '__main__':
    main()
