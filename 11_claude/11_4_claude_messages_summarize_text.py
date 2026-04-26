from anthropic import Anthropic
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv(override=True)

client = Anthropic()

reader = PdfReader("Warren_Buffett.pdf")
buffett_text = "".join(page.extract_text() or "" for page in reader.pages)

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,
    system="You are an expert analyst. Summarize documents clearly and concisely.",
    messages=[
        {
            "role": "user",
            "content": f"Please summarize the key ideas from this text in 3-5 bullet points:\n\n{buffett_text[:4000]}"
        }
    ]
)

print(response.content[0].text)
