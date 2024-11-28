import pandas as pd
from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer
from google.cloud import storage
import os

# Elasticsearch setup without authentication
es = Elasticsearch(
    hosts=["http://localhost:9200"],
    verify_certs=False
)

# Index name
INDEX_NAME = "songs_with_vectors"

# Load SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to download file from Google Cloud Storage
def download_file_from_gcs(bucket_name, source_blob_name, destination_file_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    print(f"Downloaded {source_blob_name} from bucket {bucket_name} to {destination_file_name}.")

# GCS bucket details
BUCKET_NAME = "lyrics-search-data"  # Replace with your bucket name
SOURCE_BLOB_NAME = "data/english_songs_and_lyrics.csv"  # File path in the bucket
LOCAL_FILE_NAME = "english_songs_and_lyrics.csv"  # Temporary local file name

# Download CSV from GCS
download_file_from_gcs(BUCKET_NAME, SOURCE_BLOB_NAME, LOCAL_FILE_NAME)

# Load the CSV into a Pandas DataFrame
df = pd.read_csv(LOCAL_FILE_NAME)

# Delete the index if it exists
if es.indices.exists(index=INDEX_NAME):
    es.indices.delete(index=INDEX_NAME)
    print(f"Deleted existing index '{INDEX_NAME}'.")

# Create index with the correct mapping
mapping = {
    "mappings": {
        "properties": {
            "title": {
                "type": "text"
            },
            "artist": {
                "type": "text"
            },
            "lyrics": {
                "type": "text"
            },
            "vector_field": {
                "type": "dense_vector",
                "dims": 384,  # Adjust based on your model's vector size
                "index": True,  # Enable indexing for KNN search
                "similarity": "l2_norm"  # Specify similarity metric (optional)
            }
        }
    }
}

# Create the index with the mapping
es.indices.create(index=INDEX_NAME, body=mapping)
print(f"Created index '{INDEX_NAME}' with the correct mapping.")

# Define chunk size
chunk_size = 1000  # Adjust the chunk size as needed
total_chunks = len(df) // chunk_size + 1

# Process data in chunks
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

# Clean up local file
os.remove(LOCAL_FILE_NAME)
print(f"Deleted temporary file: {LOCAL_FILE_NAME}")
