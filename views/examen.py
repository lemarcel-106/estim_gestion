# views/examen.py (version améliorée avec documentation complète)
from ninja import Router
from django.shortcuts import get_object_or_404
from django.db.models import Q
from examen_devoir.models import SemestreExamen, Devoir, Examen
from saisie_notes.models import NoteDevoir, NoteExamen
from parametre.models import Etudiant
from gestion_des_resultats.models import ResultatEtudiant
from schemas.examenSchema import (
    SessionExamenOut, SessionExamenCreate, SessionExamenUpdate,
    ResultatEtudiantOut, ResultatEtudiantCreate,
    DevoirOut, DevoirCreate,
    ExamenOut, ExamenCreate,
    NoteDevoirOut, NoteDevoirCreate,
    NoteExamenOut, NoteExamenCreate
)
from schemas.notesSchema import (
    NoteDevoirDetailOut, NoteExamenDetailOut,
    NoteDevoirFilterOut, NoteExamenFilterOut
)

examen_route = Router()

# ========== GESTION DES SESSIONS D'EXAMENS ==========

@examen_route.get("/setup-semestre", response=list[SessionExamenOut])
def list_setup_reseultats(request):
    """
    Récupère la liste de toutes les sessions d'examens.
    
    **Réponse :**
    - **200** : Liste des sessions avec leurs informations
    
    **Exemple de réponse :**
    ```json
    [
        {
            "id": 1,
            "titre": "Semestre 1 - 2024/2025",
            "anneee_scolaire": "2024-2025",
            "date_debut": "2024-09-01"
        }
    ]
    ```
    """
    return SemestreExamen.objects.all()

@examen_route.post("/setup-semestre", response=SessionExamenOut)
def create_setup_reseultat(request, data: SessionExamenCreate):
    """
    Crée une nouvelle session d'examens.
    
    **Corps de la requête :**
    ```json
    {
        "titre": "Semestre 1 - 2024/2025",
        "anneee_scolaire": "2024-2025"
    }
    ```
    
    **Réponses :**
    - **200** : Session créée avec succès
    - **400** : Données invalides
    """
    return SemestreExamen.objects.create(**data.dict())

@examen_route.get("/setup-semestre/{id}", response=SessionExamenOut)
def get_setup_reseultat(request, id: int):
    """
    Récupère les détails d'une session spécifique.
    
    **Paramètres :**
    - **id** (int) : ID de la session
    
    **Réponses :**
    - **200** : Détails de la session
    - **404** : Session non trouvée
    """
    return get_object_or_404(SemestreExamen, id=id)

@examen_route.put("/setup-semestre/{id}", response=SessionExamenOut)
def update_setup_reseultat(request, id: int, data: SessionExamenUpdate):
    """
    Met à jour une session d'examens existante.
    
    **Paramètres :**
    - **id** (int) : ID de la session
    
    **Corps de la requête :**
    ```json
    {
        "titre": "Nouveau titre",
        "anneee_scolaire": "2024-2025"
    }
    ```
    
    **Réponses :**
    - **200** : Session mise à jour
    - **404** : Session non trouvée
    """
    instance = get_object_or_404(SemestreExamen, id=id)
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(instance, attr, value)
    instance.save()
    return instance

@examen_route.delete("/setup-semestre/{id}")
def delete_setup_reseultat(request, id: int):
    """
    Supprime une session d'examens.
    
    **Paramètres :**
    - **id** (int) : ID de la session
    
    **Réponses :**
    - **200** : Session supprimée
    - **404** : Session non trouvée
    """
    session = get_object_or_404(SemestreExamen, id=id)
    session.delete()
    return {"success": True}

# ========== GESTION DES DEVOIRS ==========

