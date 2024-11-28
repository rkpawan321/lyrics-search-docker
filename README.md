# Lyrics Search Engine

## **Overview**
The Lyrics Search Engine is a web-based application that allows users to search for song lyrics using different search methods. The app is powered by a Django backend integrated with Elasticsearch and a React frontend.

## DEMO: https://lyrics-search-frontend-572081148214.us-central1.run.app/
The frontend, backend with elasticsearch are hosted on GCP.

## **Features**
1. **Level 1: Lexical Search**  
   - Searches based on exact matches of words in song lyrics, title, or artist name.

2. **Level 2: Fuzzy Search**  
   - Provides flexibility by allowing minor typos or spelling variations in search terms.

3. **Advanced Search: Semantic and Vector Search**  
   - Performs meaning-based searches using **SentenceTransformer** (`all-MiniLM-L6-v2`).
   - Compares the semantic similarity of the query with song lyrics using dense vector embeddings indexed in Elasticsearch.

## **Dataset**
- The dataset is scraped from [Genius](https://genius.com/) and cross-referenced with Spotify until 2022.
- Preprocessed to include only English songs and made available at: [Kaggle Dataset](https://www.kaggle.com/datasets/pawankondebai/english-songs-and-lyrics).
- Indexed with dense vectors for semantic search using the following configuration:
   ```json
   {
      "type": "dense_vector",
      "dims": 384,
      "index": True,
      "similarity": "l2_norm"
   }


# Lyrics Search Application

## Setup Instructions

### Step 1: Clone the Repository
Run the following command to clone the project repository:

```bash
git clone https://github.com/rkpawan321/lyrics-search-docker.git
cd lyrics-search-docker
```

### Step 2: Set Up Elasticsearch
The project requires an Elasticsearch instance with vector search capabilities enabled.

#### Sign Up for Elasticsearch Cloud
- Go to **Elastic Cloud** and create an account.
- Create a deployment and note the **Elasticsearch URL**, **username (elastic)**, and **password** or **API key**.

#### Configure Elasticsearch for Vector Search
- Log into Kibana and run the following command to create the index:

```json
PUT /songs_with_vectors
{
  "mappings": {
    "properties": {
      "lyrics_vector": {
        "type": "dense_vector",
        "dims": 384,
        "index": true,
        "similarity": "l2_norm"
      },
      "title": {
        "type": "text"
      },
      "artist": {
        "type": "text"
      },
      "lyrics": {
        "type": "text"
      }
    }
  }
}
```

#### Index the Dataset
Use the reindexing script (`reindex_vectors.py`) to upload your data to Elasticsearch:

```bash
python3 reindex_vectors.py
```

#### Verify the Setup
Test the connection with:

```bash
curl -X GET "https://<your-elasticsearch-url>/_cat/indices?v" -H "Authorization: ApiKey <your-api-key>"
```

### Step 3: Start the Backend
The backend is a Django application integrated with Elasticsearch. Use Docker to simplify the setup process.

Navigate to the backend directory:

```bash
cd backend
```

Build and run the Docker container:

```bash
docker build -t lyrics-search-backend .
docker run -p 8000:8000 lyrics-search-backend
```

### Step 4: Start the Frontend
The frontend is a React-based application.

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies and start the development server:

```bash
npm install
npm start
```

### Step 5: Test the Application
- Access the frontend in your browser at: [http://localhost:3000](http://localhost:3000).
- The backend API is available at: [http://localhost:8000](http://localhost:8000).

## Endpoints Overview

| Search Type           | Endpoint                    | Description                                                      |
|-----------------------|-----------------------------|------------------------------------------------------------------|
| Lexical Search        | `/lexical_search/?q=<query>` | Exact keyword matches in lyrics, title, or artist.               |
| Fuzzy Search          | `/fuzzy_search/?q=<query>`  | Matches keywords with minor variations or typos.                 |
| Semantic and Vector Search | `/vector_search/` (POST)    | Performs advanced meaning-based search. Requires a query vector in the POST request body. |

### Example: Vector Search
For semantic vector search, send a POST request to `/vector_search/` with the following payload:

```json
{
  "vector": [0.1, 0.2, 0.3, ...]  // Provide the vector embedding for the search
}
```

## Technology Stack
- **Backend**: Django, Elasticsearch
- **Frontend**: React
- **Machine Learning Model**: SentenceTransformer (all-MiniLM-L6-v2)
- **Data**: Scraped dataset of English songs and lyrics from Genius and Spotify.

## DEMO Link
https://lyrics-search-frontend-572081148214.us-central1.run.app/


PS: My GCP credits are over. Please feel free to donate $ :)


