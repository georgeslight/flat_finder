import logging
import os

import openai
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from structural_filtering import filter_apartments, User
from wg_gesucht_scraper import scrap_wg_gesucht
from ai_recommendation import recommend_wg

load_dotenv(dotenv_path="../../.env")

app = FastAPI()

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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


# Scrap and notify user
@app.get("/notify-user")
async def notify_user(user_data: User):
    apartments = scrap_wg_gesucht()
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
    # add the message to the thread
    client.beta.threads.messages.create(
        thread_id=user_message.thread,
        role="user",
        content=user_message.text,
    )
    # run the assistant
    run = client.beta.threads.runs.create(
        thread_id=user_message.thread,
        assistant_id=assistant_id,
        instructions=f"Please address the user as {user_message.user_name}."
    )

    # checks run status
    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=user_message.thread,
            run_id=run.id
        )
        if run.status != "in_progress":
            break

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
