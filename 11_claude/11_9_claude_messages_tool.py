import json
from anthropic import Anthropic
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv(override=True)

client = Anthropic()

reader = PdfReader("Warren_Buffett.pdf")
buffett_text = "".join(page.extract_text() or "" for page in reader.pages)

# -----------------------------
# 1. Define a callable tool
# -----------------------------
def summarize_text(text: str, length: str = "short") -> str:
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[
            {"role": "user", "content": f"Summarize this text in a {length} way:\n\n{text[:2000]}"}
        ],
    )
    return response.content[0].text


tools = [
    {
        "name": "summarize_text",
        "description": "Summarize the given text concisely.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to summarize"},
                "length": {
                    "type": "string",
                    "enum": ["short", "medium", "long"],
                    "description": "Desired summary length",
                },
            },
            "required": ["text"],
        },
    }
]

# -----------------------------
# 2. Agent loop with tool use
# -----------------------------
def ask_agent(prompt: str) -> str:
    messages = [
        {
            "role": "user",
            "content": f"{prompt}\n\nReference text:\n{buffett_text[:4000]}",
        }
    ]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=(
            "You are an intelligent agent trained on Warren Buffett's writings. "
            "If the question requires deep context, call the summarize_text tool first."
        ),
        tools=tools,
        messages=messages,
    )

    # Handle tool use if the model calls summarize_text
    if response.stop_reason == "tool_use":
        tool_block = next(b for b in response.content if b.type == "tool_use")
        tool_result = summarize_text(**tool_block.input)

        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": tool_result,
                }
            ],
        })

        follow_up = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system="You are a helpful assistant.",
            tools=tools,
            messages=messages,
        )
        return follow_up.content[0].text

    return response.content[0].text


# -----------------------------
# 3. Interactive loop
# -----------------------------
if __name__ == "__main__":
    print("Warren Buffett Agent (powered by Claude)\n(Type 'exit' to quit)\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        answer = ask_agent(user_input)
        print(f"\nAgent: {answer}\n")
