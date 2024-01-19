from openai import OpenAI
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

assistant = client.beta.assistants.create(
    name="Football Facts",
    instructions="You are Football Facts. You have conversations on football (also called soccer). Your favourite team is Arsenal FC. You like to banter about other football teams.",
    tools=[],
    model=MODEL
)

thread = client.beta.threads.create()

print(f"Assistant ID: {assistant.id}")
print(f"Thread ID: {thread.id}\n")

print("Football Facts: ")

while True:
    message = input("You: ")
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
    print("Football Facts: " + messages.data[0].content[0].text.value)