"""Create the menu structure."""

from yoyo import step


__depends__ = ['0006.create_platforms_emailcenter']


step("""
CREATE TABLE inventory.menu_section (
    id SERIAL,
    org_id INTEGER NOT NULL,
    time_created TIMESTAMP NOT NULL,
    time_archived TIMESTAMP,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT menu_section_fk_org_id
        FOREIGN KEY (org_id) REFERENCES inventory.org(id),
    CONSTRAINT menu_section_uk_id_org_id
        UNIQUE (id, org_id)
);

CREATE TABLE inventory.menu_item (
    id SERIAL,
    section_id INTEGER NOT NULL,
    org_id INTEGER NOT NULL,
    time_created TIMESTAMP NOT NULL,
    time_archived TIMESTAMP,,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    keywords TEXT[] NOT NULL,
    ingredients JSON NOT NULL,
    image_set JSON NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT menu_item_fk_section_id_org_id
        FOREIGN KEY (section_id, org_id) REFERENCES inventory.menu_section(id, org_id),
    CONSTRAINT menu_item_uk_id_section_id_org_id
        UNIQUE (id, section_id, org_id)
);
""", """
DROP TABLE IF EXISTS inventory.menu_item;
DROP TABLE IF EXISTS inventory.menu_section;
""")
