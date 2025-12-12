import sqlite3
import os
import uuid
import argparse
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "queue.db")


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_table_exists():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            task_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_task_to_queue(task_name: str = None):
    ensure_table_exists()
    
    task_id = str(uuid.uuid4())[:8]
    if task_name is None:
        task_name = f"Rozmowa telefoniczna #{task_id}"
    
    now = datetime.now().isoformat()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (id, task_name, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (task_id, task_name, "pending", now, now)
    )
    conn.commit()
    conn.close()
    
    print(f"[PRODUCER] Dodano zadanie: {task_name} (ID: {task_id})")
    return task_id


def add_multiple_tasks(count: int):
    print(f"[PRODUCER] Dodawanie {count} zadań do kolejki...")
    for i in range(1, count + 1):
        task_name = f"Rozmowa telefoniczna #{i}"
        add_task_to_queue(task_name)
    print(f"[PRODUCER] Zakończono dodawanie {count} zadań.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Producer - dodaje zadania do kolejki")
    parser.add_argument("-n", "--count", type=int, default=1)
    parser.add_argument("--name", type=str, default=None)
    
    args = parser.parse_args()
    
    if args.count > 1:
        add_multiple_tasks(args.count)
    else:
        add_task_to_queue(args.name)
