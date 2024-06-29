import json
import logging
from datetime import date
import os
import openai
from bson import ObjectId
from dotenv import load_dotenv
from openai import OpenAI
from src.mongo.user_db import User

load_dotenv(dotenv_path="../../.env")

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_apartments():
    try:
        with open('output.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Error loading apartments: {e}")
        return []


# user_a = {
#     '_id': ObjectId('6677f439242205068f743a26'),
#     'id': '188',
#     'thread_id': '1',
#     'full_name': 'John Doe',
#     'phone_number': '+49123456789',
#     'email': 'john.doe@example.com',
#     'address': {
#         'street': 'Sample Street',
#         'house_number': 10,
#         'zip_code': 10115,
#         'city': 'Berlin',
#         'country': 'Germany'
#     },
#     'date_of_birth': date(1990, 7, 15),
#     'smoker': False,
#     'employment_type': 'Part-time',
#     'average_monthly_net_income': 2000,
#     'languages': ['English', 'German', 'French'],
#     'apartment_preferences': {
#         'max_rent': 1500,
#         'location': 'Berlin',
#         'bezirk': ['Kreuzberg', 'Neukölln', 'Pankow'],
#         'min_size': 10,
#         'ready_to_move_in': '2023-11-01',
#         'preferred_roommates_sex': 'Egal',
#         'preferred_roommate_age': [20, 60],
#         'preferred_roommate_num': 3,
#         'smoking_ok': True
#     },
#     'additional_info': [
#         'Iam allergic to cats',
#         "Iam a student",
#         'Looking for a vibrant community.',
#         'Enjoy cooking and sharing meals.',
#         'Passionate about photography.',
#         'Need a pet-friendly environment.',
#         'Prefer a room with lots of natural light.',
#         'Freelancer working from home.',
#         'Interested in cultural exchanges.',
#         'Fluent in English, German, and French.',
#         'Looking for a long-term stay.'
#     ],
# }
# user_data = User(**user_a)
# apartments = [
#     {
#         "ID": 11,
#         "Link": "https://www.wg-gesucht.de/wg-zimmer-in-Berlin-Kreuzberg.11072022.html",
#         "Ort": "Kreuzberg",
#         "Straße": "Gneisenaustraße 10",
#         "PLZ": "10961",
#         "Zimmergröße": "25m²",
#         "Gesamtmiete": "690€",
#         "Miete": "600€",
#         "Nebenkosten": "90€",
#         "Sonstige Kosten": "n.a.",
#         "Kaution": "700€",
#         "Ablösevereinbarung": "n.a.",
#         "frei ab": "2023-11-01",
#         "frei bis": None,
#         "Anzeige Datum": "2024-06-21 19:47:23",
#         "features": [
#             "Altbau", "2. OG", "möbliert", "Badewanne", "Parkett",
#             "Zentralheizung", "Bewohnerparken", "5 Minuten zu Fuß entfernt",
#             "Waschmaschine", "pet-friendly", "viel natürliches Licht"
#         ],
#         "tab_contents": [
#             "Dein sonniges Zimmer befindet sich in einer voll möblierten Altbauwohnung in Berlin-Kreuzberg. Vor dem Haus hält die U-Bahnlinie 7. Es gibt ein Bad, eine Küche mit Kühlschrank, Waschmaschine und Flur. 10 Minuten sind es bis zum Alexanderplatz. Vereinbare einen Termin mit Natalie und Jo und sende uns Deinen Einkommensnachweis per whatsapp (siehe Kontaktinformationen).",
#             "U-Bahnhof Gneisenaustraße",
#             "Wir sprechen Deutsch und Englisch."
#             "We are looking for a Student"
#             "We have 2 cats"
#         ],
#         "Wohnungsgröße": "90",
#         "WG_groesse": "3",
#         "Mitbewohnern_Geschlecht": "Egal",
#         "WG_Art": ["Studenten-WG", "Berufstätigen-WG"],
#         "Gesuchte_Geschlecht": "Egal",
#         "Gesuchte_Alter": [20, 35],
#         "Mitbewohner_Alter": [20, 35],
#         "smoking": True
#     },
#     {
#         "ID": 12,
#         "Link": "https://www.wg-gesucht.de/wg-zimmer-in-Berlin-Neukoelln.11073450.html",
#         "Ort": "Neukölln",
#         "Straße": "Sonnenallee 101",
#         "PLZ": "12045",
#         "Zimmergröße": "22m²",
#         "Gesamtmiete": "700€",
#         "Miete": "620€",
#         "Nebenkosten": "80€",
#         "Sonstige Kosten": "n.a.",
#         "Kaution": "700€",
#         "Ablösevereinbarung": "n.a.",
#         "frei ab": "2023-11-01",
#         "frei bis": None,
#         "Anzeige Datum": "2024-06-21 19:47:40",
#         "features": [
#             "Altbau", "1. OG", "möbliert", "Dusche", "Parkett",
#             "Zentralheizung", "Bewohnerparken", "3 Minuten zu Fuß entfernt",
#             "Waschmaschine", "viel natürliches Licht"
#         ],
#         "tab_contents": [
#             "Das sonnige Zimmer befindet sich in einer voll möblierten Altbauwohnung in Berlin-Neukölln. Vor dem Haus "
#             "hält die U-Bahnlinie 8. Es gibt ein Bad, eine Küche mit Kühlschrank, Waschmaschine und Flur. 15 Minuten "
#             "sind es bis zum Alexanderplatz. Vereinbare einen Termin mit Alex und Maria und sende uns Deinen "
#             "Einkommensnachweis per whatsapp (siehe Kontaktinformationen).",
#             "U-Bahnhof Hermannplatz",
#             "Wir sprechen Deutsch, Englisch und Französisch."
#         ],
#         "Wohnungsgröße": "85",
#         "WG_groesse": "3",
#         "Mitbewohnern_Geschlecht": "Egal",
#         "WG_Art": ["Studenten-WG", "Berufstätigen-WG"],
#         "Gesuchte_Geschlecht": "Egal",
#         "Gesuchte_Alter": [20, 35],
#         "Mitbewohner_Alter": [20, 30],
#         "smoking": True
#     }
# ]

assistant_id = "asst_3h49BMfT4jf0mMlkQxAXQYjZ"


def recommend_wg(user: User, apartment=None):
    if apartment is None:
        apartment = load_apartments()[0]

    user_bio = user.additional_info
    str_user_bio = "User: " + ", ".join(user_bio)

    apartment_features = apartment.get("features", [])
    apartment_details = apartment.get("tab_contents", [])

    str_apartment_features = "features: " + ", ".join(apartment_features)
    str_apartment_details = "details: " + ", ".join(apartment_details)

    apartment_info = f"{str_apartment_features}, {str_apartment_details}"

    # First API call to check if the user and the apartment are a good fit
    ko_prompt_content = (
        f"Please check if the following user is interested in this shared apartment and if they fit the "
        f"description of the apartment. If they are a good fit, then return 'True', else return 'False'."
        f"Your should be only 'TRUE' or 'FALSE'. if 'FALSE' include the reasons why very briefly \n\n"
        f"User: {str_user_bio}\nApartment: {apartment_info}"
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

    if ko_result == "TRUE":
        # Second API call to generate the recommendation
        recommend_prompt_content = (
            f"write a recommendation for the user for this apartment. The recommendation should be a string and have the"
            f"description: 'you should apply for this apartment because 1. reason 2. reason 3. reason'. your response "
            f"should include the recommendation. consider that the apartment already been filtered by the user "
            f"preferences. only consider the data under 'tabs_contents', 'features' in the apartment. and "
            f"'additional_info' in User. your response most contain max 250 chars!!!. \n\n"
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

        recommend_result = recommend_response.choices[0].message.content.strip()
        recommend_result += f"\n ID: {apartment.get('ID')} \n Bezirk: {apartment.get('Ort')} \n Zimmergröße: {apartment.get('Zimmergröße')} \n Gesamtmiete: {apartment.get('Gesamtmiete')}"
        recommend_result += f"\n\n[{apartment.get('ID')}]({apartment.get('Link')})"

        return recommend_result
    else:
        return "The user and the apartment are not a good fit. AI Output: \n" + ko_response.choices[0].message.content


# print(ko_filter(user_data, apartments[0]))
# print(recommend_wg(user_data, apartments[0]))
