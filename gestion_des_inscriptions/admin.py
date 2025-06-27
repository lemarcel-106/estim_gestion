from django.contrib import admin
from .models import EtudiantLambda, Inscription, DossierEtudiant, PreInscription
# from unfold.admin import ModelAdmin

from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm, SelectableFieldsExportForm
from import_export.admin import ExportActionModelAdmin



@admin.register(DossierEtudiant)
class DossierEtudiantAdmin(ExportActionModelAdmin, ModelAdmin):
    list_display = ('nom', 'prenom', 'date_naissance', 'lieu_naissance', 'telephone', 'filiere_souhaitee', 'possede_ordinateur')
    search_fields = ('nom', 'prenom', 'telephone')
    list_filter = ('filiere_souhaitee',)
    list_per_page = 25


@admin.register(PreInscription)
class PreInscriptionAdmin(ExportActionModelAdmin, ModelAdmin):
    list_display = ('nom', 'prenom', 'telephone', 'email', 'filiere_souhaitee')
    search_fields = ('nom', 'prenom', 'telephone')
    list_filter = ('filiere_souhaitee',)
    list_per_page = 25