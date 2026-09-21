import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from ai_engineer_roadmap.models import Task, TaskSuggestion

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise RuntimeError("DEEPSEEK_API_KEY not found")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
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
