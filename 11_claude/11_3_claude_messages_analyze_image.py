import base64
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(override=True)

client = Anthropic()

image_path = "animals.jpg"

with open(image_path, "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data,
                    },
                },
                {
                    "type": "text",
                    "text": "Describe what you see in this image in detail."
                }
            ],
        }
    ],
)

print(response.content[0].text)
