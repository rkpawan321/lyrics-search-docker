from django.urls import path
from . import views

urlpatterns = [
    path('lexical-search/', views.lexical_search, name='lexical_search'),
    path('fuzzy-search/', views.fuzzy_search, name='fuzzy_search'),
    path('semantic-search/', views.semantic_search, name='semantic_search'),
    path('vector-search/', views.vector_search, name='vector_search'),
    path('generate-vector/', views.generate_vector, name='generate-vector'),
]
