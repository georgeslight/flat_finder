# https://fastapi.tiangolo.com/tutorial/first-steps/

import os
import openai
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

openai.api_key = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(api_key=openai.api_key)

assistant_id = os.getenv('ASSISTANT_ID')


class Message(BaseModel):
    text: str
    thread: str
    user_name: str


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

    # run steps
    run_steps = client.beta.threads.runs.steps.list(
        thread_id=user_message.thread,
        run_id=run.id
    )

    # checks if tool was used
    if len(run_steps.data) > 1:
        # if tool was used, steps are printed
        print(run_steps.data[1].step_details.tool_calls[0].code_interpreter.input)

    # returns assistants response
    return messages.data[0].content[0].text.value


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=4000)
