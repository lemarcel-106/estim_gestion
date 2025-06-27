# views/notes_mobile.py
from ninja import Router
from django.shortcuts import get_object_or_404
from django.db.models import Q
from parametre.models import Etudiant, Classe, Matiere
from examen_devoir.models import Devoir, Examen, SemestreExamen
from saisie_notes.models import NoteDevoir, NoteExamen
from schemas.notesMobileSchema import (
    ClasseNotesConfigOut,
    EtudiantNoteEntryOut,
    NoteSaisieRequest,
    NoteBulkSaisieRequest,
    SaisieNotesResponseOut
)

notes_mobile_router = Router()

@notes_mobile_router.get("/classe/{classe_nom}/configuration")
def get_classe_notes_config(request, classe_nom: str, type_evaluation: str, matiere_id: int = None):
    """
    Configuration pour la saisie de notes d'une classe.
    
    **Paramètres :**
    - **classe_nom** (str) : Nom de la classe (ex: "GI-2", "INFO-1")
    - **type_evaluation** (str) : "devoir" ou "examen"  
    - **matiere_id** (int, optionnel) : ID de la matière pour filtrer
    
    **Réponses :**
    - **200** : Configuration de saisie
    - **404** : Classe non trouvée
    
    **Exemple de réponse :**
    ```json
    {
        "classe": {
            "id": 1,
            "nom": "GI-2",
            "niveau": "Licence 2"
        },
        "matieres": [
            {
                "id": 1,
                "nom": "Français",
                "abreviation": "FR",
                "coefficient": 2
            }
        ],
        "sessions": [
            {
                "id": 1,
                "titre": "Semestre 1 - 2024/2025"
            }
        ],
        "etudiants": [
            {
                "id": 1,
                "matricule": "1234",
                "nom_prenom": "DUPONT Jean",
                "note_existante": null,
                "evaluation_id": null
            }
        ],
        "type_evaluation": "examen",
        "nombre_etudiants": 25
    }
    ```
    """
    # Récupérer la classe
    classe = get_object_or_404(Classe, nom=classe_nom)
    
    # Récupérer les matières de la classe
    matieres_query = Matiere.objects.filter(classe=classe)
    if matiere_id:
        matieres_query = matieres_query.filter(id=matiere_id)
    
    # Récupérer les sessions disponibles
    sessions = SemestreExamen.objects.all().order_by('-id')[:5]  # 5 dernières sessions
    
    # Récupérer les étudiants actifs de la classe
    etudiants = Etudiant.objects.filter(classe=classe, actif=True).order_by('nom_prenom')
    
    # Pour chaque étudiant, vérifier s'il a déjà une note
    etudiants_data = []
    for etudiant in etudiants:
        note_existante = None
        evaluation_id = None
        
        if matiere_id and sessions.exists():
            # Chercher une évaluation existante
            session_actuelle = sessions.first()
            
            if type_evaluation == "devoir":
                devoir = Devoir.objects.filter(
                    matiere_id=matiere_id, 
                    session=session_actuelle
                ).first()
                if devoir:
                    evaluation_id = devoir.id
                    note_obj = NoteDevoir.objects.filter(
                        devoir=devoir, 
                        etudiant=etudiant
                    ).first()
                    if note_obj:
                        note_existante = float(note_obj.note)
            
            elif type_evaluation == "examen":
                examen = Examen.objects.filter(
                    matiere_id=matiere_id, 
                    session=session_actuelle
                ).first()
                if examen:
                    evaluation_id = examen.id
                    note_obj = NoteExamen.objects.filter(
                        examen=examen, 
                        etudiant=etudiant
                    ).first()
                    if note_obj:
                        note_existante = float(note_obj.note)
        
        etudiants_data.append({
            "id": etudiant.pk,
            "matricule": etudiant.matricule,
            "nom_prenom": etudiant.nom_prenom,
            "note_existante": note_existante,
            "evaluation_id": evaluation_id
        })
    
    return {
        "classe": {
            "id": classe.pk,
            "nom": classe.nom,
            "niveau": classe.niveau
        },
        "matieres": [
            {
                "id": matiere.pk,
                "nom": matiere.nom,
                "abreviation": matiere.abreviation,
                "coefficient": matiere.coefficient
            }
            for matiere in matieres_query
        ],
        "sessions": [
            {
                "id": session.pk,
                "titre": session.titre
            }
            for session in sessions
        ],
        "etudiants": etudiants_data,
        "type_evaluation": type_evaluation,
        "nombre_etudiants": len(etudiants_data)
    }

