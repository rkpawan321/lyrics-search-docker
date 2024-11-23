import pandas as pd
from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer

# Elasticsearch setup without authentication
es = Elasticsearch(
    hosts=["http://elasticsearch:9200"],  # Use service name from docker-compose
    verify_certs=False
)

# Load SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Path to the CSV file
data_file = "../data/english_songs_and_lyrics.csv"
df = pd.read_csv(data_file)

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
            "_index": "songs_with_vectors",
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
