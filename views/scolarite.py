from ninja import Router
from parametre.models import Matiere, Classe, Filiere
from schemas.scolariteSchema import MatiereOut, MatiereCreate, MatiereUpdate, ClasseOut, ClasseCreate, FilliereCreate,FilliereOut
scolarite_route = Router()

@scolarite_route.get("/matieres", response=list[MatiereOut])
def list_matieres(request):
    return [
        {
            "id": matiere.pk,
            "nom": matiere.nom,
            "classe_id": matiere.classe.id,
            "abreviation": matiere.abreviation,
            "coefficient": matiere.coefficient,
            "classe": matiere.classe.nom,
        } for matiere in Matiere.objects.all()
    ]

@scolarite_route.post("/matieres", response=MatiereOut)
def create_matiere(request, payload: MatiereCreate):
    matiere = Matiere.objects.create(**payload.dict())
    return {
            "id": matiere.pk,
            "nom": matiere.nom,
            "classe_id": matiere.classe.id,
            "abreviation": matiere.abreviation,
            "coefficient": matiere.coefficient,
            "classe": matiere.classe.nom,
        }

@scolarite_route.post("/matieres/{matiere_id}", response=MatiereOut)
def update_matiere(request, matiere_id: int, payload: MatiereUpdate):
    matiere = Matiere.objects.get(id=matiere_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(matiere, attr, value)
    matiere.save()
    return {
            "id": matiere.pk,
            "nom": matiere.nom,
            "classe_id": matiere.classe.id,
            "abreviation": matiere.abreviation,
            "coefficient": matiere.coefficient,
            "classe": matiere.classe.nom,
        }

@scolarite_route.post("/matiere/{matiere_id}")
def delete_matiere(request, matiere_id:int):
    matiere = Matiere.objects.filter(id=matiere_id).first().delete()
    return {'success': True}




## Liste des classes
@scolarite_route.get("/classes", response=list[ClasseOut])
def list_classes(request):
    return Classe.objects.all()


@scolarite_route.post("/classes", response=ClasseOut)
def create_classe(request, payload: ClasseCreate):
    classe = Classe.objects.create(**payload.dict())
    return {
        'id': classe.pk,
        'nom': classe.nom,
        'filiere_id':classe.filiere.id,
        'niveau': classe.niveau
    }


@scolarite_route.post("/classes/{classe_id}")
def delete_classe(request, classe_id:int):
    classe = Classe.objects.get(id=classe_id).delete()
    return {'success': True}


##########

@scolarite_route.post("/fillieres/", response=FilliereOut)
def create_filliere(request, payload: FilliereCreate):
    filiere = Filiere.objects.create(**payload.dict())
    return filiere

@scolarite_route.get("/fillieres/", response=list[FilliereOut])
def list_fillieres(request):
    return Filiere.objects.all()


@scolarite_route.post("/fillieres/{filiere_id}")
def delete_filliere(request, filiere_id:int):
    filiere = Filiere.objects.get(id=filiere_id).delete()
    return {'success': True}