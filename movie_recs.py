import os
import pymongo
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get environment variables
hf_token = os.getenv("HF_TOKEN")
embedding_url = os.getenv("EMBEDDING_URL")
mongo_uri = os.getenv("MONGO_URI")

# Connect to MongoDB
client = pymongo.MongoClient(mongo_uri)
db = client.sample_mflix
collection = db.movies

def generate_embedding(text: str) -> list[float]:
    response = requests.post(
        embedding_url,
        headers={"Authorization": f"Bearer {hf_token}"},
        json={"inputs": text}
    )
    if response.status_code != 200:
        raise ValueError(f"Request failed with status code {response.status_code}: {response.text}")
    return response.json()

query = "suicide"

results = collection.aggregate([
    {"$vectorSearch": {
        "queryVector": generate_embedding(query),
        "path": "plot_embedding_hf",
        "numCandidates": 100,
        "limit": 50,
        "index": "PlotSemanticSearch",
    }}
])

for document in results:
    print(f'Movie Name: {document["title"]},\nMovie Plot: {document["plot"]}\n')
