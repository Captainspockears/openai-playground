from openai import OpenAI, file_from_path
import os
import time
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("MODEL") or "gpt-3.5-turbo"
API_KEY = os.getenv("OPENAI_API_KEY")

# Check if API_KEY is set
if API_KEY is None:
    raise ValueError("OPENAI_API_KEY not set in the environment variables.")

client = OpenAI(api_key=API_KEY)

print("Model used:", MODEL)
print("Client:", client)

file = client.files.create(
    file=file_from_path("camping_brochure.pdf"),
    purpose="assistants",
)

assistant = client.beta.assistants.create(
    name="Nature Inspires Chatbot",
    instructions="You are a chatbot that helps visitors get their queries resolved regarding Nature Inspire's farm - Chiguru Ecospace. Use the knowledge from the brochure uploaded in the retrieval to answer the queries.",
    file_ids=[
        file.id,
    ],
    tools=[
        {"type": "retrieval"}
    ],
    model=MODEL
)

thread = client.beta.threads.create()

print(f"Assistant ID: {assistant.id}")
print(f"Thread ID: {thread.id}\n")

print("Nature Inspires Chatbot: ")

while True:
    message = input("\nYou: ")
    print()

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message,
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    while True:
        run = client.beta.threads.runs.retrieve(
            run_id=run.id,
            thread_id=thread.id,
        )

        if run.status not in ["queued", "in_progress", "cancelling"]:
            break

        time.sleep(1)

    messages = client.beta.threads.messages.list(
        thread_id=thread.id,
        limit=1,
    )
    print("Nature Inspires Chatbot: " + messages.data[0].content[0].text.value)