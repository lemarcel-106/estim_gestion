from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings
import os
from .models import ParametreResultat
from parametre.models import Matiere
from django.shortcuts import render
import qrcode
import os
from PIL import Image
from django.utils import timezone
from qrcode.constants import ERROR_CORRECT_H
from .utils import link_callback  # Assure-toi que ce helper est défini
from attestations.models import Attestation

def generate_pdf_resultat_etudiant(request, resultat):
    template_path = 'admin/bulletin.html'
    template = get_template(template_path)

    etudiant = resultat.etudiant
    session = ParametreResultat.objects.first().session

    matieres = Matiere.objects.filter(classe=etudiant.classe)
    matieres_valides = []
    matieres_non_valides = []

    for matiere in matieres:
        res = etudiant.moyenne_par_matiere(matiere, session)
        if res:
            if res["moyenne_brute"] >= 10:
                matieres_valides.append(res)
            else:
                matieres_non_valides.append(res)

    # Construction de l'URL complète pour la photo
    host = request.get_host()
    photo_url = f"http://{host}{settings.MEDIA_URL}{etudiant.photo}"

    context = {
        'etudiant': etudiant,
        'resultat': resultat,
        'matieres_valides': matieres_valides,
        'matieres_non_valides': matieres_non_valides,
        'photo_url': photo_url,
        'logo_path': 'http://127.0.0.1:8080/static/logo_estim.jpg',
        'date_du_jour': timezone.now(),
    }

    # Création du PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bulletin_{etudiant.matricule}.pdf"'

    pisa_status = pisa.CreatePDF(
        template.render(context),
        dest=response,
        link_callback=link_callback
    )

    if pisa_status.err:
        return HttpResponse('Une erreur est survenue lors de la génération du PDF.', status=500)

    return response


def link_callback(uri, rel):
    # Gestion des liens statiques et médias
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri[len(settings.MEDIA_URL):])
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri[len(settings.STATIC_URL):])
    else:
        return uri

    if not os.path.isfile(path):
        raise Exception(f"Fichier introuvable : {path}")

    return path

def hello_world(request):
    return render(request, 'admin/attestation_frequentation.html')


def attestation_inscription(request, resultat):
    template_path = 'admin/attestation_inscription.html'
    template = get_template(template_path)
    etudiant = resultat

    # Donnée à encoder dans le QR code
    qr_data = f"""
        N° : {etudiant.matricule}/ESTIM/DG/{etudiant.annee_scolaire}
        Nom et Prénoms : {etudiant.nom_prenom}
        Fait le  : {timezone.now().strftime("%d/%m/%Y")}
    """

    # Création du QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=4,
        border=2,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Dossier et nom du fichier QR
    qr_folder = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
    os.makedirs(qr_folder, exist_ok=True)
    qr_filename = f"{etudiant.matricule}_qr.png"
    qr_path = os.path.join(qr_folder, qr_filename)
    img.save(qr_path)

    # URL vers l’image QR code
    qr_url = f"{settings.MEDIA_URL}qr_codes/{qr_filename}"

    # URL de la photo de l’étudiant
    photo_url = f"http://{request.get_host()}{settings.MEDIA_URL}{etudiant.photo}"


    # Création de l'attestation dans la base de données

    Attestation.objects.create(
    etudiant=etudiant,
    type='inscription',
    numero=f"{etudiant.matricule}/ESTIM/DG/{etudiant.annee_scolaire}"
    )

    # Contexte du template
    context = {
        "numero": etudiant.matricule,
        "annee": etudiant.annee_scolaire,
        "nom_complet": etudiant.nom_prenom,
        "date_naissance": etudiant.date_naissance.strftime("%d/%m/%Y") if etudiant.date_naissance else "Non renseignée",
        "lieu_naissance": etudiant.lieu_naissance or "Non renseigné",
        "annee_academique": etudiant.annee_scolaire,
        "option": etudiant.classe.filiere.nom if etudiant.classe and etudiant.classe.filiere else "Non renseignée",
        "niveau": etudiant.classe.niveau if etudiant.classe else "Non renseigné",
        "date_du_jour": timezone.now(),
        "qr_code_url": qr_url,
        "photo_url": photo_url,
    }

    # Génération du PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Attestation_inscription__{etudiant.nom_prenom}.pdf"'

    pisa_status = pisa.CreatePDF(
        template.render(context),
        dest=response,
        link_callback=link_callback
    )

    if pisa_status.err:
        return HttpResponse('Une erreur est survenue lors de la génération du PDF.', status=500)

    return response



def attestation_frequentation(request, resultat):
    template_path = 'admin/attestation_frequentation.html'
    template = get_template(template_path)
    etudiant = resultat

    # Donnée à encoder dans le QR code
    qr_data = f"""
        N° : {etudiant.matricule}/ESTIM/DG/{etudiant.annee_scolaire}
        Nom et Prénoms : {etudiant.nom_prenom}
        Fait le  : {timezone.now().strftime("%d/%m/%Y")}
    """
    
    # Création du QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_H,
        box_size=4,
        border=2,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Dossier et nom du fichier de sortie
    qr_folder = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
    os.makedirs(qr_folder, exist_ok=True)
    qr_filename = f"{etudiant.matricule}_qr.png"
    qr_path = os.path.join(qr_folder, qr_filename)

    # Sauvegarde du QR code
    img.save(qr_path)

    # URL vers l’image QR code (accessible dans le template)
    qr_url = f"{settings.MEDIA_URL}qr_codes/{qr_filename}"

    # URL de la photo de l’étudiant (optionnelle)
    photo_url = f"http://{request.get_host()}{settings.MEDIA_URL}{etudiant.photo}" if etudiant.photo else ""


    # Création de l'attestation dans la base de données
    Attestation.objects.create(
    etudiant=etudiant,
    type='frequentation',
    numero=f"{etudiant.matricule}/ESTIM/DG/{etudiant.annee_scolaire}"
    )

    # Contexte du template
    context = {
        "numero": etudiant.matricule,
        "annee": etudiant.annee_scolaire,
        "nom_complet": etudiant.nom_prenom,
        "date_naissance": etudiant.date_naissance.strftime("%d/%m/%Y") if etudiant.date_naissance else "Non renseignée",
        "lieu_naissance": etudiant.lieu_naissance or "Non renseigné",
        "annee_academique": etudiant.annee_scolaire,
        "option": etudiant.classe.filiere.nom if etudiant.classe and etudiant.classe.filiere else "Non renseignée",
        "niveau": etudiant.classe.niveau if etudiant.classe else "Non renseigné",
        'date_du_jour': timezone.now(),
        'qr_code_url': qr_url,
        'photo_url': photo_url,
    }

    # Génération du PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Attestation_frequentation__{etudiant.nom_prenom}.pdf"'

    pisa_status = pisa.CreatePDF(
        template.render(context),
        dest=response,
        link_callback=link_callback
    )

    if pisa_status.err:
        return HttpResponse('Une erreur est survenue lors de la génération du PDF.', status=500)

    return response
