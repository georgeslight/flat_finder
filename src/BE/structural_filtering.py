import json
import logging
from datetime import datetime

from src.mongo.user_db import User
from dotenv import load_dotenv
from fastapi import HTTPException
import datetime

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

        print(miete, id, ort, zimmergroesses, frei_absa, wg_groesse, mitbewohnern_geschlecht, gesuchte_alter_min,
              gesuchte_alter_max, mitbewohner_alter_min, mitbewohner_alter_max, gesuchte_geschlecht, smoking)
        print(user_preferences.max_rent, user_preferences.bezirk, user_preferences.min_size, user_preferences.ready_to_move_in,
              user_preferences.preferred_roommate_age, user_preferences.preferred_roommates_sex, user_preferences.smoking_ok)
        try:
            gesamtmiete = int(apartment.get("Gesamtmiete", "0€").replace("€", "").strip())
            zimmergroesse = int(apartment.get("Zimmergröße", "0m²").replace("m²", "").strip())
            frei_ab_str = apartment.get("frei ab", "")
            frei_ab = datetime.datetime.strptime(frei_ab_str, "%Y-%m-%d").date() if frei_ab_str else None
            #ready_to_move_in = datetime.datetime.strptime(user_preferences.ready_to_move_in, "%Y-%m-%d").date() todo: fix this
        except ValueError:
            logger.warning(f"Skipping apartment with invalid data: {apartment}")
            continue
        print(apartment.get("frei bis"))

        # Check if the apartment fits the user's preferences
        if (
                gesamtmiete <= user_preferences.max_rent and
                apartment.get("Ort") in user_preferences.bezirk and
                zimmergroesse >= user_preferences.min_size and
                #(frei_ab is None or frei_ab <= ready_to_move_in) and todo: fix this
                (user_preferences.smoking_ok or not apartment.get("smoking", False)) and
                (
                        user_preferences.preferred_roommates_sex == "Egal" or user_preferences.preferred_roommates_sex ==
                        apartment.get("Mitbewohnern_Geschlecht", "Egal")
                ) and
                (apartment.get("Gesuchte_Alter", [0, 100])[0] <= user_age <= apartment.get("Gesuchte_Alter", [0, 100])[
                    1]) and
                (user_preferences.preferred_roommate_age[0] <= apartment.get("Mitbewohner_Alter", [0, 100])[0]) and (
                user_preferences.preferred_roommate_age[1] >= apartment.get("Mitbewohner_Alter", [0, 100])[1])
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


# # Example test call
# user = get_user("188")


