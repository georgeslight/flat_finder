import datetime
import json
import logging
import os

from dotenv import load_dotenv
from fastapi import HTTPException

from src.mongo.user_db import User

load_dotenv(dotenv_path="../../.env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_apartments():
    pardir_path = os.path.abspath(os.pardir)
    file_path = os.path.join(pardir_path, 'BE\\output.json')
    logging.info(f"Fetching JSON from {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Error loading apartments: {e}")
        return []


def turn_user_to_user_model(user):
    return User(**user)


def calculate_age(birthdate: datetime.date) -> int:
    if birthdate is None:
        logger.error("Birthdate is None. Cannot calculate age.")
        return -1
    try:
        today = datetime.date.today()
        return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    except Exception as e:
        logger.error(f"Error calculating age: {e}")


def filter_apartments(user_data: User, json_apartments=None):
    if json_apartments is None:
        json_apartments = load_apartments()
    logger.info(f"Filtering apartments for User: {user_data.id}")

    if not json_apartments:
        logger.error("No apartment data available.")
        raise HTTPException(status_code=500, detail="Apartment data could not be loaded.")

    apartments = reformat_apartment_data(json_apartments)
    fitting_apartments = []

    user_age = calculate_age(user_data.date_of_birth)
    user_preferences = user_data.apartment_preferences

    for apartment in apartments:
        try:
            gesamtmiete = int(apartment["Gesamtmiete"].replace("€", "").strip())
            zimmergroesse = int(apartment["Zimmergröße"].replace("m²", "").strip())

            if apartment_matches_preferences(apartment, gesamtmiete, zimmergroesse, user_preferences, user_age):
                fitting_apartments.append(apartment)
        except ValueError as e:
            logger.warning(f"Skipping apartment {apartment.get('ID')} due to invalid data: {e}")
        except Exception as e:
            logger.error(f"Unexpected error filtering apartments: {e}")

    if not fitting_apartments:
        logger.info("No matching apartments found.")

    logger.info(f"Matching apartments found: {len(fitting_apartments)}")
    return fitting_apartments


def reformat_apartment(apartment):
    return {
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


def reformat_apartment_data(input_data):
    formatted_apartments = []

    def process_apartment(apartment):
        if isinstance(apartment, dict):
            formatted_apartments.append(reformat_apartment(apartment))
        elif isinstance(apartment, list):
            for nested_apartment in apartment:
                process_apartment(nested_apartment)

    for apartment in input_data:
        process_apartment(apartment)

    return formatted_apartments


def apartment_matches_preferences(apartment, gesamtmiete, zimmergroesse, prefs, user_age):
    rent = gesamtmiete <= prefs.max_rent
    city = ((apartment["Ort"] in prefs.location) or (apartment["Ort"] == "Berlin") or (apartment["Ort"] == ""))
    size = zimmergroesse >= prefs.min_size
    smoking = (prefs.smoking_ok or not apartment["smoking"])
    gender = (prefs.preferred_roommates_sex == "gender_irrelevant" or prefs.preferred_roommates_sex == apartment[
        "Mitbewohnern_Geschlecht"])
    age = (apartment.get("Gesuchte_Alter")[0] <= user_age <= apartment.get("Gesuchte_Alter")[1])
    age_fit = (prefs.preferred_roommate_age[0] <= apartment["Mitbewohner_Alter"][0] <= prefs.preferred_roommate_age[
        1] and
               prefs.preferred_roommate_age[0] <= apartment["Mitbewohner_Alter"][1] <= prefs.preferred_roommate_age[1])
    res = (rent and city and size and smoking and gender and age and age_fit)
    return res