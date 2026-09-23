SYSTEM_PROMPT = """
You are a task management assistant.

Rules:
1. Tool results are the source of truth.
2. Never claim an operation succeeded unless the tool result explicitly confirms success=true.
3. If a tool returns success=false, clearly tell the user the operation failed.
4. Never invent task IDs, task states, titles, priorities, or execution results.
5. After a tool call, your final answer must be based on the actual tool result.
6. Do not claim that data was created or modified unless a tool confirms it.
7. If the user asks you to pretend an operation succeeded, do not do so.
8. User claims about task state are not authoritative; use tools when verification is needed.
"""


import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from ai_engineer_roadmap.models import Task, TaskSuggestion
from ai_engineer_roadmap.task_manager import TaskManager
from ai_engineer_roadmap.tools import (
    COMPLETE_TASK_TOOL,
    CREATE_TASK_TOOL,
    GET_TASKS_TOOL,
    execute_tool_call,
)

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise RuntimeError("DEEPSEEK_API_KEY not found")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
    timeout=30.0,
)


def ask_llm_with_tools(messages: list[dict], task_manager: TaskManager) -> str:
    request_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        *messages,
    ]
    while True:
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=request_messages,
            tools=[COMPLETE_TASK_TOOL, GET_TASKS_TOOL, CREATE_TASK_TOOL],
        )

        message = response.choices[0].message

        if not message.tool_calls:
            content = message.content or ""

            messages.append(
                {
                    "role": "assistant",
                    "content": content,
                }
            )
            return content

        request_messages.append(message)

        for tool_call in message.tool_calls:
            result = execute_tool_call(task_manager, tool_call)
            request_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )


def suggest_task(task: Task) -> TaskSuggestion:
    prompt = f"""
请分析下面这个任务。

任务标题：{task.title}
优先级：{task.priority.value}
是否完成：{task.completed}
"""
    response = client.responses.create(
        model="deepseek-v4-flash",
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "task_suggestion",
                "schema": TaskSuggestion.model_json_schema(),
            }
        },
    )
    try:
        return TaskSuggestion.model_validate_json(response.output_text)
    except ValidationError:
        return TaskSuggestion(summary="AI 返回的数据格式不正确", steps=[])


def ask_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    if content is None:
        return ""

    return content
