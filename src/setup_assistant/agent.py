import json
import logging
import os
from typing import Optional

import openai
from dotenv import load_dotenv
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from src.mongo.user_db import handle_date_formating, get_user, User

# Load environment variables
load_dotenv(dotenv_path=".env")

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
uri = os.getenv('MONGO_URI')
mongo_client = MongoClient(uri, server_api=ServerApi('1'))
collections = mongo_client["Flat_Finder_DB"]["USER"]


def generate_recommendations(user, apartments):
    vectorStore = MongoDBAtlasVectorSearch(
        collections, OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY')), index_name=os.getenv('INDEX_NAME')
    )

    compressor = LLMChainExtractor.from_llm(client)

    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=vectorStore.as_retriever()
    )

    recommendations = []

    for apt in apartments:
        score = sum(info in apt['tab_contents'] for info in user['additional_info'])
        recommendations.append({
            'ID': apt['ID'],
            'Link': apt['Link'],
            'Recommendation': f"This apartment matches {score} of your preferences."
        })
    return recommendations


def fetch_user_data(user_id: str) -> dict:
    user: Optional[User] = get_user(user_id)
    if user is None:
        raise ValueError(f"No user found with id {user_id}")

    user_dict = user.dict()
    user_dict = handle_date_formating(user, user_dict)
    return user_dict


def fetch_flats():
    base_path = os.path.dirname(os.path.abspath(__name__))
    file_path = os.path.join(base_path, 'src', 'BE', 'output.json')
    try:
        with open(file_path, 'r') as file:
            flats_data = json.load(file)
            return flats_data
    except FileNotFoundError:
        logging.info(f"File {file_path} not found.")
        return []
    except json.decoder.JSONDecodeError:
        logging.info(f"Error decoding JSON from file {file_path}.")
        return []


# todo:Ghazi (filter flats base in structural data)
def filtered_flats():
    # todo George: get user from current user (no id)
    # apartaments = filter_apartments(get_user(user_id))  # fetch_flats() ->
    return filtered_flats  # in json


functions = [
    # {
    #     "name": "wirte_recommendation",
    #     "description": "write a recommendation for a user, if the apartment fits the user profile or not.",
    #     "parameters": {
    #         "type": "object",
    #         "properties": {
    #             "user_data": {"type": "object", "description": "Vectorized User data."},
    #             "apartments": {"type": "object", "description": "List of available apartments."}
    #         },
    #         "required": ["user_data", "apartments"]
    #     }
    # }
    {
        "type": "function",
        "function": {
            "name": "fetch_user_data",
            "description": "get a user dictionary, with all information about the user looking for apartments, "
                           "and their apartment preferences its looking for",
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
    {
        "type": "function",
        "function": {
            "name": "filtered_flats",
            "description": "fetch a list of all new listed flats in wg-gesucht.com from the last day. get the user recomendations"
                           "base on the field features and tab_contents",
            # "parameters": {
            #     "type": "object",
            #     "properties": {
            #         "user_id": {
            #             "type": "string",
            #             "description": "The ID of the user to look for"
            #         },
            #     },
            #     "required": ["user_id"]
            # }
        }
    }
    #     todo send notification method????? without sending a input to ai
]

# todo better instructions
# Create the assistant
assistant = client.beta.assistants.create(
    name="Apartment Recommendation Assistant",
    description="Assists users in finding the perfect apartment based on their preferences.",
    instructions="Use the fetch_user_data function to get information about the user.",
    tools=functions,
    model="gpt-3.5-turbo-0125",
)


def generate_recommendations_call(user_data, apartments):
    return generate_recommendations(user_data, apartments)


function_lookup = {
    # "generate_recommendations": generate_recommendations_call
    "fetch_user_data": fetch_user_data,

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