@notes_mobile_router.post("/saisie-evaluation")
def create_ou_update_evaluation(request, data: dict):
    """
    Crée ou récupère une évaluation (devoir/examen) pour la saisie.
    
    **Corps de la requête :**
    ```json
    {
        "type_evaluation": "examen",
        "matiere_id": 1,
        "session_id": 1
    }
    ```
    
    **Réponses :**
    - **200** : Évaluation créée ou récupérée
    - **400** : Données invalides
    
    **Exemple de réponse :**
    ```json
    {
        "evaluation_id": 1,
        "type": "examen",
        "matiere": "Français",
        "session": "Semestre 1",
        "created": false
    }
    ```
    """
    type_evaluation = data.get('type_evaluation')
    matiere_id = data.get('matiere_id')
    session_id = data.get('session_id')
    
    matiere = get_object_or_404(Matiere, id=matiere_id)
    session = get_object_or_404(SemestreExamen, id=session_id)
    
    if type_evaluation == "devoir":
        evaluation, created = Devoir.objects.get_or_create(
            matiere=matiere,
            session=session
        )
    elif type_evaluation == "examen":
        evaluation, created = Examen.objects.get_or_create(
            matiere=matiere,
            session=session
        )
    else:
        return {"error": "Type d'évaluation invalide"}
    
    return {
        "evaluation_id": evaluation.pk,
        "type": type_evaluation,
        "matiere": matiere.nom,
        "session": session.titre,
        "created": created
    }

@notes_mobile_router.post("/saisie-notes-bulk", response=SaisieNotesResponseOut)
def saisie_notes_bulk_mobile(request, data: NoteBulkSaisieRequest):
    """
    Saisie en masse de notes pour mobile avec gestion d'erreurs avancée.
    
    **Corps de la requête :**
    ```json
    {
        "type_evaluation": "examen",
        "evaluation_id": 1,
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
    - **200** : Saisie effectuée avec détails des succès/erreurs
    
    **Exemple de réponse :**
    ```json
    {
        "success": true,
        "total_notes": 25,
        "notes_creees": 20,
        "notes_mises_a_jour": 3,
        "erreurs": 2,
        "details_succes": [
            {
                "etudiant_id": 1,
                "etudiant_nom": "DUPONT Jean",
                "note": 15.5,
                "action": "créée"
            }
        ],
        "details_erreurs": [
            {
                "etudiant_id": 999,
                "erreur": "Étudiant non trouvé",
                "note_tentee": 10.0
            }
        ]
    }
    ```
    """
    notes_creees = 0
    notes_mises_a_jour = 0
    erreurs = 0
    details_succes = []
    details_erreurs = []
    
    for note_data in data.notes:
        try:
            etudiant = Etudiant.objects.get(id=note_data.etudiant_id)
            
            if data.type_evaluation == "devoir":
                note_obj, created = NoteDevoir.objects.update_or_create(
                    devoir_id=data.evaluation_id,
                    etudiant=etudiant,
                    defaults={'note': note_data.note}
                )
            else:  # examen
                note_obj, created = NoteExamen.objects.update_or_create(
                    examen_id=data.evaluation_id,
                    etudiant=etudiant,
                    defaults={'note': note_data.note}
                )
            
            if created:
                notes_creees += 1
                action = "créée"
            else:
                notes_mises_a_jour += 1
                action = "mise à jour"
            
            details_succes.append({
                "etudiant_id": etudiant.id,
                "etudiant_nom": etudiant.nom_prenom,
                "note": float(note_data.note),
                "action": action
            })
            
        except Etudiant.DoesNotExist:
            erreurs += 1
            details_erreurs.append({
                "etudiant_id": note_data.etudiant_id,
                "erreur": "Étudiant non trouvé",
                "note_tentee": float(note_data.note)
            })
        except Exception as e:
            erreurs += 1
            details_erreurs.append({
                "etudiant_id": note_data.etudiant_id,
                "erreur": str(e),
                "note_tentee": float(note_data.note)
            })
    
    return {
        "success": erreurs == 0,
        "total_notes": len(data.notes),
        "notes_creees": notes_creees,
        "notes_mises_a_jour": notes_mises_a_jour,
        "erreurs": erreurs,
        "details_succes": details_succes,
        "details_erreurs": details_erreurs
    }

