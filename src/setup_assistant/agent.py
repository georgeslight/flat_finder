import logging
from typing import Optional

import openai
import os
import json
from dotenv import load_dotenv
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from openai import OpenAI
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from src.mongo.user_db import User, get_user, handle_date_formating

from src.mongo.user_db import collection, openai_key

# Load environment variables
load_dotenv(dotenv_path=".env")

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
uri = os.getenv('MONGO_URI')
mongo_client = MongoClient(uri, server_api=ServerApi('1'))
collections = mongo_client["Flat_Finder_DB"]["USER"]


def fetch_user_data(user_id: str) -> dict:
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
    }
]

# Create the assistant
assistant = client.beta.assistants.create(
    name="Apartment Recommendation Assistant",
    description="Assists users in finding the perfect apartment based on their preferences.",
    instructions="Use the fetch_user_data function to get information about the user.",
    tools=functions,
    model="gpt-3.5-turbo-0125",
)


function_lookup = {
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
