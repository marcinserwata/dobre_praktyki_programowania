import sqlite3
import os
import time
import argparse
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "queue.db")
TASK_EXECUTION_TIME = 30
CHECK_INTERVAL = 5


def get_connection():
    conn = sqlite3.connect(DB_FILE, timeout=30)
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


def read_all_tasks() -> list[dict]:
    ensure_table_exists()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def update_task_status(task_id: str, new_status: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    cursor.execute(
        "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
        (new_status, now, task_id)
    )
    
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return updated


def get_pending_task() -> dict | None:
    ensure_table_exists()
    
    conn = get_connection()
    conn.isolation_level = 'IMMEDIATE'
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT * FROM tasks WHERE status = 'pending' ORDER BY created_at LIMIT 1"
        )
        row = cursor.fetchone()
        
        if row:
            task = dict(row)
            now = datetime.now().isoformat()
            
            cursor.execute(
                "UPDATE tasks SET status = 'in_progress', updated_at = ? WHERE id = ?",
                (now, task['id'])
            )
            task['status'] = 'in_progress'
            task['updated_at'] = now
            
            conn.commit()
            conn.close()
            return task
        
        conn.close()
        return None
        
    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        print(f"[ERROR] Błąd bazy danych: {e}")
        return None


def execute_task(task: dict, consumer_id: str):
    print(f"[CONSUMER {consumer_id}] Rozpoczynam wykonywanie: {task['task_name']} (ID: {task['id']})")
    print(f"[CONSUMER {consumer_id}] Czas wykonania: {TASK_EXECUTION_TIME}s")
    
    for i in range(TASK_EXECUTION_TIME):
        time.sleep(1)
        if (i + 1) % 10 == 0:
            print(f"[CONSUMER {consumer_id}] Postęp: {i + 1}/{TASK_EXECUTION_TIME}s")
    
    update_task_status(task["id"], "done")
    print(f"[CONSUMER {consumer_id}] Zakończono: {task['task_name']} (ID: {task['id']})")


def get_queue_stats() -> dict:
    tasks = read_all_tasks()
    stats = {"pending": 0, "in_progress": 0, "done": 0, "total": len(tasks)}
    
    for task in tasks:
        status = task.get("status", "unknown")
        if status in stats:
            stats[status] += 1
    
    return stats


def run_consumer(consumer_id: str):
    print(f"[CONSUMER {consumer_id}] Uruchomiony. Sprawdzanie kolejki co {CHECK_INTERVAL}s...")
    print(f"[CONSUMER {consumer_id}] Czas wykonania pojedynczego zadania: {TASK_EXECUTION_TIME}s")
    print("-" * 60)
    
    while True:
        task = get_pending_task()
        
        if task:
            execute_task(task, consumer_id)
            stats = get_queue_stats()
            print(f"[CONSUMER {consumer_id}] Statystyki: pending={stats['pending']}, "
                  f"in_progress={stats['in_progress']}, done={stats['done']}, total={stats['total']}")
            print("-" * 60)
        else:
            stats = get_queue_stats()
            print(f"[CONSUMER {consumer_id}] Brak zadań do wykonania. "
                  f"(pending={stats['pending']}, done={stats['done']}) "
                  f"Sprawdzam ponownie za {CHECK_INTERVAL}s...")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consumer - wykonuje zadania z kolejki")
    parser.add_argument("-id", "--consumer-id", type=str, default="1")
    parser.add_argument("-t", "--task-time", type=int, default=30)
    parser.add_argument("-i", "--interval", type=int, default=5)
    
    args = parser.parse_args()
    
    TASK_EXECUTION_TIME = args.task_time
    CHECK_INTERVAL = args.interval
    
    try:
        run_consumer(args.consumer_id)
    except KeyboardInterrupt:
        print(f"\n[CONSUMER {args.consumer_id}] Zatrzymany przez użytkownika.")
