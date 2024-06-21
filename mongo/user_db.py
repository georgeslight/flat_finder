from datetime import date
from typing import List

import openai
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pymongo.mongo_client import MongoClient
import requests
import json
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr

import os

load_dotenv()

mongo_conn_string = os.getenv("MONGODB_CONN_STRING")
openai_key = os.getenv('OPENAI_API_KEY')
mongo_db_data_api_key = os.getenv('MONGO_DB_DATA_API_KEY')
mongo_index = os.getenv('INDEX_NAME')

uri = os.getenv('MONGO_URI')
mongo_client = MongoClient(uri, server_api=ServerApi('1'))
openai_client = openai.OpenAI(api_key=openai_key)
collection = mongo_client["Flat_Finder_DB"]["USER"]

model = "text-embedding-3-small"

try:
    mongo_client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


# Define collection and index name
# db_name = os.getenv('DB_NAME')
# collection_name = os.getenv('USER_COLLECTION')
# atlas_collection = client["Flat_Finder_DB"]["USER"]
# vector_search_index = os.getenv('INDEX_NAME')

class Address(BaseModel):
    street: str
    house_number: int
    zip_code: int
    city: str
    country: str


class ApartmentPreferences(BaseModel):
    max_rent: int
    location: str
    bezirk: List[str]
    min_size: int
    ready_to_move_in: str  # Format: "YYYY-MM"


class User(BaseModel):
    # mongo generates auto Ids. the ID in the USER BaseNodel is the telegram given ID
    id: str
    full_name: str
    phone_number: str
    email: EmailStr
    address: Address
    date_of_birth: date  # Format: "YYYY-MM-DD"
    smoker: bool
    employment_type: str
    average_monthly_net_income: int
    pets: bool
    languages: List[str]
    apartment_preferences: ApartmentPreferences
    additional_info: List[str]


def get_embedding(text_list: List[str]) -> List[float]:
    # Concatenate the list into a single string, as OpenAI embedding usually works with text input.
    combined_text = " ".join(text_list)
    responses = openai_client.embeddings.create(input=[combined_text], model=model)
    return responses.data[0].embedding


def save_user(users: User):
    # Convert datetime.date to string in the user data
    user_dict = users.dict()

    # Convert date_of_birth to string
    user_dict['date_of_birth'] = user_dict['date_of_birth'].isoformat()

    # Convert additional_info embeddings
    embedded_info = get_embedding(users.additional_info)
    user_dict['additional_info_embedding'] = embedded_info

    collection.insert_one(user_dict)


def update_user(users: User):
    # Convert datetime.date to string in the user data
    user_dict = users.dict()

    # Convert date_of_birth to string
    user_dict['date_of_birth'] = user_dict['date_of_birth'].isoformat()

    # Convert additional_info embeddings
    embedded_info = get_embedding(users.additional_info)
    user_dict['additional_info_embedding'] = embedded_info

    collection.update_one({"id": users.id}, {"$set": user_dict})


def get_user(user_id: str):
    user = collection.find_one({"id": user_id})
    if user:
        user['date_of_birth'] = date.fromisoformat(user['date_of_birth'])
        return User(**user)
    return None


def get_all_user():
    user_collection = collection.find()
    users = []
    for user_x in user_collection:
        if user_collection:
            user_x['date_of_birth'] = date.fromisoformat(user_x['date_of_birth'])
            users.append(User(**user_x))
    return users


# ------------------------------------------------------------- #

# EXAMPLES!!!

user_data = {
    "id": "1",
    "full_name": "Anna Schmidt",
    "phone_number": "+49123456789",
    "email": "anna.schmidt@example.com",
    "address": {
        "street": "Example Street",
        "house_number": 12,
        "zip_code": 12345,
        "city": "Munich",
        "country": "Germany"
    },
    "date_of_birth": "1995-05-10",
    "employment_type": "Full-time",
    "average_monthly_net_income": 3500,
    "smoker": False,
    "pets": False,
    "languages": ["English", "German"],
    "apartment_preferences": {
        "max_rent": 800,
        "location": "Berlin",
        "bezirk": ["Mitte", "Friedrichshain", "Prenzlauer Berg"],
        "min_size": 15,
        "ready_to_move_in": "2021-09"
    },
    "additional_info": [
        "Relocating for a new job.",
        "like vegan food",
        "love jazz music",
        "enjoy running",
        "looking for a quiet place to work from home",
        "speak English and German fluently",
        "looking for a wg room with only female roommates",
        "I rather have a fully furnished Room",
        "I need fast internet connection for my job"
    ]
}

user = User(**user_data)
#save_user(user)

update_user_data_old = {
    "id": "2",
    "full_name": "Anna Schmidt",
    "phone_number": "+49123456789",
    "email": "anna.schmidt@example.com",
    "address": {
        "street": "Example Street",
        "house_number": 12,
        "zip_code": 12345,
        "city": "Munich",
        "country": "Germany"
    },
    "date_of_birth": "1995-05-10",
    "employment_type": "Full-time",
    "average_monthly_net_income": 3500,
    "smoker": False,
    "pets": False,
    "languages": ["English", "German"],
    "apartment_preferences": {
        "max_rent": 800,
        "location": "Berlin",
        "bezirk": ["Mitte", "Friedrichshain", "Prenzlauer Berg"],
        "min_size": 15,
        "ready_to_move_in": "2021-09"
    },
    "additional_info": [
        "Relocating for a new job.",
        "like vegan food",
        "love jazz music",
        "enjoy running",
        "looking for a quiet place to work from home",
        "speak English and German fluently",
        "looking for a wg room with only female roommates",
        "I rather have a fully furnished Room",
        "I need fast internet connection for my job"
    ]
}

updated_user_data_new = {
    "id": "2",
    "full_name": "Anna Schmidt",
    "phone_number": "+49123456789",
    "email": "anna.schmidt@example.com",
    "address": {
        "street": "Example Street",
        "house_number": 12,
        "zip_code": 12345,
        "city": "Munich",
        "country": "Germany"
    },
    "date_of_birth": "1995-05-10",
    "employment_type": "Full-time",
    "average_monthly_net_income": 2500,
    "smoker": False,
    "pets": False,
    "languages": ["English", "German"],
    "apartment_preferences": {
        "max_rent": 900,
        "location": "Berlin",
        "bezirk": ["Mitte", "Friedrichshain", "Prenzlauer Berg"],
        "min_size": 15,
        "ready_to_move_in": "2021-09"
    },
    "additional_info": [
        "Relocating for a new job.",
        "like vegan food",
        "love jazz music",
        "enjoy running",
        "looking for a quiet place to work from home",
        "speak English and German fluently",
        "looking for a wg room with only female roommates",
        "I rather have a fully furnished Room",
        "I need fast internet connection for my job"
    ]
}

updated_user_old = User(**update_user_data_old)
updated_user = User(**updated_user_data_new)
#save_user(updated_user_old)
#update_user(updated_user)

print(get_user("1"))
print(get_all_user())
