from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(override=True)

client = Anthropic()

print("Claude (streaming): ", end="", flush=True)

with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=512,
    system="You are a helpful assistant.",
    messages=[
        {
            "role": "user",
            "content": "Explain how large language models work in simple terms."
        }
    ]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

print()
