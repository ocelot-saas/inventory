"""Create the callcenter platform table."""

from yoyo import step


__depends__ = ['0004.inventory.create_platforms_website']


step("""
CREATE TABLE inventory.platforms_callcenter (
    id SERIAL,
    org_id INTEGER NOT NULL,
    time_created TIMESTAMP NOT NULL,
    phone_number TEXT NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT platforms_callcenter_fk_org_id
        FOREIGN KEY (org_id) REFERENCES inventory.org(id),
    CONSTRAINT platforms_callcenter_uk_org_id
        UNIQUE (org_id)
);
""", """
DROP TABLE IF EXISTS inventory.platforms_callcenter
""")
