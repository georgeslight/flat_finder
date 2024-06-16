# https://fastapi.tiangolo.com/tutorial/first-steps/


import datetime
import json
import logging
import os
from typing import List

import openai
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv(dotenv_path="../.env")

app = FastAPI()

openai.api_key = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(api_key=openai.api_key)

assistant_id = os.getenv('ASSISTANT_ID')


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Address(BaseModel):
    street: str
    house_number: int
    zip_code: int
    city: str
    country: str


class Employment(BaseModel):
    employment_type: str
    employment_start_date: str
    job_title: str
    current_employer: str


class ApartmentPreferences(BaseModel):
    max_rent: int
    location: str
    bezirk: List[str]
    min_size: int  # in square meters
    move_in_date: str
    move_out_date: str
    features: List[str]


class UserData(BaseModel):
    full_name: str
    contact_number: str
    email: str
    address: Address
    date_of_birth: str
    smoker: bool
    employment: Employment
    average_monthly_net_income: int
    reason_for_move: str
    pets: bool
    commercial_use: bool
    guarantor: bool
    wohnberechtigungsschein: bool
    private_liability_insurance: bool
    apartment_preferences: ApartmentPreferences


def load_apartments():
    try:
        with open('output.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Error loading apartments: {e}")
        return []


@app.post("/notify-apartment")
async def notify_apartment(user_data: UserData):
    logger.info("Received request to notify apartment")
    apartments = load_apartments()
    if not apartments:
        logger.error("Could not load apartment data.")
        raise HTTPException(status_code=500, detail="Could not load apartment data.")

    fitting_apartments = []

    user_preferences = user_data.apartment_preferences

    for apartment in apartments:
        try:
            gesamtmiete = int(apartment.get("Gesamtmiete", "0€").replace("€", "").strip())
            zimmergroesse = int(apartment.get("Zimmergröße", "0m²").replace("m²", "").strip())
        except ValueError:
            logger.warning(f"Skipping apartment with invalid data: {apartment}")
            continue

        # Check if the apartment fits the user's preferences
        if (
                gesamtmiete <= user_preferences.max_rent and
                apartment["Ort"] in user_preferences.bezirk and
                zimmergroesse >= user_preferences.min_size and
                all(feature in apartment["features"] for feature in user_preferences.features)
        ):
            fitting_apartments.append(apartment)

    if not fitting_apartments:
        logger.info("No matching apartments found.")
        raise HTTPException(status_code=404, detail="No matching apartments found.")

    logger.info("Matching apartments found.")
    return {"fitting_apartments": fitting_apartments}


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

# Test function to call the endpoint with dummy_user
