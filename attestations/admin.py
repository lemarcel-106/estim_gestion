from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Attestation


@admin.register(Attestation)
class AttestationAdmin(ModelAdmin):
    list_display = ['numero', 'etudiant', 'type', 'date_creation', 'valide']
    list_filter = ['type', 'valide']
    search_fields = ['etudiant__nom', 'etudiant__prenom', 'numero']
    list_editable = ('valide',)


    def has_add_permission(self, request):
        return False
