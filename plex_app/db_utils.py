import os
import sqlite3
basepath = os.path.dirname(os.path.abspath(__file__))
DATABASEPATH = os.path.join(basepath,'database','plex_database.db')


def init_db():
    conn = sqlite3.connect(DATABASEPATH)
    c = conn.cursor()
    table_sql = """CREATE TABLE IF NOT EXISTS available_dls (
     seedbox_name text NOT NULL,
     last_update_date date DEFAULT (datetime('now','localtime')),
     is_file integer DEFAULT 0,
     downloaded integer DEFAULT 0
     )"""
    downloads = """CREATE TABLE IF NOT EXISTS downloads (
     seedbox_name text NOT NULL,
     size integer NOT NULL,
     insert_date date DEFAULT (datetime('now','localtime')),
     download_state text DEFAULT 'QUEUED',
     download_path text DEFAULT 'Not Downloaded',
     downloaded integer DEFAULT 0,
     is_movie integer DEFAULT 0,
     download_start date DEFAULT NULL,
     download_date date DEFAULT NULL,
     is_file integer DEFAULT 0
     )"""
    c.execute(table_sql)
    c.execute(downloads)
def get_connection():
    conn = sqlite3.connect(DATABASEPATH)
    return conn

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size
if __name__ == '__main__':
    init_db()
