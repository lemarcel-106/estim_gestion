from django.contrib import admin
from .models import  Examen, Devoir
from unfold.admin import ModelAdmin




@admin.register(Devoir)
class DevoirAdmin(ModelAdmin):
    list_display = ('matiere', 'session', 'date')
    search_fields = ['matiere__nom',]  # ou tout champ utile
    autocomplete_fields = ['matiere']
    
@admin.register(Examen)
class ExamenAdmin(ModelAdmin):
    list_display = ('matiere', 'session', 'date')
    search_fields = ['matiere__nom',]  # ou tout champ utile
    autocomplete_fields = ['matiere']

