import json
import logging
import os
from typing import Optional

import openai
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from src.BE.ai_recommendation import recommend_wg
from src.BE.structural_filtering import filter_apartments
from src.mongo.user_db import handle_date_formating, get_user, User

load_dotenv(dotenv_path=".env")

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
uri = os.getenv('MONGO_URI')
mongo_client = MongoClient(uri, server_api=ServerApi('1'))
collections = mongo_client["Flat_Finder_DB"]["USER"]


def fetch_flats(user_id: str):
    pardir_path = os.path.abspath(os.pardir)
    file_path = os.path.join(pardir_path, 'FE\\output.json')
    logging.info(f"Fetching JSON from {file_path}")
    flats = None
    try:
        with open(file_path, 'r') as file:
            flats_data = json.load(file)
            flats = flats_data
    except FileNotFoundError:
        logging.info(f"File {file_path} not found.")
        return []
    except json.decoder.JSONDecodeError:
        logging.info(f"Error decoding JSON from file {file_path}.")
        return []

    user = get_user(user_id)
    if user is None:
        raise ValueError(f"No user found with id {user_id}")

    filtered_flats = None
    try:
        filtered_flats = filter_apartments(user, flats)
    except Exception as e:
        logging.error(f"An error occurred while filtering apartments: {e}")

    recommendations = []
    if filtered_flats:
        logging.info(f"Found {len(filtered_flats)} apartments.")
        for apt in filtered_flats:
            recommendation = recommend_wg(user, apt)
            if recommendation is not None:
                recommendations.append(recommendation)
    else:
        return "No new apartments found."

    return recommendations if recommendations else "No new apartments found."


def fetch_user(user_id: str) -> dict:
    user: Optional[User] = get_user(user_id)
    if user is None:
        raise ValueError(f"No user found with id {user_id}")

    user_dict = user.dict()
    user_dict = handle_date_formating(user, user_dict)
    return user_dict


functions = [
    {
        "type": "function",
        "function": {
            "name": "fetch_flats",
            "description": "This function returns a JSON list of new listed flats."
                           "With a ai generated message, the message contains an explication why its the best fit"
                           "for the user, and an example application text for the user to apply for the flat."
                           "This function requires a parameter user_id. Use the default id given.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The default user id"
                    },
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_user",
            "description": "get a user dictionary, with all information about the user looking for apartments, "
                           "and their apartment preferences in the field apartment_preferences its looking for. "
                           "This function requires a parameter user_id. Use the default id given.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The ID of the user to look for"
                    },
                },
                "required": ["user_id"]
            }
        }
    },
]

# Create the assistant
assistant = client.beta.assistants.create(
    name="Flat Search Assistant",
    description="Assists users in finding the perfect apartment based on their preferences.",
    instructions="When the user asks for their information, look in the function fetch_user, there you can find"
                 "information about the current user and in the field apartment_preferences, all the criteria for the "
                 "flats its looking for. When the user asks if there are new flats available, look into the function"
                 "fetch_flats. This function already fetches flats that match the current user, and returns also a"
                 "message with it, explaining why its the best match for him. Both of this functions require a"
                 "parameter, use the default user_id given.",
    tools=functions,
    model="gpt-3.5-turbo-0125",
)

function_lookup = {
    "fetch_flats": fetch_flats,
    "fetch_user": fetch_user,
}


def submit_tool_outputs(thread_id, run_id, tools_to_call):
    tool_output_array = []
    for tool in tools_to_call:
        output = None
        tool_call_id = tool.id
        logging.info(f"Submitting tool {tool_call_id}")
        function_name = tool.function.name
        logging.info(f"Function name: {function_name}")
        function_args = json.loads(tool.function.arguments)
        logging.info(f"Function arguments: {function_args}")
        function_to_call = function_lookup[function_name]
        output = function_to_call(**function_args)
        logging.info(f"Output: {output}")
        if output:
            tool_output_array.append({"tool_call_id": tool_call_id, "output": json.dumps(output)})

    response = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_output_array
    )
    logging.info(f"Submit tool outputs response: {response}")
    return response
