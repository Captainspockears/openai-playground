from openai import OpenAI, file_from_path
from twilio.rest import Client
import os
import time
import json
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("MODEL") or "gpt-3.5-turbo"
API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Check if API_KEY is set
if API_KEY is None:
    raise ValueError("OPENAI_API_KEY not set in the environment variables.")


################

RECIPIENT_MAPPER = {
    "ruthuparna": "+918867092264",
    "aditya": "+919449003120",
    "suhruth": "+918722909562",
    "sayak": "+918867092264",
}


def send_sms(recipient_number, message):
    try:
        # Create a Twilio client using your account SID and Auth Token
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # Send the SMS
        message = client.messages.create(
            to=recipient_number, from_=TWILIO_PHONE_NUMBER, body=message
        )

        return {"success": "true"}

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"success": "false"}


################

client = OpenAI(api_key=API_KEY)

print("Model used:", MODEL)
print("Client:", client)

assistant = client.beta.assistants.create(
    name="Messenger Bot",
    instructions="You are a bot that sends messages to recipients. For example, 'Tell Aditya to buy groceries' will send a message 'Buy groceries' to the recipient called 'aditya'. You should also be able to understand nicknames - example, adi is aditya. Match the given recipient name to one of the mentioned enums.",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "sendMessage",
                "description": "Send a message to the recipient",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The message to be sent",
                        },
                        "recipient": {
                            "type": "string",
                            "enum": list(RECIPIENT_MAPPER.keys()),
                        },
                    },
                    "required": ["message", "recipient"],
                },
            },
        }
    ],
    model=MODEL,
)

thread = client.beta.threads.create()

print(f"Assistant ID: {assistant.id}")
print(f"Thread ID: {thread.id}\n")

print("Messenger Bot: ")

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

        # Check if the run requires action (function call)
        if run.status == "requires_action":

            # Assuming there's only one tool call required
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]

            # Extract the tool_call_id
            tool_call_id = tool_call.id

            # Extract the message parameter
            message = json.loads(tool_call.function.arguments)["message"]

            # Extract the recipient parameter
            recipient = json.loads(tool_call.function.arguments)["recipient"]

            # Fetch the number of the recipient
            recipient_number = RECIPIENT_MAPPER[recipient]

            # Send Message
            success = send_sms(recipient_number, message)

            # Submit the tool output to complete the run
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=[
                    {"tool_call_id": tool_call_id, "output": json.dumps(success)}
                ],
            )

        if run.status not in ["queued", "in_progress", "cancelling", "requires_action"]:
            break

        time.sleep(1)

    messages = client.beta.threads.messages.list(
        thread_id=thread.id,
        limit=1,
    )
    print("Messenger Bot: " + messages.data[0].content[0].text.value)
