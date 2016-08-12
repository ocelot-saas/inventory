#!/usr/bin/env python3

from yoyo import read_migrations, get_backend
import inventory.config as config


def main():
    """Migrations script entry point."""
    migrations = read_migrations(config.MIGRATIONS_PATH)
    backend = get_backend(config.DATABASE_URL)
    backend.apply_migrations(backend.to_apply(migrations))


if __name__ == '__main__':
    main()
