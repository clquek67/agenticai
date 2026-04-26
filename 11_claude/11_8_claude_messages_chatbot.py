from anthropic import Anthropic
from dotenv import load_dotenv
from pypdf import PdfReader
import gradio as gr

load_dotenv(override=True)

client = Anthropic()

reader = PdfReader("Warren_Buffett.pdf")
buffett_text = "".join(page.extract_text() or "" for page in reader.pages)

system_prompt = (
    "You are a helpful assistant knowledgeable about Warren Buffett. "
    "Answer questions based on the following text or from general knowledge.\n\n"
    f"{buffett_text[:4000]}"
)


def chat_with_buffett(message, history):
    messages = []
    for user_msg, assistant_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})
    messages.append({"role": "user", "content": message})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )
    return response.content[0].text


with gr.Blocks() as demo:
    gr.Markdown("# Ask about Warren Buffett (powered by Claude)")

    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="Ask a question about Buffett...")
    clear = gr.Button("Clear")

    def respond(user_message, chat_history):
        answer = chat_with_buffett(user_message, chat_history)
        chat_history.append((user_message, answer))
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

demo.launch()
