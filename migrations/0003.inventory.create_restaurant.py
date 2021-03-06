"""Create the restaurant table."""

from yoyo import step


__depends__ = ['0002.inventory.create_org']


step("""
CREATE TABLE inventory.restaurant (
    id SERIAL,
    org_id INTEGER NOT NULL,
    time_created TIMESTAMP NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    keywords TEXT[] NOT NULL,
    address TEXT NOT NULL,
    opening_hours JSON NOT NULL,
    image_set JSON NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT restaurant_fk_org_id
        FOREIGN KEY (org_id) REFERENCES inventory.org(id),
    CONSTRAINT restaurant_uk_org_id
        UNIQUE (org_id)
);
""", """
DROP TABLE IF EXISTS inventory.restaurant;
""")
