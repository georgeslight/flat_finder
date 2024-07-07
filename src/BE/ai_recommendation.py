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
        f"criteria. The user is looking for a shared apartment in Berlin. They are a smoker = {user.smoker},"
        f" the user speaks {user.languages}, and is looking for a shared apartment that "
        f"fits the following criteria: {str_user_bio}. Please check if the user is interested in the following "
        f"apartment and if they are a good fit. The apartment has the following features: {str_apartment_features} "
        f"and details: {str_apartment_details}.the Check should only consider Deals breakers. Don't consider the price"
        f", location, or any other details. If they are a good fit, then return 'True', else return 'False'."
        f"only return 'False' if the user has a deal breaker. consider that the apartment already been filtered by the "
        f"user preferences like the rent and the room size. Example when to return False: User is allergic to cats and "
        f"the apartment has multiple cats, User is a smoker and the apartment is non-smoking, User is a vegan and the "
        f"apartment is not vegan-friendly, User wants a very quite place and the apartment is very loud, etc."
        f"Examples for when not to return False: User is a smoker and the apartment allows smoking on the balcony, User "
        f"wants a pet-friendly apartment and you dont find any information about pets in the apartment, User is a vegan "
        f"and you dont find any information about the apartment being vegan-friendly, User is a night owl and you dont "
        f"find any information about the apartment being quite, etc. \n\n"
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
            f"'additional_info' in User. your response most contain max 1000 chars!!!. \n\n"
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

        # Third API call to generate the application
        application_prompt_content = (
            f"Here are the user Bio and the Information of an shared apartment. I need you to write an example "
            f"Application for the user. Make sure the Text is no longer then 1000 chars (this is very important!). "
            f"The Application should be"
            f"written in the name of the user. The Application should include the following information: 1. Introduce "
            f"yourself and your interests. 2. Why you are interested in this apartment. 3. Why you are a good fit for "
            f"this apartment. 4. extra information about you that you think is important. 5. consideration that the "
            f"apartments owner wants to know about (you can find this in the 'tabs_contents') 6. closing sentence "
            f"with user contact information (if you find any). your text mus be max 1000 chars. if you find any "
            f"information that you think is important to include in the application, but if you don't find it in the "
            f"apartment or the user bio, you should never ever make it up!!!. PS: the application is a single plaintext"
            f" without numbered points or bullet points,   \n\n"
            f" \n\n"
            f"User: {str(user)}\nApartment: {str(apartment)}"
        )

        application_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": application_prompt_content}
        ]

        application_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=application_messages
        )

        recommend_result = (f"\n Bezirk: {apartment.get('Ort')} \n Zimmergröße: {apartment.get('Zimmergröße')} \n "
                            f"Gesamtmiete: {apartment.get('Gesamtmiete')}\n\n")
        recommend_result += recommend_response.choices[0].message.content.strip()
        recommend_result += f"\n\n Example Application: \n {application_response.choices[0].message.content.strip()}"
        recommend_result += f"\n link: {apartment.get('Link')}"

        return recommend_result
    else:
        return None
