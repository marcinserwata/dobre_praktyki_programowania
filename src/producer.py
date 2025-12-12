import csv
import os
import uuid
import argparse
from datetime import datetime

QUEUE_FILE = os.path.join(os.path.dirname(__file__), "queue.csv")


def ensure_queue_file_exists():
    if not os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "task_name", "status", "created_at", "updated_at"])


def add_task_to_queue(task_name: str = None):
    ensure_queue_file_exists()
    
    task_id = str(uuid.uuid4())[:8]
    if task_name is None:
        task_name = f"Rozmowa telefoniczna #{task_id}"
    
    now = datetime.now().isoformat()
    
    with open(QUEUE_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([task_id, task_name, "pending", now, now])
    
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
