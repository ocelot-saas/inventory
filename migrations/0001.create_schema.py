"""Crete the schema for the inventory service."""

from yoyo import step


step("""
CREATE SCHEMA inventory;
""", """
DROP SCHEMA IF EXISTS inventory;
""")
