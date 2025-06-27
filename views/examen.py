from ninja import Router
from examen_devoir.models import SemestreExamen, Devoir, Examen
from saisie_notes.models import NoteDevoir, NoteExamen
from parametre.models import Etudiant
from schemas.examenSchema import (
    SessionExamenOut, SessionExamenCreate, SessionExamenUpdate,
    ResultatEtudiantOut, ResultatEtudiantCreate,
    DevoirOut, DevoirCreate,
    ExamenOut, ExamenCreate,
    NoteDevoirOut, NoteDevoirCreate,
    NoteExamenOut, NoteExamenCreate
)

examen_route = Router()

# ---------- SetupReseultat ----------
@examen_route.get("/setup-semestre", response=list[SessionExamenOut])
def list_setup_reseultats(request):
    return SemestreExamen.objects.all()

@examen_route.post("/setup-semestre", response=SessionExamenOut)
def create_setup_reseultat(request, data: SessionExamenCreate):
    return SemestreExamen.objects.create(**data.dict())

@examen_route.get("/setup-semestre/{id}", response=SessionExamenOut)
def get_setup_reseultat(request, id: int):
    return SemestreExamen.objects.get(id=id)

@examen_route.post("/setup-semestre/{id}", response=SessionExamenOut)
def update_setup_reseultat(request, id: int, data: SessionExamenUpdate):
    instance = SemestreExamen.objects.get(id=id)
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(instance, attr, value)
    instance.save()
    return instance

@examen_route.delete("/setup-semestre/{id}")
def delete_setup_reseultat(request, id: int):
    SemestreExamen.objects.get(id=id).delete()
    return {"success": True}


# ---------- ResultatEtudiant ----------
@examen_route.get("/resultats", response=list[ResultatEtudiantOut])
def list_resultats(request):
    return  [{
            "id": resultat.pk,
            "etudiant": resultat.etudiant.nom_prenom,
            "classe": resultat.etudiant.classe.nom,
            "moyenne_generale": resultat.moyenne_generale,
            "mention": resultat.mention,
        } for resultat in ResultatEtudiant.objects.all()
        ]
    

@examen_route.get("/resultat/{matricule_id}", response=ResultatEtudiantOut)
def resultat_etudiant(request, matricule_id: int):
    resultat = None
    if matricule_id:
        resultat = ResultatEtudiant.objects.filter(etudiant__matricule=matricule_id).first()
        if not resultat:
            resultat = Etudiant.objects.filter(matricule=matricule_id).first().moyenne_generale()
    return {
            "id": resultat.pk,
            "etudiant": resultat.etudiant.nom_prenom,
            "classe": resultat.etudiant.classe.nom,
            "moyenne_generale": resultat.moyenne_generale,
            "mention": resultat.mention,
            "photo": request.build_absolute_uri(resultat.etudiant.photo.url)
        }

@examen_route.post("/resultats")
def create_resultat(request, data: ResultatEtudiantCreate):
    ResultatEtudiant.objects.create(**data.dict())
    return {"success": True}

# CRUD similar pour ResultatEtudiant, Devoir, Examen, NoteDevoir, NoteExamen

# ---------- Devoir ----------
@examen_route.get("/devoirs", response=list[DevoirOut])
def list_devoirs(request):
    return [
        {
            "id": devoir.pk,
            "matiere_id": devoir.matiere.id,
            "matiere": devoir.matiere.nom,
            "session_id": devoir.session.id,
            "session": devoir.session.titre} for devoir in Devoir.objects.all()
    ]

@examen_route.post("/devoirs", response=DevoirOut)
def create_devoir(request, data: DevoirCreate):
    devoir = Devoir.objects.create(**data.dict())
    return  {
            "id": devoir.pk,
            "matiere_id": devoir.matiere.id,
            "matiere": devoir.matiere.nom,
            "session_id": devoir.session.id,
            "session": devoir.session.titre} 

# ---------- Examen ----------
@examen_route.get("/examens", response=list[ExamenOut])
def list_examens(request):
    return [
        {
            "id": examen.pk,
            "matiere_id": examen.matiere.id,
            "matiere": examen.matiere.nom,
            "session_id": examen.session.id,
            "session": examen.session.titre} for examen in Examen.objects.all()
    ]

@examen_route.post("/examens", response=ExamenOut)
def create_examen(request, data: ExamenCreate):
    examen = Examen.objects.create(**data.dict())
    return   {
            "id": examen.pk,
            "matiere_id": examen.matiere.id,
            "matiere": examen.matiere.nom,
            "session_id": examen.session.id,
            "session": examen.session.titre}



# ---------- NoteDevoir ----------
@examen_route.get("/notes-devoir", response=list[NoteDevoirOut])
def list_notes_devoir(request):
    return [
        {
            "id": note.pk,
            "devoir_id": note.devoir.id,
            "etudiant_id": note.etudiant.id,
            "note": note.note,
            "devoir": note.devoir.matiere.nom,
            "etudiant": note.etudiant.nom_prenom,
          } for note in NoteDevoir.objects.all()
    ]
# ---------- NoteDevoir ----------
@examen_route.get("/notes-devoir", response=list[NoteDevoirOut])
def list_notes_devoir_etudiant(request, matricule_id: int):
    return [
         {
            "id": note.pk,
            "devoir_id": note.devoir.id,
            "etudiant_id": note.etudiant.id,
            "note": note.note,
            "devoir": note.devoir.matiere.nom,
            "etudiant": note.etudiant.nom_prenom,
         } for note in NoteDevoir.objects.all(etudiant__matricule=matricule_id)
    ]

@examen_route.post("/notes-devoir", response=NoteDevoirOut)
def create_note_devoir(request, data: NoteDevoirCreate):
    note = NoteDevoir.objects.create(**data.dict())
    return {
            "id": note.pk,
            "devoir_id": note.devoir.id,
            "etudiant_id": note.etudiant.id,
            "note": note.note,
            "devoir": note.devoir.matiere.nom,
            "etudiant": note.etudiant.nom_prenom,
    }

# ---------- NoteExamen ----------
@examen_route.get("/notes-examen", response=list[NoteExamenOut])
def list_notes_examen(request):
    return [
         {
            "id": note.pk,
            "examen_id": note.examen.id,
            "etudiant_id": note.etudiant.id,
            "examen": note.examen.matiere.nom,
            "etudiant": note.etudiant.nom_prenom,
            "note": note.note,
            } for note in NoteExamen.objects.all()
    ]
@examen_route.get("/notes-examen", response=list[NoteExamenOut])
def list_notes_examen_etudiant(request, matricule_id: int):
    return [
         {
           "id": note.pk,
            "examen_id": note.examen.id,
            "etudiant_id": note.etudiant.id,
            "examen": note.examen.matiere.nom,
            "etudiant": note.etudiant.nom_prenom,
            "note": note.note,
         } for note in NoteExamen.objects.all(etudiant__matricule=matricule_id)
    ]
@examen_route.post("/notes-examen", response=NoteExamenOut)
def create_note_examen(request, data: NoteExamenCreate):
    note =  NoteExamen.objects.create(**data.dict())
    return  {
            "id": note.pk,
            "examen_id": note.examen.id,
            "etudiant_id": note.etudiant.id,
            "examen": note.examen.matiere.nom,
            "etudiant": note.etudiant.nom_prenom,
            "note": note.note,
            } 
