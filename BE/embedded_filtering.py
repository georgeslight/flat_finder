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



# def deep_filter(user_data: User, apartments=None):
