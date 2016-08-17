"""Create the org and the org_users table."""

from yoyo import step


__depends__ = ['0001.inventory.create_schema']


step("""
CREATE TABLE inventory.org (
    id SERIAL,
    time_created TIMESTAMP NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE inventory.org_user (
    org_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    time_created TIMESTAMP NOT NULL,
    PRIMARY KEY (org_id, user_id),
    CONSTRAINT org_user_fk_org_id
        FOREIGN KEY (org_id) REFERENCES inventory.org(id),
    CONSTRAINT org_user_uk_org_id
        UNIQUE (org_id),
    CONSTRAINT org_user_uk_user_id
        UNIQUE (user_id)
);
""", """
DROP TABLE IF EXISTS inventory.org_user;
DROP TABLE IF EXISTS inventory.org;
""")
