from pathlib import Path
from openai import OpenAI


client = OpenAI(
    base_url="https://one.aios123.com/v1",
    api_key="sk-LR70O3o5qf5L9fIo62Da419a4bEd461bA7AcA3D3056a2310"
)

completion = client.chat.completions.create(
model="gpt-4o-mini",
messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
]
)

print(completion.choices[0].message.content)
