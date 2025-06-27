# views/notes.py
from ninja import Router
from django.shortcuts import get_object_or_404
from django.db.models import Q
from parametre.models import Etudiant
from saisie_notes.models import NoteDevoir, NoteExamen
from schemas.notesSchema import (
    NotesEtudiantOut, 
    NoteDetailOut,
    NoteBulkCreateIn,
    NoteBulkUpdateIn,
    NotesStatsOut
)

notes_router = Router()

@notes_router.get("/etudiant/{matricule}", response=NotesEtudiantOut)
def get_notes_etudiant(request, matricule: str):
    """
    Récupère toutes les notes d'un étudiant (devoirs et examens).
    
    **Paramètres :**
    - **matricule** (str) : Matricule de l'étudiant
    
    **Réponses :**
    - **200** : Notes de l'étudiant
    - **404** : Étudiant non trouvé
    
    **Exemple de réponse :**
    ```json
    {
        "etudiant": {
            "id": 1,
            "matricule": "1234",
            "nom_prenom": "DUPONT Jean",
            "classe": "INFO-1"
        },
        "notes_devoirs": [
            {
                "id": 1,
                "matiere": "Algorithmes",
                "note": 15.5,
                "coefficient": 3,
                "session": "Semestre 1"
            }
        ],
        "notes_examens": [
            {
                "id": 1,
                "matiere": "Algorithmes", 
                "note": 14.0,
                "coefficient": 3,
                "session": "Semestre 1"
            }
        ],
        "moyenne_generale": 14.65,
        "nombre_matieres": 5
    }
    ```
    """
    etudiant = get_object_or_404(Etudiant, matricule=matricule)
    
    # Récupération des notes de devoirs
    notes_devoirs = NoteDevoir.objects.filter(etudiant=etudiant).select_related(
        'devoir__matiere', 'devoir__session'
    )
    
    # Récupération des notes d'examens
    notes_examens = NoteExamen.objects.filter(etudiant=etudiant).select_related(
        'examen__matiere', 'examen__session'
    )
    
    return {
        "etudiant": {
            "id": etudiant.pk,
            "matricule": etudiant.matricule,
            "nom_prenom": etudiant.nom_prenom,
            "classe": etudiant.classe.nom
        },
        "notes_devoirs": [
            {
                "id": note.pk,
                "matiere": note.devoir.matiere.nom,
                "note": note.note,
                "coefficient": note.devoir.matiere.coefficient,
                "session": note.devoir.session.titre
            }
            for note in notes_devoirs
        ],
        "notes_examens": [
            {
                "id": note.pk,
                "matiere": note.examen.matiere.nom,
                "note": note.note,
                "coefficient": note.examen.matiere.coefficient,
                "session": note.examen.session.titre
            }
            for note in notes_examens
        ],
        "moyenne_generale": etudiant.moyenne_generale() or 0,
        "nombre_matieres": len(set([n.devoir.matiere.id for n in notes_devoirs] + 
                                 [n.examen.matiere.id for n in notes_examens]))
    }

@notes_router.get("/classe/{classe_id}")
def get_notes_classe(request, classe_id: int, session_id: int = None):
    """
    Récupère les notes de tous les étudiants d'une classe.
    
    **Paramètres :**
    - **classe_id** (int) : ID de la classe
    - **session_id** (int, optionnel) : ID de la session pour filtrer
    
    **Réponses :**
    - **200** : Liste des notes par étudiant
    - **404** : Classe non trouvée
    
    **Exemple de réponse :**
    ```json
    [
        {
            "etudiant": {
                "id": 1,
                "matricule": "1234",
                "nom_prenom": "DUPONT Jean"
            },
            "moyenne_generale": 14.5,
            "nombre_notes": 10
        }
    ]
    ```
    """
    etudiants = Etudiant.objects.filter(classe_id=classe_id)
    
    result = []
    for etudiant in etudiants:
        # Filtrage par session si spécifiée
        notes_devoirs = NoteDevoir.objects.filter(etudiant=etudiant)
        notes_examens = NoteExamen.objects.filter(etudiant=etudiant)
        
        if session_id:
            notes_devoirs = notes_devoirs.filter(devoir__session_id=session_id)
            notes_examens = notes_examens.filter(examen__session_id=session_id)
        
        result.append({
            "etudiant": {
                "id": etudiant.pk,
                "matricule": etudiant.matricule,
                "nom_prenom": etudiant.nom_prenom
            },
            "moyenne_generale": etudiant.moyenne_generale() or 0,
            "nombre_notes": notes_devoirs.count() + notes_examens.count()
        })
    
    return result

