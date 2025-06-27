from django.contrib import admin
from .models import NoteDevoir, NoteExamen
from parametre.models import Etudiant
from unfold.admin import ModelAdmin
from examen_devoir.models import Devoir, Examen
from django import forms
from django.utils.translation import gettext_lazy as _





#######################################################################################################




@admin.register(NoteExamen)
class NoteExamenAdmin(ModelAdmin):
    autocomplete_fields = ['etudiant']
    list_display = ('etudiant', 'examen', 'note')
    search_fields = ('etudiant__matricule', 'examen__id')
    autocomplete_fields = ['examen', 'etudiant']






@admin.register(NoteDevoir)
class NoteDevoirAdmin(ModelAdmin):
    # form = NoteDevoirForm
    list_display = ('etudiant', 'devoir', 'note')
    search_fields = ('etudiant__nom_prenom', 'devoir')
    autocomplete_fields = ['devoir', 'etudiant']


    # list_filter_submit = True  # Submit button at the bottom of the filter
   