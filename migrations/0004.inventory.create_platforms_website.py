"""Create the website platform table."""

from yoyo import step


__depends__ = ['0003.inventory.create_restaurant']


step("""
CREATE TABLE inventory.platforms_website (
    id SERIAL,
    org_id INTEGER NOT NULL,
    time_created TIMESTAMP NOT NULL,
    domain_prefix TEXT NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT platforms_website_fk_org_id
        FOREIGN KEY (org_id) REFERENCES inventory.org(id),
    CONSTRAINT platforms_website_uk_org_id
        UNIQUE (org_id)
);
""", """
DROP TABLE IF EXISTS inventory.platforms_website
""")
