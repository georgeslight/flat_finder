import json
import logging
import os
from typing import List, Optional
from datetime import datetime
from mongo.user_db import get_user, User
import openai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import datetime

load_dotenv(dotenv_path="../.env")

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


def calculate_age(birthdate: datetime.date) -> int:
    today = datetime.date.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))


def filter_apartments(user_data: User, apartments=None):
    if apartments is None:
        apartments = load_apartments()
    logger.info("Received request to notify apartment")
    if not apartments:
        logger.error("Could not load apartment data.")
        raise HTTPException(status_code=500, detail="Could not load apartment data.")

    fitting_apartments = []
    user_preferences = user_data.apartment_preferences
    user_age = calculate_age(user_data.date_of_birth)

    for apartment in apartments:
        id = apartment.get("ID")
        miete = apartment.get("Gesamtmiete")
        ort = apartment.get("Ort")
        zimmergroesses = apartment.get("Zimmergröße")
        frei_absa = apartment.get("frei ab")
        wg_groesse = apartment.get("WG_groesse")
        mitbewohnern_geschlecht = apartment.get("Mitbewohnern_Geschlecht")
        gesuchte_alter_min = apartment.get("Gesuchte_Alter")[0]
        gesuchte_alter_max = apartment.get("Gesuchte_Alter")[1]
        mitbewohner_alter_min = apartment.get("Mitbewohner_Alter")[0]
        mitbewohner_alter_max = apartment.get("Mitbewohner_Alter")[1]
        gesuchte_geschlecht = apartment.get("Gesuchte_Geschlecht")
        smoking = apartment.get("smoking")

        print(miete, id, ort, zimmergroesses, frei_absa, wg_groesse, mitbewohnern_geschlecht, gesuchte_alter_min, gesuchte_alter_max, mitbewohner_alter_min, mitbewohner_alter_max, gesuchte_geschlecht, smoking)

        try:
            gesamtmiete = int(apartment.get("Gesamtmiete", "0€").replace("€", "").strip())
            zimmergroesse = int(apartment.get("Zimmergröße", "0m²").replace("m²", "").strip())
            frei_ab_str = apartment.get("frei ab", "")
            frei_ab = datetime.datetime.strptime(frei_ab_str, "%Y-%m-%d").date() if frei_ab_str else None
            ready_to_move_in = datetime.datetime.strptime(user_preferences.ready_to_move_in, "%Y-%m-%d").date()
        except ValueError:
            logger.warning(f"Skipping apartment with invalid data: {apartment}")
            continue
        print(apartment.get("frei bis"))

        # Check if the apartment fits the user's preferences
        if (
                gesamtmiete <= user_preferences.max_rent and
                apartment.get("Ort") in user_preferences.bezirk and
                zimmergroesse >= user_preferences.min_size and
                (frei_ab is None or frei_ab <= ready_to_move_in) and
                (user_preferences.smoking_ok or not apartment.get("smoking", False)) and
                (
                        user_preferences.preferred_roommates_sex == "Egal" or user_preferences.preferred_roommates_sex ==
                        apartment.get("Mitbewohnern_Geschlecht", "Egal")
                ) and
                (apartment.get("Gesuchte_Alter", [0, 100])[0] <= user_age <= apartment.get("Gesuchte_Alter", [0, 100])[1]) and
                (user_preferences.preferred_roommate_age[0]<=apartment.get("Mitbewohner_Alter", [0, 100])[0]) and (user_preferences.preferred_roommate_age[1]>=apartment.get("Mitbewohner_Alter", [0, 100])[1])
        ):
            fitting_apartments.append(apartment)

    print(f"gesuchteAlter:{apartment.get("Gesuchte_Alter", [0, 100])[0]}")
    print(f"gesuchteAlter:{apartment.get("Gesuchte_Alter", [0, 100])[1]}")
    print(f"userAge:{user_age}")

    if not fitting_apartments:
        logger.info("No matching apartments found.")
        return {"message": "No matching apartments found."}

    logger.info(f"Matching apartments found: {len(fitting_apartments)}")
    return {"fitting_apartments": fitting_apartments}


