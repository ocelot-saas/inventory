"""Create the callcenter platform table."""

from yoyo import step


__depends__ = ['0005.inventory.create_platforms_callcenter']


step("""
CREATE TABLE inventory.platforms_emailcenter (
    id SERIAL,
    org_id INTEGER NOT NULL,
    time_created TIMESTAMP NOT NULL,
    email_address TEXT NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT platforms_emailcenter_fk_org_id
        FOREIGN KEY (org_id) REFERENCES inventory.org(id),
    CONSTRAINT platforms_emailcenter_uk_org_id
        UNIQUE (org_id)
);
""", """
DROP TABLE IF EXISTS inventory.platforms_emailcenter
""")
