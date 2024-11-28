from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer
import pandas as pd

# Elasticsearch Cloud setup
ELASTIC_CLOUD_ID = "03f2e51817714e24b3ef132dc10054e7:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvJDAzMDE2YzMxNGZmYTQ4ZmU5NzU0ODVkYWM1YjkwZDUzJGIwM2M3NzQ4NWNiZTRkN2U4ZTM2YzNmZjc3ODE4Zjdj"
API_KEY = "bExCVlk1TUJVTklhV00xbHVyUG86aWwyYXpUdVBRWUdqVFcxR2NMR2JHZw==s"

es = Elasticsearch(
    cloud_id=ELASTIC_CLOUD_ID,
    api_key=API_KEY
)

# Index name
INDEX_NAME = "songs_with_vectors"

# Path to the CSV file
LOCAL_CSV_PATH = "../data/english_songs_and_lyrics.csv"  # Update this path to where your data file resides

# Load SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load the CSV data
df = pd.read_csv(LOCAL_CSV_PATH)

# Delete the index if it exists
if es.indices.exists(index=INDEX_NAME):
    es.indices.delete(index=INDEX_NAME)
    print(f"Deleted existing index '{INDEX_NAME}'.")

# Define the index mapping
mapping = {
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "artist": {"type": "text"},
            "lyrics": {"type": "text"},
            "vector_field": {
                "type": "dense_vector",
                "dims": 384,  # Adjust based on your model's vector size
                "index": True,  # Enable indexing for KNN search
                "similarity": "l2_norm"  # Specify similarity metric (optional)
            }
        }
    }
}

# Create the index
es.indices.create(index=INDEX_NAME, body=mapping)
print(f"Created index '{INDEX_NAME}' with the correct mapping.")

# Process data in chunks
chunk_size = 1000  # Adjust the chunk size as needed
total_chunks = len(df) // chunk_size + 1

for chunk_idx, chunk_start in enumerate(range(0, len(df), chunk_size)):
    chunk = df.iloc[chunk_start:chunk_start + chunk_size]

    # Prepare actions for bulk upload
    actions = []
    for _, row in chunk.iterrows():
        title = row['title']
        artist = row['artist']
        lyrics = row['lyrics']

        # Generate vector embedding
        embedding = model.encode(lyrics).tolist()

        # Prepare Elasticsearch document
        actions.append({
            "_index": INDEX_NAME,
            "_source": {
                "title": title,
                "artist": artist,
                "lyrics": lyrics,
                "vector_field": embedding
            }
        })

    # Bulk upload the chunk
    try:
        helpers.bulk(es, actions)
        print(f"Chunk {chunk_idx + 1}/{total_chunks} uploaded successfully!")
    except Exception as e:
        print(f"Error uploading chunk {chunk_idx + 1}: {e}")

print("Data indexing completed!")