# Example test call
user = get_user("5")
user.apartment_preferences.ready_to_move_in = "2023-11-01"  # Ensure date format is string
apartments = [
    {
        "ID": 11,
        "Link": "https://www.wg-gesucht.de/wg-zimmer-in-Berlin-Kreuzberg.11072022.html",
        "Ort": "Kreuzberg",
        "Straße": "Gneisenaustraße 10",
        "PLZ": "10961",
        "Zimmergröße": "25m²",
        "Gesamtmiete": "690€",
        "Miete": "600€",
        "Nebenkosten": "90€",
        "Sonstige Kosten": "n.a.",
        "Kaution": "700€",
        "Ablösevereinbarung": "n.a.",
        "frei ab": "2023-11-01",
        "frei bis": None,
        "Anzeige Datum": "2024-06-21 19:47:23",
        "features": [
            "Altbau",
            "2. OG",
            "möbliert",
            "Badewanne",
            "Parkett",
            "Zentralheizung",
            "Bewohnerparken",
            "5 Minuten zu Fuß entfernt",
            "Waschmaschine",
            "pet-friendly",
            "viel natürliches Licht"
        ],
        "tab_contents": [
            "Dein sonniges Zimmer befindet sich in einer voll möblierten Altbauwohnung in Berlin-Kreuzberg. Vor dem Haus hält die U-Bahnlinie 7. Es gibt ein Bad, eine Küche mit Kühlschrank, Waschmaschine und Flur. 10 Minuten sind es bis zum Alexanderplatz. Vereinbare einen Termin mit Natalie und Jo und sende uns Deinen Einkommensnachweis per whatsapp (siehe Kontaktinformationen).",
            "U-Bahnhof Gneisenaustraße",
            "Wir sprechen Deutsch und Englisch."
        ],
        "Wohnungsgröße": "90",
        "WG_groesse": "3",
        "Mitbewohnern_Geschlecht": "Egal",
        "WG_Art": [
            "Studenten-WG",
            "Berufstätigen-WG"
        ],
        "Gesuchte_Geschlecht": "Egal",
        "Gesuchte_Alter": [
            20,
            35
        ],
        "Mitbewohner_Alter": [
            20,
            35
        ],
        "smoking": True
    },
    {
        "ID": 12,
        "Link": "https://www.wg-gesucht.de/wg-zimmer-in-Berlin-Neukoelln.11073450.html",
        "Ort": "Neukölln",
        "Straße": "Sonnenallee 101",
        "PLZ": "12045",
        "Zimmergröße": "22m²",
        "Gesamtmiete": "700€",
        "Miete": "620€",
        "Nebenkosten": "80€",
        "Sonstige Kosten": "n.a.",
        "Kaution": "700€",
        "Ablösevereinbarung": "n.a.",
        "frei ab": "2023-11-01",
        "frei bis": None,
        "Anzeige Datum": "2024-06-21 19:47:40",
        "features": [
            "Altbau",
            "1. OG",
            "möbliert",
            "Dusche",
            "Parkett",
            "Zentralheizung",
            "Bewohnerparken",
            "3 Minuten zu Fuß entfernt",
            "Waschmaschine",
            "viel natürliches Licht"
        ],
        "tab_contents": [
            "Das sonnige Zimmer befindet sich in einer voll möblierten Altbauwohnung in Berlin-Neukölln. Vor dem Haus hält die U-Bahnlinie 8. Es gibt ein Bad, eine Küche mit Kühlschrank, Waschmaschine und Flur. 15 Minuten sind es bis zum Alexanderplatz. Vereinbare einen Termin mit Alex und Maria und sende uns Deinen Einkommensnachweis per whatsapp (siehe Kontaktinformationen).",
            "U-Bahnhof Hermannplatz",
            "Wir sprechen Deutsch, Englisch und Französisch."
        ],
        "Wohnungsgröße": "85",
        "WG_groesse": "3",
        "Mitbewohnern_Geschlecht": "Egal",
        "WG_Art": [
            "Studenten-WG",
            "Berufstätigen-WG"
        ],
        "Gesuchte_Geschlecht": "Egal",
        "Gesuchte_Alter": [
            20,
            35
        ],
        "Mitbewohner_Alter": [
            20,
            30
        ],
        "smoking": True
    }
]

filtered_apartments = filter_apartments(user, apartments)
print(filtered_apartments)