@examen_route.get("/devoirs", response=list[DevoirOut])
def list_devoirs(request, session_id: int = None, matiere_id: int = None):
    """
    Récupère la liste des devoirs avec filtres optionnels.
    
    **Paramètres de requête :**
    - **session_id** (int, optionnel) : Filtrer par session
    - **matiere_id** (int, optionnel) : Filtrer par matière
    
    **Réponse :**
    - **200** : Liste des devoirs
    
    **Exemple de réponse :**
    ```json
    [
        {
            "id": 1,
            "matiere_id": 1,
            "matiere": "Algorithmes",
            "session_id": 1,
            "session": "Semestre 1"
        }
    ]
    ```
    """
    devoirs = Devoir.objects.select_related('matiere', 'session').all()
    
    if session_id:
        devoirs = devoirs.filter(session_id=session_id)
    if matiere_id:
        devoirs = devoirs.filter(matiere_id=matiere_id)
    
    return [
        {
            "id": devoir.pk,
            "matiere_id": devoir.matiere.id,
            "matiere": devoir.matiere.nom,
            "session_id": devoir.session.id,
            "session": devoir.session.titre
        }
        for devoir in devoirs
    ]

@examen_route.post("/devoirs", response=DevoirOut)
def create_devoir(request, data: DevoirCreate):
    """
    Crée un nouveau devoir.
    
    **Corps de la requête :**
    ```json
    {
        "matiere_id": 1,
        "session_id": 1
    }
    ```
    
    **Réponses :**
    - **200** : Devoir créé avec succès
    - **400** : Données invalides
    """
    devoir = Devoir.objects.create(**data.dict())
    return {
        "id": devoir.pk,
        "matiere_id": devoir.matiere.id,
        "matiere": devoir.matiere.nom,
        "session_id": devoir.session.id,
        "session": devoir.session.titre
    }

@examen_route.get("/devoirs/{devoir_id}", response=DevoirOut)
def get_devoir(request, devoir_id: int):
    """
    Récupère les détails d'un devoir spécifique.
    
    **Paramètres :**
    - **devoir_id** (int) : ID du devoir
    
    **Réponses :**
    - **200** : Détails du devoir
    - **404** : Devoir non trouvé
    """
    devoir = get_object_or_404(Devoir, id=devoir_id)
    return {
        "id": devoir.pk,
        "matiere_id": devoir.matiere.id,
        "matiere": devoir.matiere.nom,
        "session_id": devoir.session.id,
        "session": devoir.session.titre
    }

@examen_route.delete("/devoirs/{devoir_id}")
def delete_devoir(request, devoir_id: int):
    """
    Supprime un devoir.
    
    **Paramètres :**
    - **devoir_id** (int) : ID du devoir
    
    **Réponses :**
    - **200** : Devoir supprimé
    - **404** : Devoir non trouvé
    """
    devoir = get_object_or_404(Devoir, id=devoir_id)
    devoir.delete()
    return {"success": True}

# ========== GESTION DES EXAMENS ==========

@examen_route.get("/examens", response=list[ExamenOut])
def list_examens(request, session_id: int = None, matiere_id: int = None):
    """
    Récupère la liste des examens avec filtres optionnels.
    
    **Paramètres de requête :**
    - **session_id** (int, optionnel) : Filtrer par session
    - **matiere_id** (int, optionnel) : Filtrer par matière
    
    **Réponse :**
    - **200** : Liste des examens
    
    **Exemple de réponse :**
    ```json
    [
        {
            "id": 1,
            "matiere_id": 1,
            "matiere": "Algorithmes",
            "session_id": 1,
            "session": "Semestre 1"
        }
    ]
    ```
    """
    examens = Examen.objects.select_related('matiere', 'session').all()
    
    if session_id:
        examens = examens.filter(session_id=session_id)
    if matiere_id:
        examens = examens.filter(matiere_id=matiere_id)
    
    return [
        {
            "id": examen.pk,
            "matiere_id": examen.matiere.id,
            "matiere": examen.matiere.nom,
            "session_id": examen.session.id,
            "session": examen.session.titre
        }
        for examen in examens
    ]

