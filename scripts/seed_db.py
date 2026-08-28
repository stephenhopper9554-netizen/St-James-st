#!/usr/bin/env python3
"""
Seed script: create initial roles and invite codes in the database.
Usage:
  DATABASE_URL=postgresql://postgres:postgres@localhost:5432/stjames python3 scripts/seed_db.py
"""
import os
import sys
import uuid

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    print("psycopg2 is required. Install with: pip install psycopg2-binary")
    sys.exit(1)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/stjames")

INVITE_CODES = [
    "J7K9L2X4QZ",
    "M3V8R1T6SB",
]

ROLES = [
    "resident_unverified",
    "resident_verified",
    "admin",
    "enforcement",
]


def upsert_roles(conn):
    with conn.cursor() as cur:
        for r in ROLES:
            cur.execute(
                "INSERT INTO roles (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;",
                (r,)
            )
    conn.commit()


def seed_invites(conn):
    with conn.cursor() as cur:
        for code in INVITE_CODES:
            cur.execute(
                "INSERT INTO invite_codes (code, created_at) VALUES (%s, now()) ON CONFLICT (code) DO NOTHING;",
                (code,)
            )
    conn.commit()


def main():
    print(f"Connecting to {DATABASE_URL}")
    conn = psycopg2.connect(DATABASE_URL)
    try:
        upsert_roles(conn)
        seed_invites(conn)
        print("Seeded roles and invite codes:")
        for c in INVITE_CODES:
            print(f" - {c}")
    finally:
        conn.close()


if __name__ == '__main__':
    main()
