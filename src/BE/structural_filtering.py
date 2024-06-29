import json
import logging
from datetime import datetime

from src.mongo.user_db import User
from dotenv import load_dotenv
from fastapi import HTTPException
import datetime
from datetime import date

load_dotenv(dotenv_path="../../.env")

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


def turn_user_to_user_model(user):
    return User(**user)


def calculate_age(birthdate: datetime.date) -> int:
    today = datetime.date.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))


def reformat_apartment_data(input_data):

    formatted_apartments = []
    for apartment in input_data:
        if isinstance(apartment, dict):  # Ensure we are working with a dictionary
            formatted_apartment = {
                "ID": apartment.get("ID"),
                "Link": apartment.get("Link"),
                "Ort": apartment.get("Ort", ""),
                "Straße": apartment.get("Straße", ""),
                "PLZ": apartment.get("PLZ", ""),
                "Zimmergröße": apartment.get("Zimmergröße", ""),
                "Gesamtmiete": apartment.get("Gesamtmiete", "0€"),
                "Miete": apartment.get("Miete", "0€"),
                "Nebenkosten": apartment.get("Nebenkosten", "0€"),
                "Sonstige Kosten": apartment.get("Sonstige Kosten", "n.a."),
                "Kaution": apartment.get("Kaution", "0€"),
                "Ablösevereinbarung": apartment.get("Ablösevereinbarung", "n.a."),
                "frei ab": apartment.get("frei ab"),
                "frei bis": apartment.get("frei bis"),
                "Anzeige Datum": apartment.get("Anzeige Datum"),
                "features": apartment.get("features", []),
                "tab_contents": apartment.get("tab_contents", []),
                "Wohnungsgröße": apartment.get("Wohnungsgröße"),
                "WG_groesse": apartment.get("WG_groesse"),
                "Mitbewohnern_Geschlecht": apartment.get("Mitbewohnern_Geschlecht"),
                "WG_Art": apartment.get("WG_Art", []),
                "Gesuchte_Geschlecht": apartment.get("Gesuchte_Geschlecht"),
                "Gesuchte_Alter": [int(age) for age in apartment.get("Gesuchte_Alter", ["0", "99"])],
                "Mitbewohner_Alter": [int(age) for age in apartment.get("Mitbewohner_Alter", ["0", "99"])],
                "smoking": apartment.get("smoking", False)
            }
            formatted_apartments.append(formatted_apartment)
        elif isinstance(apartment, list):  # Handle unexpected nested lists
            for nested_apartment in apartment:
                if isinstance(nested_apartment, dict):
                    formatted_apartment = {
                        "ID": nested_apartment.get("ID"),
                        "Link": nested_apartment.get("Link"),
                        "Ort": nested_apartment.get("Ort", ""),
                        "Straße": nested_apartment.get("Straße", ""),
                        "PLZ": nested_apartment.get("PLZ", ""),
                        "Zimmergröße": nested_apartment.get("Zimmergröße", ""),
                        "Gesamtmiete": nested_apartment.get("Gesamtmiete", "0€"),
                        "Miete": nested_apartment.get("Miete", "0€"),
                        "Nebenkosten": nested_apartment.get("Nebenkosten", "0€"),
                        "Sonstige Kosten": nested_apartment.get("Sonstige Kosten", "n.a."),
                        "Kaution": nested_apartment.get("Kaution", "0€"),
                        "Ablösevereinbarung": nested_apartment.get("Ablösevereinbarung", "n.a."),
                        "frei ab": nested_apartment.get("frei ab"),
                        "frei bis": nested_apartment.get("frei bis"),
                        "Anzeige Datum": nested_apartment.get("Anzeige Datum"),
                        "features": nested_apartment.get("features", []),
                        "tab_contents": nested_apartment.get("tab_contents", []),
                        "Wohnungsgröße": nested_apartment.get("Wohnungsgröße"),
                        "WG_groesse": nested_apartment.get("WG_groesse"),
                        "Mitbewohnern_Geschlecht": nested_apartment.get("Mitbewohnern_Geschlecht"),
                        "WG_Art": nested_apartment.get("WG_Art", []),
                        "Gesuchte_Geschlecht": nested_apartment.get("Gesuchte_Geschlecht"),
                        "Gesuchte_Alter": [int(age) for age in nested_apartment.get("Gesuchte_Alter", ["0", "99"])],
                        "Mitbewohner_Alter": [int(age) for age in nested_apartment.get("Mitbewohner_Alter", ["0", "99"])],
                        "smoking": nested_apartment.get("smoking", False)
                    }
                    formatted_apartments.append(formatted_apartment)

    return formatted_apartments


def filter_apartments(user_data: User, json_apartments=None):
    if json_apartments is None:
        json_apartments = load_apartments()
    logger.info(f"Received request to filter apartments for User: {user_data.id}")
    if not json_apartments:
        logger.error("Could not load apartment data.")
        raise HTTPException(status_code=500, detail="Could not load apartment data.")

    apartments = reformat_apartment_data(json_apartments)
    fitting_apartments = []
    user_preferences = user_data.apartment_preferences
    user_age = calculate_age(user_data.date_of_birth)

    for apartment in apartments:
        try:
            try:
                gesamtmiete = int(apartment.get("Gesamtmiete", "0€").replace("€", "").strip())
                zimmergroesse = int(apartment.get("Zimmergröße", "0m²").replace("m²", "").strip())
                #frei_ab_str = apartment.get("frei ab", "")
                #frei_ab = datetime.datetime.strptime(frei_ab_str, "%Y-%m-%d").date() if frei_ab_str else None
                #ready_to_move_in = datetime.datetime.strptime(user_preferences.ready_to_move_in, "%Y-%m-%d").date() todo: fix this
            except ValueError:
                logger.warning(f"Skipping apartment {apartment.get("ID")} with invalid data: {ValueError}")
                continue

            # Check if the apartment fits the user's preferences
            if (
                    gesamtmiete <= user_preferences.max_rent and
                    apartment.get("Ort", "") in user_preferences.bezirk and
                    zimmergroesse >= user_preferences.min_size and
                    #(frei_ab is None or frei_ab <= ready_to_move_in) and todo: fix this
                    (user_preferences.smoking_ok or not apartment.get("smoking", False)) and
                    (
                            user_preferences.preferred_roommates_sex == "gender_irrelevant" or user_preferences.preferred_roommates_sex ==
                            apartment.get("Mitbewohnern_Geschlecht", "gender_irrelevant")
                    ) and
                    (apartment.get("Gesuchte_Alter", [0, 100])[0] <= user_age <=
                     apartment.get("Gesuchte_Alter", [0, 100])[1]) and
                    (user_preferences.preferred_roommate_age[0] <= apartment.get("Mitbewohner_Alter", [0, 100])[0]) and
                    (user_preferences.preferred_roommate_age[1] >= apartment.get("Mitbewohner_Alter", [0, 100])[1])
            ):
                fitting_apartments.append(apartment)
        except Exception as e:
            logger.error(f"Error filtering apartments: {e}")

    if not fitting_apartments:
        logger.info("No matching apartments found.")
        return {"message": "No matching apartments found."}

    logger.info(f"Matching apartments found: {len(fitting_apartments)}")
    if fitting_apartments is None:
        return None
    return {"fitting_apartments": fitting_apartments}

# todo consider the preferred_roommates_sex options in UI