@examen_route.post("/examens", response=ExamenOut)
def create_examen(request, data: ExamenCreate):
    """
    Crée un nouvel examen.
    
    **Corps de la requête :**
    ```json
    {
        "matiere_id": 1,
        "session_id": 1
    }
    ```
    
    **Réponses :**
    - **200** : Examen créé avec succès
    - **400** : Données invalides
    """
    examen = Examen.objects.create(**data.dict())
    return {
        "id": examen.pk,
        "matiere_id": examen.matiere.id,
        "matiere": examen.matiere.nom,
        "session_id": examen.session.id,
        "session": examen.session.titre
    }

@examen_route.get("/examens/{examen_id}", response=ExamenOut)
def get_examen(request, examen_id: int):
    """
    Récupère les détails d'un examen spécifique.
    
    **Paramètres :**
    - **examen_id** (int) : ID de l'examen
    
    **Réponses :**
    - **200** : Détails de l'examen
    - **404** : Examen non trouvé
    """
    examen = get_object_or_404(Examen, id=examen_id)
    return {
        "id": examen.pk,
        "matiere_id": examen.matiere.id,
        "matiere": examen.matiere.nom,
        "session_id": examen.session.id,
        "session": examen.session.titre
    }

@examen_route.delete("/examens/{examen_id}")
def delete_examen(request, examen_id: int):
    """
    Supprime un examen.
    
    **Paramètres :**
    - **examen_id** (int) : ID de l'examen
    
    **Réponses :**
    - **200** : Examen supprimé
    - **404** : Examen non trouvé
    """
    examen = get_object_or_404(Examen, id=examen_id)
    examen.delete()
    return {"success": True}

# ========== GESTION DES NOTES DE DEVOIRS ==========

@examen_route.get("/notes-devoir", response=list[NoteDevoirDetailOut])
def list_notes_devoir(request, devoir_id: int = None, etudiant_id: int = None, classe_id: int = None):
    """
    Récupère la liste des notes de devoirs avec filtres optionnels.
    
    **Paramètres de requête :**
    - **devoir_id** (int, optionnel) : Filtrer par devoir
    - **etudiant_id** (int, optionnel) : Filtrer par étudiant
    - **classe_id** (int, optionnel) : Filtrer par classe
    
    **Réponse :**
    - **200** : Liste des notes de devoirs
    
    **Exemple de réponse :**
    ```json
    [
        {
            "id": 1,
            "devoir_id": 1,
            "devoir_matiere": "Algorithmes",
            "devoir_session": "Semestre 1",
            "etudiant_id": 1,
            "etudiant_nom": "DUPONT Jean",
            "etudiant_matricule": "1234",
            "etudiant_classe": "INFO-1",
            "note": 15.5,
            "coefficient": 3
        }
    ]
    ```
    """
    notes = NoteDevoir.objects.select_related(
        'devoir__matiere', 'devoir__session', 'etudiant__classe'
    ).all()
    
    if devoir_id:
        notes = notes.filter(devoir_id=devoir_id)
    if etudiant_id:
        notes = notes.filter(etudiant_id=etudiant_id)
    if classe_id:
        notes = notes.filter(etudiant__classe_id=classe_id)
    
    return [
        {
            "id": note.pk,
            "devoir_id": note.devoir.id,
            "devoir_matiere": note.devoir.matiere.nom,
            "devoir_session": note.devoir.session.titre,
            "etudiant_id": note.etudiant.id,
            "etudiant_nom": note.etudiant.nom_prenom,
            "etudiant_matricule": note.etudiant.matricule,
            "etudiant_classe": note.etudiant.classe.nom,
            "note": note.note,
            "coefficient": note.devoir.matiere.coefficient
        }
        for note in notes
    ]

