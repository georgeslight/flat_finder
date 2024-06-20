import openai
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pymongo.mongo_client import MongoClient
import requests
import json
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

import os
load_dotenv()

mongo_client = MongoClient(os.getenv("MONGODB_CONN_STRING"))
openai_Key = os.getenv('OPENAI_API_KEY')
openAi_client = openai.OpenAI(api_key=openai_Key)

model = "text-embedding-3-small"

# Send a ping to confirm a successful connection
try:
    mongo_client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

url = "https://eu-central-1.aws.data.mongodb-api.com/app/data-ujyxlkh/endpoint/data/v1/action/findOne"

payload = json.dumps({
    "collection": "USER",
    "database": "Flat_Finder_DB",
    "dataSource": "FlatFinderCluster",
    "projection": {
        "_id": 1,
        "full_name": 1,

    }
})
headers = {
    'Content-Type': 'application/json',
    'Access-Control-Request-Headers': '*',
    'api-key': os.getenv('MONGO_DB_DATA_API_KEY'),
    'Accept': 'application/ejson'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)


# # Define collection and index name
# db_name = os.getenv('DB_NAME')
# collection_name = os.getenv('USER_COLLECTION')
# atlas_collection = client["Flat_Finder_DB"]["USER"]
# vector_search_index = os.getenv('INDEX_NAME')


def get_embedding(text):
    embeddings = openAi_client.embeddings.create(input=[text], model=model).data[0].embedding
    return embeddings


# Creates embeddings and stores them as a new field

user_data = "Relocating for a new job."
print(get_embedding(user_data))

