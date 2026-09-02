tasks = [
    {
        "id": 1,
        "title": "Learn Python",
        "priority": "high",
        "completed": False,
    },
    {
        "id": 2,
        "title": "Watch Netflix",
        "priority": "low",
        "completed": False,
    },
    {
        "id": 3,
        "title": "Build AI Agent",
        "priority": "high",
        "completed": False,
    },
]


def get_tasks():
    return tasks


def create_task(task_id, title, priority):
    task = {"id": task_id, "title": title, "priority": priority, "completed": False}
    tasks.append(task)


def complete_task(task_id):
    for task in get_tasks():
        if task["id"] == task_id:
            task["completed"] = True


def get_high_priority_tasks():
    result = []
    for task in get_tasks():
        if task["priority"] == "high" and not task["completed"]:
            result.append(task)
    return result


def delete_task(task_id):
    for task in get_tasks():
        if task["id"] == task_id:
            tasks.remove(task)
            break


def get_task_by_id(task_id):
    for task in get_tasks():
        if task["id"] == task_id:
            return task
    return None


def get_task_stats():
    total = len(get_tasks())
    completed = sum(1 for task in get_tasks() if task["completed"])
    pending = total - completed
    high_priority = sum(
        1
        for task in get_tasks()
        if task["priority"] == "high" and not task["completed"]
    )
    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "high_priority": high_priority,
    }



if __name__ == "__main__":
    task = get_task_by_id(3)
    print(task)

    print("=== Before Delete ===")

    for task in get_tasks():
        print(f"[{task['id']}] {task['title']}")

    delete_task(2)

    print("=== After Delete ===")

    for task in get_tasks():
        print(f"[{task['id']}] {task['title']}")