@examen_route.get("/notes-devoir/etudiant/{matricule}", response=list[NoteDevoirFilterOut])
def list_notes_devoir_etudiant(request, matricule: str):
    """
    Récupère toutes les notes de devoirs d'un étudiant spécifique.
    
    **Paramètres :**
    - **matricule** (str) : Matricule de l'étudiant
    
    **Réponses :**
    - **200** : Notes de devoirs de l'étudiant
    - **404** : Étudiant non trouvé
    
    **Exemple de réponse :**
    ```json
    [
        {
            "id": 1,
            "devoir_id": 1,
            "matiere": "Algorithmes",
            "session": "Semestre 1",
            "etudiant_id": 1,
            "etudiant": "DUPONT Jean",
            "note": 15.5
        }
    ]
    ```
    """
    etudiant = get_object_or_404(Etudiant, matricule=matricule)
    notes = NoteDevoir.objects.filter(etudiant=etudiant).select_related(
        'devoir__matiere', 'devoir__session'
    )
    
    return [
        {
            "id": note.pk,
            "devoir_id": note.devoir.id,
            "matiere": note.devoir.matiere.nom,
            "session": note.devoir.session.titre,
            "etudiant_id": note.etudiant.id,
            "etudiant": note.etudiant.nom_prenom,
            "note": note.note
        }
        for note in notes
    ]

@examen_route.post("/notes-devoir", response=NoteDevoirOut)
def create_note_devoir(request, data: NoteDevoirCreate):
    """
    Crée une nouvelle note de devoir.
    
    **Corps de la requête :**
    ```json
    {
        "devoir_id": 1,
        "etudiant_id": 1,
        "note": 15.5
    }
    ```
    
    **Réponses :**
    - **200** : Note créée avec succès
    - **400** : Données invalides (note déjà existante, valeurs incorrectes)
    """
    note = NoteDevoir.objects.create(**data.dict())
    return {
        "id": note.pk,
        "devoir_id": note.devoir.id,
        "etudiant_id": note.etudiant.id,
        "note": note.note,
        "devoir": note.devoir.matiere.nom,
        "etudiant": note.etudiant.nom_prenom,
    }

@examen_route.put("/notes-devoir/{note_id}", response=NoteDevoirOut)
def update_note_devoir(request, note_id: int, data: NoteDevoirCreate):
    """
    Met à jour une note de devoir existante.
    
    **Paramètres :**
    - **note_id** (int) : ID de la note
    
    **Corps de la requête :**
    ```json
    {
        "devoir_id": 1,
        "etudiant_id": 1,
        "note": 16.0
    }
    ```
    
    **Réponses :**
    - **200** : Note mise à jour
    - **404** : Note non trouvée
    """
    note = get_object_or_404(NoteDevoir, id=note_id)
    for attr, value in data.dict().items():
        setattr(note, attr, value)
    note.save()
    
    return {
        "id": note.pk,
        "devoir_id": note.devoir.id,
        "etudiant_id": note.etudiant.id,
        "note": note.note,
        "devoir": note.devoir.matiere.nom,
        "etudiant": note.etudiant.nom_prenom,
    }

@examen_route.delete("/notes-devoir/{note_id}")
def delete_note_devoir(request, note_id: int):
    """
    Supprime une note de devoir.
    
    **Paramètres :**
    - **note_id** (int) : ID de la note
    
    **Réponses :**
    - **200** : Note supprimée
    - **404** : Note non trouvée
    """
    note = get_object_or_404(NoteDevoir, id=note_id)
    note.delete()
    return {"success": True}

# ========== GESTION DES NOTES D'EXAMENS ==========