@notes_mobile_router.get("/verification-notes/{evaluation_id}")
def verification_notes_saisies(request, evaluation_id: int, type_evaluation: str):
    """
    Vérifie les notes déjà saisies pour une évaluation.
    
    **Paramètres :**
    - **evaluation_id** (int) : ID de l'évaluation
    - **type_evaluation** (str) : "devoir" ou "examen"
    
    **Réponses :**
    - **200** : Liste des notes saisies
    - **404** : Évaluation non trouvée
    
    **Exemple de réponse :**
    ```json
    {
        "evaluation_id": 1,
        "type": "examen",
        "matiere": "Français",
        "notes_saisies": [
            {
                "etudiant_id": 1,
                "etudiant_nom": "DUPONT Jean",
                "matricule": "1234",
                "note": 15.5,
                "date_saisie": "2024-01-15T10:30:00"
            }
        ],
        "total_notes": 15,
        "notes_manquantes": 10,
        "pourcentage_completion": 60.0
    }
    ```
    """
    if type_evaluation == "devoir":
        evaluation = get_object_or_404(Devoir, id=evaluation_id)
        notes = NoteDevoir.objects.filter(devoir=evaluation).select_related('etudiant')
        matiere_nom = evaluation.matiere.nom
    else:
        evaluation = get_object_or_404(Examen, id=evaluation_id)
        notes = NoteExamen.objects.filter(examen=evaluation).select_related('etudiant')
        matiere_nom = evaluation.matiere.nom
    
    # Compter le total d'étudiants dans la classe
    if type_evaluation == "devoir":
        total_etudiants = Etudiant.objects.filter(
            classe=evaluation.matiere.classe, 
            actif=True
        ).count()
    else:
        total_etudiants = Etudiant.objects.filter(
            classe=evaluation.matiere.classe, 
            actif=True
        ).count()
    
    notes_saisies_data = [
        {
            "etudiant_id": note.etudiant.id,
            "etudiant_nom": note.etudiant.nom_prenom,
            "matricule": note.etudiant.matricule,
            "note": float(note.note),
            "date_saisie": note.created_at.isoformat() if hasattr(note, 'created_at') else None
        }
        for note in notes
    ]
    
    total_notes_saisies = len(notes_saisies_data)
    notes_manquantes = total_etudiants - total_notes_saisies
    pourcentage_completion = (total_notes_saisies / total_etudiants * 100) if total_etudiants > 0 else 0
    
    return {
        "evaluation_id": evaluation_id,
        "type": type_evaluation,
        "matiere": matiere_nom,
        "notes_saisies": notes_saisies_data,
        "total_notes": total_notes_saisies,
        "notes_manquantes": notes_manquantes,
        "pourcentage_completion": round(pourcentage_completion, 2)
    }

@notes_mobile_router.get("/classes-disponibles")
def get_classes_pour_saisie(request):
    """
    Récupère la liste des classes disponibles pour la saisie de notes.
    
    **Réponses :**
    - **200** : Liste des classes avec nombre d'étudiants
    
    **Exemple de réponse :**
    ```json
    [
        {
            "id": 1,
            "nom": "GI-2",
            "niveau": "Licence 2",
            "filiere": "Génie Informatique",
            "nombre_etudiants": 25,
            "nombre_matieres": 8
        },
        {
            "id": 2,
            "nom": "INFO-1",
            "niveau": "Licence 1", 
            "filiere": "Informatique",
            "nombre_etudiants": 30,
            "nombre_matieres": 6
        }
    ]
    ```
    """
    from django.db.models import Count
    
    classes = Classe.objects.annotate(
        nombre_etudiants=Count('etudiants', filter=Q(etudiants__actif=True)),
        nombre_matieres=Count('matieres')
    ).select_related('filiere')
    
    return [
        {
            "id": classe.pk,
            "nom": classe.nom,
            "niveau": classe.niveau,
            "filiere": classe.filiere.nom,
            "nombre_etudiants": classe.nombre_etudiants,
            "nombre_matieres": classe.nombre_matieres
        }
        for classe in classes
    ]

