import json
import logging
import os

from dotenv import load_dotenv
from openai import OpenAI

from src.mongo.user_db import User

load_dotenv(dotenv_path="../../.env")

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def load_apartments():
    try:
        with open('output.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"error accrued while loading apartments: {e}")
        return []


def recommend_wg(user: User, apartment):
    user_bio = user.additional_info
    str_user_bio = "User Bio: " + ", ".join(user_bio)

    apartment_features = apartment.get("features")
    apartment_details = apartment.get("tab_contents")

    str_apartment_features = "features: " + ", ".join(apartment_features)
    str_apartment_details = "details: " + ", ".join(apartment_details)

    apartment_info = f"Apartment: \n\n{str_apartment_features} \n\n{str_apartment_details}"

    # First API call to check if the user and the apartment are a good fit
    ko_prompt_content = (
        f"Please check if the following user is interested in this shared apartment and if they fit the "
        f"description of the apartment. If they are a good fit, then return 'True', else return 'False'."
        f"Your should be only 'TRUE' or 'FALSE'. if 'FALSE' include the reasons why very briefly \n\n"
        f"{str_user_bio}\n{apartment_info}"
    )

    ko_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": ko_prompt_content}
    ]

    ko_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=ko_messages
    )

    ko_result = ko_response.choices[0].message.content.strip()

    if "true" in ko_result.lower():
        # Second API call to generate the recommendation
        recommend_prompt_content = (  # todo: Debi -> fix and optimize this prompt
            f"write a recommendation for the user for this apartment. The recommendation should be a string and have the"
            f"description: 'you should apply for this apartment because 1. reason 2. reason 3. reason'. your response "
            f"should include the recommendation. consider that the apartment already been filtered by the user "
            f"preferences. only consider the data under 'tabs_contents', 'features' in the apartment. and "
            f"'additional_info' in User. your response most contain max 1500 chars!!!. \n\n"
            f"User: {str_user_bio}\nApartment: {apartment_info}"
        )

        recommend_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": recommend_prompt_content}
        ]

        recommend_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=recommend_messages
        )
        recommend_result = (f"\n Bezirk: {apartment.get('Ort')} \n Zimmergröße: {apartment.get('Zimmergröße')} \n "
                            f"Gesamtmiete: {apartment.get('Gesamtmiete')}\n\n")
        recommend_result += recommend_response.choices[0].message.content.strip()
        recommend_result += f"\n link: {apartment.get('Link')}"

        return recommend_result
    else:
        return None