@notes_router.post("/bulk-create")
def create_notes_bulk(request, data: NoteBulkCreateIn):
    """
    Création en masse de notes (devoirs ou examens).
    
    **Corps de la requête :**
    ```json
    {
        "type": "devoir",  // ou "examen"
        "evaluation_id": 1,  // ID du devoir ou examen
        "notes": [
            {
                "etudiant_id": 1,
                "note": 15.5
            },
            {
                "etudiant_id": 2,
                "note": 12.0
            }
        ]
    }
    ```
    
    **Réponses :**
    - **200** : Notes créées avec succès
    - **400** : Données invalides
    """
    created_notes = []
    errors = []
    
    for note_data in data.notes:
        try:
            if data.type == "devoir":
                note = NoteDevoir.objects.create(
                    devoir_id=data.evaluation_id,
                    etudiant_id=note_data.etudiant_id,
                    note=note_data.note
                )
            else:  # examen
                note = NoteExamen.objects.create(
                    examen_id=data.evaluation_id,
                    etudiant_id=note_data.etudiant_id,
                    note=note_data.note
                )
            created_notes.append({
                "id": note.pk,
                "etudiant_id": note_data.etudiant_id,
                "note": note_data.note
            })
        except Exception as e:
            errors.append({
                "etudiant_id": note_data.etudiant_id,
                "error": str(e)
            })
    
    return {
        "success": True,
        "created_count": len(created_notes),
        "created_notes": created_notes,
        "errors": errors
    }

@notes_router.put("/bulk-update")
def update_notes_bulk(request, data: NoteBulkUpdateIn):
    """
    Mise à jour en masse de notes existantes.
    
    **Corps de la requête :**
    ```json
    {
        "type": "devoir",  // ou "examen"
        "notes": [
            {
                "id": 1,
                "note": 16.0
            },
            {
                "id": 2,
                "note": 13.5
            }
        ]
    }
    ```
    
    **Réponses :**
    - **200** : Notes mises à jour avec succès
    - **400** : Données invalides
    """
    updated_notes = []
    errors = []
    
    for note_data in data.notes:
        try:
            if data.type == "devoir":
                note = NoteDevoir.objects.get(id=note_data.id)
            else:  # examen
                note = NoteExamen.objects.get(id=note_data.id)
            
            note.note = note_data.note
            note.save()
            
            updated_notes.append({
                "id": note.pk,
                "note": note.note
            })
        except Exception as e:
            errors.append({
                "id": note_data.id,
                "error": str(e)
            })
    
    return {
        "success": True,
        "updated_count": len(updated_notes),
        "updated_notes": updated_notes,
        "errors": errors
    }

@notes_router.get("/statistiques/classe/{classe_id}", response=NotesStatsOut)
def get_statistiques_classe(request, classe_id: int, session_id: int = None):
    """
    Récupère les statistiques des notes d'une classe.
    
    **Paramètres :**
    - **classe_id** (int) : ID de la classe
    - **session_id** (int, optionnel) : ID de la session
    
    **Réponses :**
    - **200** : Statistiques de la classe
    
    **Exemple de réponse :**
    ```json
    {
        "classe_id": 1,
        "nombre_etudiants": 25,
        "moyenne_classe": 13.5,
        "note_max": 18.0,
        "note_min": 8.5,
        "nombre_admis": 20,
        "taux_reussite": 80.0,
        "repartition_mentions": {
            "Très Bien": 3,
            "Bien": 8,
            "Assez Bien": 9,
            "Passable": 0,
            "Échec": 5
        }
    }
    ```
    """
    etudiants = Etudiant.objects.filter(classe_id=classe_id)
    
    if not etudiants.exists():
        return {
            "classe_id": classe_id,
            "nombre_etudiants": 0,
            "moyenne_classe": 0,
            "note_max": 0,
            "note_min": 0,
            "nombre_admis": 0,
            "taux_reussite": 0,
            "repartition_mentions": {}
        }
    
    moyennes = []
    mentions = {"Très Bien": 0, "Bien": 0, "Assez Bien": 0, "Passable": 0, "Échec": 0}
    
    for etudiant in etudiants:
        moyenne = etudiant.moyenne_generale() or 0
        moyennes.append(moyenne)
        
        # Calcul des mentions
        if moyenne >= 16:
            mentions["Très Bien"] += 1
        elif moyenne >= 14:
            mentions["Bien"] += 1
        elif moyenne >= 12:
            mentions["Assez Bien"] += 1
        elif moyenne >= 10:
            mentions["Passable"] += 1
        else:
            mentions["Échec"] += 1
    
    nombre_admis = sum([1 for m in moyennes if m >= 10])
    moyenne_classe = sum(moyennes) / len(moyennes) if moyennes else 0
    
    return {
        "classe_id": classe_id,
        "nombre_etudiants": len(etudiants),
        "moyenne_classe": round(moyenne_classe, 2),
        "note_max": max(moyennes) if moyennes else 0,
        "note_min": min(moyennes) if moyennes else 0,
        "nombre_admis": nombre_admis,
        "taux_reussite": round((nombre_admis / len(etudiants)) * 100, 2) if etudiants else 0,
        "repartition_mentions": mentions
    }