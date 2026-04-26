from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(override=True)

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,
    system="You are a creative storyteller. Write vivid, engaging short stories.",
    messages=[
        {
            "role": "user",
            "content": "Write a short story about a robot who discovers music for the first time."
        }
    ]
)

print(response.content[0].text)
