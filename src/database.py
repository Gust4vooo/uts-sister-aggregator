import sqlite3
import os

# Menentukan lokasi file database di dalam folder src
DB_FILE = os.path.join(os.path.dirname(__file__), "dedup_store.db")

def init_db():
    # Membuat tabel
    with sqlite3.connect(DB_FILE) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS processed_events (
                topic TEXT NOT NULL,
                event_id TEXT NOT NULL,
                PRIMARY KEY (topic, event_id)
            )
        """)
        con.commit()

def is_duplicate(event_topic: str, event_id: str) -> bool:
    # Memasukkan event ke database
    try:
        with sqlite3.connect(DB_FILE) as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO processed_events (topic, event_id) VALUES (?, ?)",
                (event_topic, event_id)
            )
            con.commit()
            return False  # Berhasil insert, berarti event baru
    except sqlite3.IntegrityError:
        # Gagal insert karena PRIMARY KEY constraint, berarti duplikat
        return True