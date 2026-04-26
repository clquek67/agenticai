# pip install anthropic python-dotenv
# pip install -r requirements.txt

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(override=True)

client = Anthropic()

# Basic multi-turn conversation
messages = [
    {
        "role": "user",
        "content": "What is the factorial of 7?"
    },
    {
        "role": "assistant",
        "content": "The factorial of 7 is 5040."
    },
    {
        "role": "user",
        "content": "Now explain how factorial works in simple terms."
    }
]

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="You are a helpful AI assistant who explains answers clearly and concisely.",
    messages=messages
)

print(response)
print(response.content[0].text)

'''
# Ask a challenging IQ-style question
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(override=True)
client = Anthropic()

question_prompt = "Please propose a hard, challenging question to assess someone's IQ. Respond only with the question."

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=256,
    messages=[{"role": "user", "content": question_prompt}]
)

question = response.content[0].text
print(f"Claude Question: {question}")

response2 = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,
    messages=[{"role": "user", "content": question}]
)

answer = response2.content[0].text
print(f"Claude Answer: {answer}")
'''