@examen_route.get("/notes-examen", response=list[NoteExamenDetailOut])
def list_notes_examen(request, examen_id: int = None, etudiant_id: int = None, classe_id: int = None):
    """
    Récupère la liste des notes d'examens avec filtres optionnels.
    
    **Paramètres de requête :**
    - **examen_id** (int, optionnel) : Filtrer par examen
    - **etudiant_id** (int, optionnel) : Filtrer par étudiant
    - **classe_id** (int, optionnel) : Filtrer par classe
    
    **Réponse :**
    - **200** : Liste des notes d'examens
    
    **Exemple de réponse :**
    ```json
    [
        {
            "id": 1,
            "examen_id": 1,
            "examen_matiere": "Algorithmes",
            "examen_session": "Semestre 1",
            "etudiant_id": 1,
            "etudiant_nom": "DUPONT Jean",
            "etudiant_matricule": "1234",
            "etudiant_classe": "INFO-1",
            "note": 14.0,
            "coefficient": 3
        }
    ]
    ```
    """
    notes = NoteExamen.objects.select_related(
        'examen__matiere', 'examen__session', 'etudiant__classe'
    ).all()
    
    if examen_id:
        notes = notes.filter(examen_id=examen_id)
    if etudiant_id:
        notes = notes.filter(etudiant_id=etudiant_id)
    if classe_id:
        notes = notes.filter(etudiant__classe_id=classe_id)
    
    return [
        {
            "id": note.pk,
            "examen_id": note.examen.id,
            "examen_matiere": note.examen.matiere.nom,
            "examen_session": note.examen.session.titre,
            "etudiant_id": note.etudiant.id,
            "etudiant_nom": note.etudiant.nom_prenom,
            "etudiant_matricule": note.etudiant.matricule,
            "etudiant_classe": note.etudiant.classe.nom,
            "note": note.note,
            "coefficient": note.examen.matiere.coefficient
        }
        for note in notes
    ]

@examen_route.get("/notes-examen/etudiant/{matricule}", response=list[NoteExamenFilterOut])
def list_notes_examen_etudiant(request, matricule: str):
    """
    Récupère toutes les notes d'examens d'un étudiant spécifique.
    
    **Paramètres :**
    - **matricule** (str) : Matricule de l'étudiant
    
    **Réponses :**
    - **200** : Notes d'examens de l'étudiant
    - **404** : Étudiant non trouvé
    
    **Exemple de réponse :**
    ```json
    [
        {
            "id": 1,
            "examen_id": 1,
            "matiere": "Algorithmes",
            "session": "Semestre 1",
            "etudiant_id": 1,
            "etudiant": "DUPONT Jean",
            "note": 14.0
        }
    ]
    ```
    """
    etudiant = get_object_or_404(Etudiant, matricule=matricule)
    notes = NoteExamen.objects.filter(etudiant=etudiant).select_related(
        'examen__matiere', 'examen__session'
    )
    
    return [
        {
            "id": note.pk,
            "examen_id": note.examen.id,
            "matiere": note.examen.matiere.nom,
            "session": note.examen.session.titre,
            "etudiant_id": note.etudiant.id,
            "etudiant": note.etudiant.nom_prenom,
            "note": note.note
        }
        for note in notes
    ]

@examen_route.post("/notes-examen", response=NoteExamenOut)
def create_note_examen(request, data: NoteExamenCreate):
    """
    Crée une nouvelle note d'examen.
    
    **Corps de la requête :**
    ```json
    {
        "examen_id": 1,
        "etudiant_id": 1,
        "note": 14.0
    }
    ```
    
    **Réponses :**
    - **200** : Note créée avec succès
    - **400** : Données invalides (note déjà existante, valeurs incorrectes)
    """
    note = NoteExamen.objects.create(**data.dict())
    return {
        "id": note.pk,
        "examen_id": note.examen.id,
        "etudiant_id": note.etudiant.id,
        "examen": note.examen.matiere.nom,
        "etudiant": note.etudiant.nom_prenom,
        "note": note.note,
    }

@examen_route.put("/notes-examen/{note_id}", response=NoteExamenOut)
def update_note_examen(request, note_id: int, data: NoteExamenCreate):
    """
    Met à jour une note d'examen existante.
    
    **Paramètres :**
    - **note_id** (int) : ID de la note
    
    **Corps de la requête :**
    ```json
    {
        "examen_id": 1,
        "etudiant_id": 1,
        "note": 15.0
    }
    ```
    
    **Réponses :**
    - **200** : Note mise à jour
    - **404** : Note non trouvée
    """
    note = get_object_or_404(NoteExamen, id=note_id)
    for attr, value in data.dict().items():
        setattr(note, attr, value)
    note.save()
    
    return {
        "id": note.pk,
        "examen_id": note.examen.id,
        "etudiant_id": note.etudiant.id,
        "examen": note.examen.matiere.nom,
        "etudiant": note.etudiant.nom_prenom,
        "note": note.note,
    }

