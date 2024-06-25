from datetime import date
from typing import List, Optional

import openai
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pymongo.mongo_client import MongoClient
import requests
import json
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr, Field

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
    street: Optional[str] = Field(None)
    house_number: Optional[int] = Field(None)
    zip_code: Optional[int] = Field(None)
    city: Optional[str] = Field(None)
    country: Optional[str] = Field(None)


class ApartmentPreferences(BaseModel):
    max_rent: Optional[int] = Field(None)
    location: Optional[str] = Field(None)
    bezirk: List[Optional[str]] = Field(default_factory=list)
    min_size: Optional[int] = Field(None)
    ready_to_move_in: Optional[str] = Field(None)  # Format: "YYYY-MM"
    preferred_roommates_sex: Optional[str] = Field(None)
    preferred_roommate_age: List[Optional[int]] = Field(default_factory=list)
    preferred_roommate_num: Optional[int] = Field(None)
    smoking_ok: Optional[bool] = Field(None)


class User(BaseModel):
    id: int
    thread_id: str
    full_name: Optional[str] = Field(None)
    phone_number: Optional[str] = Field(None)
    email: Optional[EmailStr] = Field(None)
    address: Optional[Address] = Field(default_factory=Address)
    date_of_birth: Optional[date] = Field(None)  # Format: "YYYY-MM-DD"
    smoker: Optional[bool] = Field(False)
    employment_type: Optional[str] = Field(None)
    average_monthly_net_income: Optional[int] = Field(None)
    languages: List[Optional[str]] = Field(default_factory=list)
    apartment_preferences: Optional[ApartmentPreferences] = Field(default_factory=ApartmentPreferences)
    additional_info: List[Optional[str]] = Field(default_factory=list)


def get_empty_user():
    return User(id=0, thread_id="", full_name=None, phone_number=None, email=None, address={
        "street": None,
        "house_number": None,
        "zip_code": None,
        "city": None,
        "country": None
    }, date_of_birth=None, employment_type=None, average_monthly_net_income=None, smoker=False, languages=[],
                apartment_preferences={
                    "max_rent": None,
                    "location": None,
                    "bezirk": [],
                    "min_size": None,
                    "ready_to_move_in": None,
                    "preferred_roommates_sex": None,
                    "preferred_roommate_age": [],
                    "preferred_roommate_num": None,
                    "smoking_ok": False
                }, additional_info=[])


def get_embedding(text_list: List[str]) -> List[float]:
    try:
        # Concatenate the list into a single string, as OpenAI embedding usually works with text input.
        combined_text = " ".join(text_list)
        responses = openai_client.embeddings.create(input=[combined_text], model=model)
        print(reversed(responses.data[0].embedding))
        return responses.data[0].embedding
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


def save_user(users: User):
    user_dict = users.dict()
    if user_dict.get('date_of_birth') is not None:
        user_dict['date_of_birth'] = user_dict['date_of_birth'].isoformat()
    if users.additional_info:
        embedded_info = get_embedding(users.additional_info)
        user_dict['additional_info_embedding'] = embedded_info
    collection.insert_one(user_dict)
    print(f"User saved with id: {user_dict.get('id')}")


def update_user(users: User):
    try:
        # Convert datetime.date to string in the user data
        user_dict = users.dict()
        # Convert date_of_birth to string
        if user_dict.get('date_of_birth') is not None:
            user_dict['date_of_birth'] = user_dict['date_of_birth'].isoformat()
        # Convert additional_info embeddings
        if users.additional_info:
            embedded_info = get_embedding(users.additional_info)
            user_dict['additional_info_embedding'] = embedded_info
        collection.update_one({"id": users.id}, {"$set": user_dict})
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


def get_user(user_id: str):
    try:
        user = collection.find_one({"id": user_id})
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

    if user:
        print(f"User found: {user}")
        try:
            if user['date_of_birth']:
                user['date_of_birth'] = date.fromisoformat(user['date_of_birth'])
            else:
                user['date_of_birth'] = None
        except ValueError as e:
            print(f"Date conversion error: {e}")
            return None

        return User(**user)
    else:
        print(f"No user found with id: {user_id}")
        return None


def get_all_user():
    user_collection = collection.find()
    users = []
    for user_x in user_collection:
        if user_collection:
            user_x['date_of_birth'] = date.fromisoformat(user_x['date_of_birth'])
            users.append(User(**user_x))
    return users

#result = collection.delete_many({})
