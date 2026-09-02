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
    task = {
        "id": task_id,
        "title": title,
        "priority": priority,
        "completed": False
    }
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


create_task(4, "Learn FastAPI", "medium")

print("=== All Tasks ===")

for task in get_tasks():
    print(
        f'[{task["id"]}] '
        f'{task["title"]} '
        f'priority={task["priority"]} '
        f'completed={task["completed"]}'
    )

print("=== Before ===")
for task in get_high_priority_tasks():
    print(f'[{task["id"]}] {task["title"]}')

complete_task(1)

print("=== After ===")
for task in get_high_priority_tasks():
    print(f'[{task["id"]}] {task["title"]}')
