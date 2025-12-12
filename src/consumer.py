import csv
import os
import time
import argparse
from datetime import datetime
from filelock import FileLock

QUEUE_FILE = os.path.join(os.path.dirname(__file__), "queue.csv")
LOCK_FILE = QUEUE_FILE + ".lock"
TASK_EXECUTION_TIME = 30
CHECK_INTERVAL = 5


def read_all_tasks() -> list[dict]:
    if not os.path.exists(QUEUE_FILE):
        return []
    
    with open(QUEUE_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def write_all_tasks(tasks: list[dict]):
    if not tasks:
        return
    
    fieldnames = ["id", "task_name", "status", "created_at", "updated_at"]
    
    with open(QUEUE_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tasks)


def update_task_status(task_id: str, new_status: str) -> bool:
    lock = FileLock(LOCK_FILE)
    
    with lock:
        tasks = read_all_tasks()
        
        for task in tasks:
            if task["id"] == task_id:
                task["status"] = new_status
                task["updated_at"] = datetime.now().isoformat()
                write_all_tasks(tasks)
                return True
    
    return False


def get_pending_task() -> dict | None:
    lock = FileLock(LOCK_FILE)
    
    with lock:
        tasks = read_all_tasks()
        
        for task in tasks:
            if task["status"] == "pending":
                task["status"] = "in_progress"
                task["updated_at"] = datetime.now().isoformat()
                write_all_tasks(tasks)
                return task
    
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
