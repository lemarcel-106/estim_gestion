from django.contrib import admin
from .models import ResultatEtudiant, ParametreResultat, MatiereRattrapage, ResultatAdmissionClasseSession
from django.shortcuts import redirect
from unfold.admin import ModelAdmin
from .views import generate_pdf_resultat_etudiant, attestation_inscription
from django.utils import timezone
from django.urls import path
from django.template.response import TemplateResponse
from parametre.models import Etudiant
from django.conf import settings

# Création de PDF

import io
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa


def export_attestation_inscription_pdf(modeladmin, request, queryset):
    resultats = []

    for resultat in queryset:
        classe = resultat.classe
        session = resultat.session

        etudiants_admis = []

        # On sélectionne uniquement les étudiants actifs de la classe
        etudiants = Etudiant.objects.filter(classe=classe, actif=True)
        for etu in etudiants:
            moyenne = etu.moyenne_generale(session)
            if moyenne is not None and moyenne >= 10:
                etudiants_admis.append({
                    'nom': etu.nom_prenom,
                    'matricule': etu.matricule,
                    'classe': etu.classe,
                })


                # N'ajouter que si au moins un étudiant a des matières non validées
        if etudiants_admis:
            resultats.append({
                'classe': classe,
                'session': session,
                'etudiants': etudiants_admis
            })

    # Rendu HTML avec template
    html = render_to_string("admin/etudiants_admis_pdf.html", {
        'resultats': resultats,
        'date_du_jour': timezone.now(),
        'logo_path': 'http://127.0.0.1:8080/static/logo_estim.jpg',

    })

    # Génération PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="etudiants_admis.pdf"'

    pisa_status = pisa.CreatePDF(io.StringIO(html), dest=response)

    if pisa_status.err:
        return HttpResponse("Erreur lors de la génération du PDF", status=500)

    return response



def export_etudiants_admis_pdf(modeladmin, request, queryset):
    resultats = []

    for resultat in queryset:
        classe = resultat.classe
        session = resultat.session

        etudiants_admis = []

        # On sélectionne uniquement les étudiants actifs de la classe
        etudiants = Etudiant.objects.filter(classe=classe, actif=True)

        for etu in etudiants:
            moyenne = etu.moyenne_generale(session)
            if moyenne is not None and moyenne >= 10:
                etudiants_admis.append({
                    'nom': etu.nom_prenom,
                    'matricule': etu.matricule,
                    'classe': etu.classe,
                })


                # N'ajouter que si au moins un étudiant a des matières non validées
        if etudiants_admis:
            resultats.append({
                'classe': classe,
                'session': session,
                'etudiants': etudiants_admis
            })

    # Rendu HTML avec template
    html = render_to_string("admin/etudiants_admis_pdf.html", {
        'resultats': resultats,
        'date_du_jour': timezone.now(),
        'logo_path': 'http://127.0.0.1:8080/static/logo_estim.jpg',

    })

    # Génération PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="etudiants_admis.pdf"'

    pisa_status = pisa.CreatePDF(io.StringIO(html), dest=response)

    if pisa_status.err:
        return HttpResponse("Erreur lors de la génération du PDF", status=500)

    return response



export_etudiants_admis_pdf.short_description = "Imprimer la liste des étudiants admis (PDF)"



def export_matieres_non_valides_pdf(modeladmin, request, queryset):
    donnees = []

    for rattrapage in queryset:
        classe = rattrapage.classe
        session = rattrapage.session
        etudiants_data = []

        etudiants = Etudiant.objects.filter(classe=classe, actif=True)
        for etudiant in etudiants:
            matieres = etudiant.matieres_non_valides(session)
            if matieres:  # équivaut à "is not None and len(matieres) > 0"
                etudiants_data.append({
                    'nom': etudiant.nom_prenom,
                    'matieres': matieres
                })

        # N'ajouter que si au moins un étudiant a des matières non validées
        if etudiants_data:
            donnees.append({
                'classe': classe,
                'session': session,
                'etudiants': etudiants_data
            })

    # Ne pas générer de PDF vide
    if not donnees:
        return HttpResponse("Aucune donnée à exporter.", content_type="text/plain")
    

    html = render_to_string('admin/matieres_non_valides_simple.html', {
        'donnees': donnees,
        'date_du_jour': timezone.now(),
        'logo_path': 'http://127.0.0.1:8080/static/logo_estim.jpg',
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="matieres_non_valides.pdf"'

    pisa.CreatePDF(io.BytesIO(html.encode("utf-8")), dest=response)
    return response

export_matieres_non_valides_pdf.short_description = "Imprimer la liste des matières non validées (PDF)"





@admin.register(MatiereRattrapage)
class MatiereRattrapageAdmin(ModelAdmin):
    list_display = ['classe', 'session',]
    list_filter = ['classe',]
    list_per_page = 20
    autocomplete_fields = ['classe',]
    actions = [export_matieres_non_valides_pdf]
    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     return qs.select_related('session', 'classe')

@admin.register(ResultatAdmissionClasseSession)
class ResultatAdmissionClasseSessionAdmin(ModelAdmin):
    list_display = ['classe', 'session',]
    list_filter = ['classe',]
    list_per_page = 20
    autocomplete_fields = ['classe',]
    actions = [export_etudiants_admis_pdf]
    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     return qs.select_related('session', 'classe')


@admin.register(ParametreResultat)
class ParametreResultatAdmin(ModelAdmin):
    list_display = ('session',)



@admin.register(ResultatEtudiant)
class ResultatEtudiantAdmin(ModelAdmin):
    list_display = ['etudiant', 'moyenne_generale']
    actions = ['imprimer_bulletin']

    

    @admin.action(description="🖨️ Imprimer le bulletin PDF")
    def imprimer_bulletin(self, request, queryset):
        if queryset.count() == 1:
            resultat = queryset.first()
            return generate_pdf_resultat_etudiant(request, resultat)
        else:
            self.message_user(request, "Veuillez sélectionner un seul étudiant à la fois.", level="warning")
            return redirect(request.get_full_path())



    imprimer_bulletin.short_description = "Imprimer le bulletin (PDF)"





from django.contrib.auth.models import User, Group
admin.site.unregister(User)
admin.site.unregister(Group)