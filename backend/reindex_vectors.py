import pandas as pd
from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer

# Elasticsearch setup without authentication
es = Elasticsearch(
    # hosts=["http://elasticsearch:9200"],  # Use service name from docker-compose
    hosts=["http://localhost:9200"],
    verify_certs=False
)

# Index name
INDEX_NAME = "songs_with_vectors"

# Load SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Path to the CSV file
data_file = "../data/english_songs_and_lyrics.csv"
df = pd.read_csv(data_file)

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
                "dims": 384  # Adjust based on your model's vector size
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
