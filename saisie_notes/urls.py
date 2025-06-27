# saisie_notes/urls.py
from django.urls import path
from .views import EtudiantAutocomplete

urlpatterns = [
    path('etudiant-autocomplete/', EtudiantAutocomplete.as_view(), name='etudiant-autocomplete'),
]
