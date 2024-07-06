import logging
import os
import time

import openai
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from ai_recommendation import recommend_wg
from src.setup_assistant.agent import submit_tool_outputs, assistant
from structural_filtering import filter_apartments, User
from wg_gesucht_scraper import scrape_wg_gesucht

load_dotenv(dotenv_path="../../.env")

app = FastAPI()

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# assistant_id = assistant.id
assistant_id = os.getenv('ASSISTANT_ID')
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/notify-apartment")
async def notify_apartment(user_data: User):
    return filter_apartments(user_data)


class Message(BaseModel):
    text: str
    thread: str
    user_name: str
    user_id: str


# Scrap and notify user
@app.get("/notify-user")
async def notify_user(user_data: User):
    apartments = scrape_wg_gesucht()
    apartments = filter_apartments(user_data, apartments)
    response = "Recommendations: \n"
    for apt in apartments:
        recommend_wg(apt)
        response += f"{apt}\n"
    return response


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/chat")
async def post_message(user_message: Message):
    # Check for active runs in the thread
    runs = client.beta.threads.runs.list(thread_id=user_message.thread)
    active_run = None
    for run in runs.data:
        if run.status in ["in_progress", "requires_action"]:
            active_run = run
            break

    if active_run:
        # Delete the active run
        client.beta.threads.runs.cancel(thread_id=user_message.thread, run_id=active_run.id)

    # add the message to the thread
    message = client.beta.threads.messages.create(
        thread_id=user_message.thread,
        role="user",
        content=user_message.text,
    )

    # run the assistant
    run = client.beta.threads.runs.create(
        thread_id=user_message.thread,
        assistant_id=assistant_id,
        instructions=f"Please address the user as {user_message.user_name}. The user_id of this user is: "
                     f"{user_message.user_id}. Use this as user_id for when calling the functions/tools."
    )

    while run.status not in ['completed', 'failed']:
        print(run.status)
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=user_message.thread, run_id=run.id)
        if run.status == 'requires_action':
            logging.info(f"User {user_message.user_name} has requested action.")
            run = submit_tool_outputs(user_message.thread, run.id, run.required_action.submit_tool_outputs.tool_calls)

    # the assistants response
    messages = client.beta.threads.messages.list(
        thread_id=user_message.thread
    )

    logging.info(f"Messages: {messages}")

    # returns assistants response
    return messages.data[0].content[0].text.value


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=4000)

# Test function to call the endpoint with dummy_user