@notes_mobile_router.get("/matieres/{classe_id}")
def get_matieres_classe(request, classe_id: int):
    """
    Récupère les matières d'une classe pour la saisie.
    
    **Paramètres :**
    - **classe_id** (int) : ID de la classe
    
    **Réponses :**
    - **200** : Liste des matières
    - **404** : Classe non trouvée
    
    **Exemple de réponse :**
    ```json
    [
        {
            "id": 1,
            "nom": "Français",
            "abreviation": "FR",
            "coefficient": 2,
            "devoirs_existants": 2,
            "examens_existants": 1
        }
    ]
    ```
    """
    classe = get_object_or_404(Classe, id=classe_id)
    matieres = Matiere.objects.filter(classe=classe)
    
    result = []
    for matiere in matieres:
        devoirs_count = Devoir.objects.filter(matiere=matiere).count()
        examens_count = Examen.objects.filter(matiere=matiere).count()
        
        result.append({
            "id": matiere.pk,
            "nom": matiere.nom,
            "abreviation": matiere.abreviation,
            "coefficient": matiere.coefficient,
            "devoirs_existants": devoirs_count,
            "examens_existants": examens_count
        })
    
    return result

@notes_mobile_router.post("/note-individuelle")
def saisie_note_individuelle(request, data: NoteSaisieRequest):
    """
    Saisie d'une note individuelle (utile pour les corrections).
    
    **Corps de la requête :**
    ```json
    {
        "type_evaluation": "examen",
        "evaluation_id": 1,
        "etudiant_id": 1,
        "note": 16.5
    }
    ```
    
    **Réponses :**
    - **200** : Note saisie avec succès
    - **400** : Données invalides
    - **404** : Évaluation ou étudiant non trouvé
    
    **Exemple de réponse :**
    ```json
    {
        "success": true,
        "note_id": 1,
        "etudiant": "DUPONT Jean",
        "note": 16.5,
        "action": "mise à jour",
        "ancienne_note": 15.0
    }
    ```
    """
    etudiant = get_object_or_404(Etudiant, id=data.etudiant_id)
    ancienne_note = None
    
    try:
        if data.type_evaluation == "devoir":
            devoir = get_object_or_404(Devoir, id=data.evaluation_id)
            
            # Vérifier si une note existe déjà
            note_existante = NoteDevoir.objects.filter(
                devoir=devoir, 
                etudiant=etudiant
            ).first()
            
            if note_existante:
                ancienne_note = float(note_existante.note)
                note_existante.note = data.note
                note_existante.save()
                note_obj = note_existante
                action = "mise à jour"
            else:
                note_obj = NoteDevoir.objects.create(
                    devoir=devoir,
                    etudiant=etudiant,
                    note=data.note
                )
                action = "création"
                
        else:  # examen
            examen = get_object_or_404(Examen, id=data.evaluation_id)
            
            # Vérifier si une note existe déjà
            note_existante = NoteExamen.objects.filter(
                examen=examen, 
                etudiant=etudiant
            ).first()
            
            if note_existante:
                ancienne_note = float(note_existante.note)
                note_existante.note = data.note
                note_existante.save()
                note_obj = note_existante
                action = "mise à jour"
            else:
                note_obj = NoteExamen.objects.create(
                    examen=examen,
                    etudiant=etudiant,
                    note=data.note
                )
                action = "création"
        
        return {
            "success": True,
            "note_id": note_obj.pk,
            "etudiant": etudiant.nom_prenom,
            "note": float(data.note),
            "action": action,
            "ancienne_note": ancienne_note
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "etudiant": etudiant.nom_prenom
        }