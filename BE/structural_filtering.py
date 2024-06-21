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

load_dotenv(dotenv_path="../.env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize FastAPI app and logger

def load_apartments():
    try:
        with open('output.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Error loading apartments: {e}")
        return []


def filter_apartments(user_data: User, apartments):
    if apartments is None:
        apartments = load_apartments()
    logger.info("Received request to notify apartment")
    if not apartments:
        logger.error("Could not load apartment data.")
        raise HTTPException(status_code=500, detail="Could not load apartment data.")

    fitting_apartments = []

    user_preferences = user_data.apartment_preferences

    for apartment in apartments:
        try:
            gesamtmiete = int(apartment.get("Gesamtmiete", "0€").replace("€", "").strip())
            zimmergroesse = int(apartment.get("Zimmergröße", "0m²").replace("m²", "").strip())
            frei_ab = datetime.strptime(apartment.get("frei ab", ""), "%Y-%m-%d").date()

            # Convert user_preferences.ready_to_move_in to date
            ready_to_move_in = datetime.strptime(user_preferences.ready_to_move_in, "%Y-%m").date()
        except ValueError:
            logger.warning(f"Skipping apartment with invalid data: {apartment}")
            continue

        print(gesamtmiete, zimmergroesse, frei_ab, apartment.get("Ort"))
        print(user_preferences.max_rent, user_preferences.bezirk, user_preferences.min_size, ready_to_move_in)

        # Check if the apartment fits the user's preferences
        if (
                gesamtmiete <= user_preferences.max_rent and
                apartment.get("Ort") in user_preferences.bezirk and
                zimmergroesse >= user_preferences.min_size and
                frei_ab <= ready_to_move_in
        ):
            fitting_apartments.append(apartment)

    if not fitting_apartments:
        logger.info("No matching apartments found.")
        return {"message": "No matching apartments found."}

    logger.info("Matching apartments found.")
    return {"fitting_apartments": fitting_apartments}


print(filter_apartments(get_user("5"), load_apartments()))
