import logging

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

from src.mongo.user_db import collection, openai_key

# Load environment variables
load_dotenv(dotenv_path=".env")

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
uri = os.getenv('MONGO_URI')
mongo_client = MongoClient(uri, server_api=ServerApi('1'))
collections = mongo_client["Flat_Finder_DB"]["USER"]


def generate_recommendations(user, apartments):
    vector_store = MongoDBAtlasVectorSearch(
        collections, OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY')), index_name=os.getenv('INDEX_NAME')
    )

    compressor = LLMChainExtractor.from_llm(client)

    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=vector_store.as_retriever()
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


load_dotenv(dotenv_path="../../.env")

functions = [
    {
        "name": "wirte_recommendation",
        "description": "write a recommendation for a user, if the apartment fits the user profile or not.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_data": {"type": "object", "description": "Vectorized User data."},
                "apartments": {"type": "object", "description": "List of available apartments."}
            },
            "required": ["user_data", "apartments"]
        }
    }
]

# Create the assistant
assistant = client.beta.assistants.create(
    name="Apartment Recommendation Assistant",
    description="Assists users in finding the perfect apartment based on their preferences.",
    instructions="Use the generate_recommendations function to recommend apartments based on user preferences.the "
                 "recommendation should be a string an have the following format: 'you should (not) apply for this "
                 "apartment because 1. reason 2. reason 3. reason'. your response should include the recommendation.",
    model="gpt-3.5-turbo-0125",
    tools=[
        {"type": "function", "function": functions[0]}
    ]
)
print(f"Assistant ID: {assistant.id}")


def generate_recommendations_call(user_data, apartments):

    return generate_recommendations(user_data, apartments)


function_lookup = {
    "generate_recommendations": generate_recommendations_call
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
