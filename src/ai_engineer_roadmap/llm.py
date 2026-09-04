import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise RuntimeError("DEEPSEEK_API_KEY not found")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)


def ask_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )
    content = response.choices[0].message.content
    if content is None:
        return ""

    return content
