# https://fastapi.tiangolo.com/tutorial/first-steps/


import json
import logging
import os
from typing import List, Optional

import openai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv(dotenv_path="../.env")




# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize FastAPI app and logger

class ApartmentPreferences(BaseModel):
    max_rent: int
    location: str
    bezirk: List[str]
    min_size: int
    move_in_date: str
    move_out_date: Optional[str] = None
    features: List[str]


class UserData(BaseModel):
    id: Optional[str] = None
    full_name: str
    phone_number: str
    email: str
    address: dict
    date_of_birth: str
    smoker: bool
    employment: dict
    average_monthly_net_income: int
    pets: bool
    guarantor: bool
    wohnberechtigungsschein: bool
    private_liability_insurance: bool
    apartment_preferences: ApartmentPreferences
    additional_info: Optional[List[str]] = None


def load_apartments():
    try:
        with open('output.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Error loading apartments: {e}")
        return []



def filter_apartments(user_data: UserData):
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
            frei_ab = apartment.get("frei ab", "")

        except ValueError:
            logger.warning(f"Skipping apartment with invalid data: {apartment}")
            continue

        # Check if the apartment fits the user's preferences
        if (
                gesamtmiete <= user_preferences.max_rent and
                apartment.get("Ort") in user_preferences.bezirk and
                zimmergroesse >= user_preferences.min_size and
                frei_ab <= user_preferences.move_in_date
        ):
            fitting_apartments.append(apartment)

    if not fitting_apartments:
        logger.info("No matching apartments found.")
        raise HTTPException(status_code=404, detail="No matching apartments found.")

    logger.info("Matching apartments found.")
    return {"fitting_apartments": fitting_apartments}