from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(override=True)

client = Anthropic()

system_prompt = (
    "You are a pirate. You must respond to every message in pirate speak. "
    "Use 'Arrr', 'matey', 'ye', and other pirate phrases. Keep answers brief."
)

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=256,
    system=system_prompt,
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(response.content[0].text)
