from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import json

# Initialize Elasticsearch client
es = Elasticsearch(
    hosts=["http://elasticsearch:9200"],
    # basic_auth=("elastic", "PO0IlHE4wxZwiqL+F5Yd"),
    verify_certs=False
)

# Load the pre-trained model (ensure it's already downloaded)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Lexical Search
@csrf_exempt
def lexical_search(request):
    if request.method != "GET":
        return JsonResponse({'error': 'Only GET method is allowed'}, status=400)

    query = request.GET.get('q', '')
    print(f"Received query: {query}")  # Debugging: Log the query

    if not query:
        return JsonResponse({'error': 'Query parameter "q" is required'}, status=400)

    body = {
        "_source": ["title", "artist", "lyrics"],
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["lyrics^2", "title", "artist"],  # Boost lyrics
            }
        },
        "highlight": {
            "fields": {
                "lyrics": {"pre_tags": ["<mark>"], "post_tags": ["</mark>"]},
                "title": {"pre_tags": ["<mark>"], "post_tags": ["</mark>"]},
            }
        }
    }

    try:
        response = es.search(index="songs_with_vectors", body=body)
        hits = response['hits']['hits']
        print(f"ElasticSearch Hits: {hits}")  # Debugging: Log Elasticsearch results

        return JsonResponse({
            'results': [
                {
                    'title': hit['_source']['title'],
                    'artist': hit['_source']['artist'],
                    'lyrics': hit['_source']['lyrics'],
                    'highlight': hit.get('highlight', {})
                }
                for hit in hits
            ]
        })
    except Exception as e:
        print(f"Error in lexical_search: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# Fuzzy Search
@csrf_exempt
def fuzzy_search(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'error': 'Query parameter "q" is required'}, status=400)

    body = {
        "_source": ["title", "artist", "lyrics"],
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["lyrics^2", "title", "artist"],
                "fuzziness": 2,
                "prefix_length": 4
            }
        },
        "highlight": {
            "fields": {
                "lyrics": {"pre_tags": ["<mark>"], "post_tags": ["</mark>"]},
                "title": {"pre_tags": ["<mark>"], "post_tags": ["</mark>"]},
            }
        }
    }

    try:
        response = es.search(index="songs_with_vectors", body=body)
        hits = response['hits']['hits']
        return JsonResponse({
            'results': [
                {
                    'title': hit['_source']['title'],
                    'artist': hit['_source']['artist'],
                    'lyrics': hit['_source']['lyrics'],
                    'highlight': hit.get('highlight', {})
                }
                for hit in hits
            ]
        })
    except Exception as e:
        print(f"Error in fuzzy_search: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# Semantic Search
@csrf_exempt
def semantic_search(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'error': 'Query parameter "q" is required'}, status=400)

    body = {
        "_source": ["title", "artist", "lyrics"],
        "query": {
            "match": {
                "lyrics": query
            }
        }
    }

    try:
        response = es.search(index="songs_with_vectors", body=body)
        hits = response['hits']['hits']
        return JsonResponse({
            'results': [
                {'title': hit['_source']['title'], 'artist': hit['_source']['artist'], 'lyrics': hit['_source']['lyrics']}
                for hit in hits
            ]
        })
    except Exception as e:
        print(f"Error in semantic_search: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# Vector Search using POST
@csrf_exempt
def vector_search(request):
    if request.method != "POST":
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body)
        query_vector = data.get('vector', [])
        if not query_vector or not isinstance(query_vector, list):
            return JsonResponse({'error': 'Invalid or missing vector in payload'}, status=400)

        # Ensure the vector is of type float
        query_vector = [float(v) for v in query_vector]

        # Elasticsearch KNN query
        body = {
            "size": 10,
            "_source": ["title", "artist", "lyrics"],
            "knn": {  # Use the knn body parameter
                "field": "vector_field",  # Name of the field in Elasticsearch
                "query_vector": query_vector,
                "k": 10,
                "num_candidates": 100
            }
        }

        response = es.search(index="songs_with_vectors", body=body)
        hits = response['hits']['hits']

        return JsonResponse({
            'results': [
                {
                    'title': hit['_source']['title'],
                    'artist': hit['_source']['artist'],
                    'lyrics': hit['_source']['lyrics'],
                    'score': hit['_score']
                }
                for hit in hits
            ]
        })
    except Exception as e:
        print(f"Error in vector_search: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def generate_vector(request):
    if request.method != "POST":
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body)
        query = data.get('q', '')
        if not query:
            return JsonResponse({'error': 'Query parameter "q" is required'}, status=400)

        # Ensure model is working correctly
        query_vector = model.encode(query).tolist()
        
        print(f"Query: {query}")
        print(f"Vector Length: {len(query_vector)}")
        print(f"Vector First 5 Values: {query_vector[:5]}")
        print(f"Vector Type: {type(query_vector[0])}")

        return JsonResponse({
            'vector': query_vector,
            'vector_length': len(query_vector),
            'first_5_values': query_vector[:5]
        })
    except Exception as e:
        print(f"Error in generate_vector: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