@examen_route.delete("/notes-examen/{note_id}")
def delete_note_examen(request, note_id: int):
    """
    Supprime une note d'examen.
    
    **Paramètres :**
    - **note_id** (int) : ID de la note
    
    **Réponses :**
    - **200** : Note supprimée
    - **404** : Note non trouvée
    """
    note = get_object_or_404(NoteExamen, id=note_id)
    note.delete()
    return {"success": True}

# ========== GESTION DES RÉSULTATS ==========

@examen_route.get("/resultats", response=list[ResultatEtudiantOut])
def list_resultats(request):
    """
    Récupère la liste de tous les résultats des étudiants.
    
    **Réponse :**
    - **200** : Liste des résultats
    
    **Exemple de réponse :**
    ```json
    [
        {
            "id": 1,
            "etudiant": "DUPONT Jean",
            "classe": "INFO-1",
            "moyenne_generale": 14.5,
            "mention": "Bien",
            "photo": "http://example.com/media/photos/photo.jpg"
        }
    ]
    ```
    """
    return [
        {
            "id": resultat.pk,
            "etudiant": resultat.etudiant.nom_prenom,
            "classe": resultat.etudiant.classe.nom,
            "moyenne_generale": resultat.moyenne_generale,
            "mention": resultat.mention,
        }
        for resultat in ResultatEtudiant.objects.all()
    ]

@examen_route.get("/resultat/{matricule}", response=ResultatEtudiantOut)
def resultat_etudiant(request, matricule: str):
    """
    Récupère le résultat d'un étudiant spécifique.
    
    **Paramètres :**
    - **matricule** (str) : Matricule de l'étudiant
    
    **Réponses :**
    - **200** : Résultat de l'étudiant
    - **404** : Étudiant non trouvé
    
    **Exemple de réponse :**
    ```json
    {
        "id": 1,
        "etudiant": "DUPONT Jean",
        "classe": "INFO-1",
        "moyenne_generale": 14.5,
        "mention": "Bien",
        "photo": "http://example.com/media/photos/photo.jpg"
    }
    ```
    """
    etudiant = get_object_or_404(Etudiant, matricule=matricule)
    resultat = ResultatEtudiant.objects.filter(etudiant=etudiant).first()
    
    if not resultat:
        # Calculer la moyenne si pas de résultat enregistré
        moyenne = etudiant.moyenne_generale() or 0
        mention = "En cours"
        if moyenne >= 16:
            mention = "Très Bien"
        elif moyenne >= 14:
            mention = "Bien"
        elif moyenne >= 12:
            mention = "Assez Bien"
        elif moyenne >= 10:
            mention = "Passable"
        else:
            mention = "Échec"
        
        return {
            "id": 0,
            "etudiant": etudiant.nom_prenom,
            "classe": etudiant.classe.nom,
            "moyenne_generale": moyenne,
            "mention": mention,
            "photo": request.build_absolute_uri(etudiant.photo.url) if etudiant.photo else ""
        }
    
    return {
        "id": resultat.pk,
        "etudiant": resultat.etudiant.nom_prenom,
        "classe": resultat.etudiant.classe.nom,
        "moyenne_generale": resultat.moyenne_generale,
        "mention": resultat.mention,
        "photo": request.build_absolute_uri(resultat.etudiant.photo.url) if resultat.etudiant.photo else ""
    }

@examen_route.post("/resultats")
def create_resultat(request, data: ResultatEtudiantCreate):
    """
    Crée un nouveau résultat pour un étudiant.
    
    **Corps de la requête :**
    ```json
    {
        "etudiant_id": 1
    }
    ```
    
    **Réponses :**
    - **200** : Résultat créé avec succès
    - **400** : Données invalides
    """
    ResultatEtudiant.objects.create(**data.dict())
    return {"success": True}