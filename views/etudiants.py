from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from ninja import Router
from parametre.models import Etudiant, Filiere
from gestion_des_resultats.models import ParametreResultat
from schemas.etudiantSchema import (
    EtudiantOut,
    EtudiantCreate,
    EtudiantDateLieu,
    EtudiantUpdate)

from ninja.files import UploadedFile
from ninja.errors import HttpError

etudiant_router = Router()

@etudiant_router.get("", response=list[EtudiantOut])
def list_etudiants(request):
    return [  {
        "id" : student.pk,
        "matricule" : student.matricule,
        "nom_prenom" : student.nom_prenom,
        "classe" : student.classe.pk,
        "photo" : request.build_absolute_uri(student.photo.url) if student.photo else None,
    }

        for student in Etudiant.objects.all()
    ]

@etudiant_router.post("", response=EtudiantOut)
def create_etudiant(request, payload: EtudiantCreate):
    student = Etudiant(**payload.dict())
    student.save()
    return {
        "id" : student.pk,
        "matricule" : student.matricule,
        "nom_prenom" : student.nom_prenom,
        "classe" : student.classe.pk,
        "photo" : request.build_absolute_uri(student.photo.url) if student.photo else None,
    }


@etudiant_router.get("get/{etudiant_id}/", response=EtudiantOut)
def get_etudiant(request, etudiant_id: int):
    student = Etudiant.objects.get(id=etudiant_id)
    return {
        "id" : student.pk,
        "matricule" : student.matricule,
        "nom_prenom" : student.nom_prenom,
        "classe" : student.classe.pk,
        "photo" : request.build_absolute_uri(student.photo.url) if student.photo else None,
    }


@etudiant_router.post("update/{etudiant_id}/", response=EtudiantOut)
def update_etudiant(request, etudiant_id: int, payload: EtudiantUpdate):
    # try:
    #     student = Etudiant.objects.get(pk=etudiant_id)
    # except Etudiant.DoesNotExist:
    #     raise HttpError(status_code=404, detail="Étudiant non trouvé")

    student = Etudiant.objects.get(pk=etudiant_id)
    # Mettre à jour uniquement les champs fournis
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(student, attr, value)

    student.save()

    return {
        "id": student.pk,
        "matricule": student.matricule,
        "nom_prenom": student.nom_prenom,
        "classe": student.classe.pk if student.classe else None,
        "photo": request.build_absolute_uri(student.photo.url) if student.photo else None,
    }


@etudiant_router.get("{etudiant_id}/")
def delete_etudiant(request, etudiant_id: int):
    Etudiant.objects.filter(id=etudiant_id).delete()
    return {"success": True}



########### Section 02

# 1. Trouver un étudiant par son matricule
@etudiant_router.get("by-matricule/{matricule}/")
def get_etudiant_by_matricule(request, matricule: str):
    student = get_object_or_404(Etudiant, matricule=matricule)
    return {
        "matricule" : student.matricule,
        "nom" : student.nom_prenom,
        "classe" : student.classe.nom,
    }
    
# 2. Ajouter ou modifier une photo
@etudiant_router.post("{etudiant_matricule}/datelieu/")
def etudiant_date_lieu(request, etudiant_matricule: int, payload: EtudiantDateLieu):
    # Vérification des paramètres requis
    etudiant = get_object_or_404(Etudiant, matricule=etudiant_matricule)
    
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(etudiant, attr, value)

    # print(payload.dict())
    
    # Enregistrement des modifications
    etudiant.save()
    return {"success": True, "message": "Date de naissance et lieu de naissance mis à jour avec succès."}
    
# 2. Ajouter ou modifier une photo
@etudiant_router.post("{etudiant_matricule}/photo/")
def upload_etudiant_photo(request, etudiant_matricule: int, file: UploadedFile):
    etudiant = get_object_or_404(Etudiant, matricule=etudiant_matricule)
    etudiant.photo.save(file.name, file)
    etudiant.save()
    return {"success": True, "message": "Photo mise à jour avec succès."}

# 2. Ajouter ou modifier une photo
@etudiant_router.get("resultat/v1/{etudiant_matricule}")
def get_resultat_etudiant(request, etudiant_matricule: int):
    etudiant = get_object_or_404(Etudiant, matricule=etudiant_matricule)
   
    if etudiant.actif:
        result = etudiant.generer_bulletin(code_session=ParametreResultat.objects.all().first().session)
        result.update({"photo" : request.build_absolute_uri(etudiant.photo.url) if etudiant.photo else None})
        return  result
    else:
        {
            "detail": "Cet étudiant n'est pas actif.",
        }



# @etudiant_router.get("resultat/v2/{etudiant_matricule}")
# def get_resultat_etudiant_v2(request, etudiant_matricule: int):
#     etudiant = get_object_or_404(EtudiantResultat, matricule=etudiant_matricule)
#     # etudiant.moyenne_generale()
#     # etudiant.save()
#     return {
#         'nom_prenom': etudiant.nom_prenom,
#         'matricule': etudiant.matricule,
#         'classe': etudiant.classe_etudiant,
#         'moyenne_generale': etudiant.moyenne_generale,
#             "photo" : request.build_absolute_uri(etudiant.photo.url) if etudiant.photo else None,

#         }



# 3. Activer ou désactiver le statut actif
@etudiant_router.post("{etudiant_matricule}/toggle/")
def toggle_etudiant_status(request, etudiant_matricule: int):
    etudiant = get_object_or_404(Etudiant, matricule=etudiant_matricule)
    etudiant.actif = not etudiant.actif
    etudiant.save()
    return {"success": True, "nouveau_statut": etudiant.actif}



# 2. Nombre d'étudiants par filière
@etudiant_router.get("statistiques/etudiants-par-filiere/")
def nombre_etudiants_par_filiere(request):
    filieres = (
        Filiere.objects
        .annotate(
            nb_etudiants=Count(
                'classes__etudiants',
                filter=Q(classes__etudiants__actif=True)
            )
        )
        .values('id', 'nom', 'nb_etudiants')
    )
    return list(filieres)
