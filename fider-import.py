"""
This script clears and then inserts data from Fider's backup.zip into a new Postgres DB.

## Dependencies
        
        pip install psycopg2-binary python-magic

## Usage
With a folder named 'backup' in the current working dir)
        
        DATABASE_URL=postgres://localhost:9999 python fider-import.py

"""

import json
import os
import sys
import magic
import psycopg2
from psycopg2.extras import execute_values

TABLES = [
    'tenants',
    'users',
    'posts',
    'comments',
    'attachments',
    'email_verifications',
    'notifications',
    'oauth_providers',
    'tags',
    'post_subscribers',
    'post_tags',
    'post_votes',
    'user_providers',
    'user_settings',
]  # Order matters



print('connecting...')
conn = psycopg2.connect("postgres://postgres@postgres:5432/db")
print('connected')
conn.set_session(autocommit=False)


def truncate_table(table_name):
    with conn.cursor() as cur:
        cur.execute(f"TRUNCATE TABLE {table_name} CASCADE")


def insert_json_file(json_path):
    print(f"Inserting: {json_path}")
    with open (json_path,'r') as f:
        rows = json.loads(f.read())

    if not rows:  # Nothing to insert for this table
        return

    with conn.cursor() as cur:
        filename = os.path.basename(json_path)
        table_name = os.path.splitext(filename)[0]

        insert_sql = ''
        table_values = []
        for r in rows:
            col_names = []
            col_values = []
            for k, v in r.items():
                col_names.append(k)
                col_values.append(v)

            col_names_str = '(' + ', '.join(col_names) + ')'

            insert_sql = f"INSERT INTO {table_name} {col_names_str} VALUES %s"
            table_values.append(col_values)

        execute_values(cur, insert_sql, table_values)


def insert_blobs():
    print("Inserting attachments, logo and user avatars")
    with conn.cursor() as cur:
        insert_values = []

        # Add attachments
        cur.execute("SELECT tenant_id, attachment_bkey FROM attachments;")
        for a in cur.fetchall():
            insert_values.append(_read_blob(a))

        # Add logo
        cur.execute("SELECT id, logo_bkey FROM tenants;")
        insert_values.append(_read_blob(cur.fetchone()))

        # Add user avatars
        cur.execute("SELECT tenant_id, avatar_bkey FROM users WHERE avatar_bkey LIKE 'avatars/%';")
        insert_values.append(_read_blob(cur.fetchone()))

        insert_sql = "INSERT INTO blobs (key, tenant_id, size, content_type, file) VALUES %s"
        execute_values(cur, insert_sql, insert_values)


def _read_blob(blob):
    file_path = os.path.join('backup/blobs', blob[1])
    content_type = magic.from_file(file_path, mime=True)
    filedata = open(file_path,'rb').read()
    return blob[1], blob[0], len(filedata), content_type, filedata


if __name__ == '__main__':
    for t in TABLES:
        try:
            truncate_table(t)
        except:
            pass
    conn.commit()

    for t in TABLES:
        insert_json_file(f"backup/{t}.json")
    conn.commit()

    try:
        insert_blobs()
    except:
        sys.stderr.write('failed to insert blobs')
    conn.commit()
