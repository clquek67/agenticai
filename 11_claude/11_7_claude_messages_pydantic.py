import json
from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv(override=True)

client = Anthropic()


class BookRecommendation(BaseModel):
    title: str
    author: str
    genre: str
    reason: str


# Use a tool with a matching schema to force structured JSON output
tools = [
    {
        "name": "recommend_book",
        "description": "Recommend a book with structured details.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Book title"},
                "author": {"type": "string", "description": "Author name"},
                "genre": {"type": "string", "description": "Book genre"},
                "reason": {"type": "string", "description": "Why this book is recommended"},
            },
            "required": ["title", "author", "genre", "reason"],
        },
    }
]

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,
    tools=tools,
    tool_choice={"type": "tool", "name": "recommend_book"},
    messages=[
        {"role": "user", "content": "Recommend a great science fiction book for a beginner."}
    ],
)

tool_use_block = next(b for b in response.content if b.type == "tool_use")
book = BookRecommendation(**tool_use_block.input)

print(f"Title:  {book.title}")
print(f"Author: {book.author}")
print(f"Genre:  {book.genre}")
print(f"Reason: {book.reason}")
print()
print("Raw JSON:", json.dumps(tool_use_block.input, indent=2))
