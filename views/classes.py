# views/classes.py
from ninja import Router
from django.shortcuts import get_object_or_404
from parametre.models import Classe, Etudiant
from schemas.scolariteSchema import ClasseOut

classes_router = Router()

@classes_router.get("", response=list[ClasseOut])
def list_classes(request):
    """
    Récupère la liste de toutes les classes.
    
    **Réponse :**
    - **200** : Liste des classes avec leurs informations complètes
    
    **Exemple de réponse :**
    ```json
    [
        {
            "id": 1,
            "nom": "INFO-1",
            "filiere_id": 1,
            "niveau": "Licence 1"
        },
        {
            "id": 2,
            "nom": "GESTION-2", 
            "filiere_id": 2,
            "niveau": "Licence 2"
        }
    ]
    ```
    """
    return [
        {
            "id": classe.pk,
            "nom": classe.nom,
            "filiere_id": classe.filiere.id,
            "niveau": classe.niveau
        }
        for classe in Classe.objects.select_related('filiere').all()
    ]

@classes_router.get("/{classe_id}", response=ClasseOut)
def get_classe(request, classe_id: int):
    """
    Récupère les détails d'une classe spécifique.
    
    **Paramètres :**
    - **classe_id** (int) : ID de la classe
    
    **Réponses :**
    - **200** : Détails de la classe
    - **404** : Classe non trouvée
    
    **Exemple de réponse :**
    ```json
    {
        "id": 1,
        "nom": "INFO-1",
        "filiere_id": 1,
        "niveau": "Licence 1"
    }
    ```
    """
    classe = get_object_or_404(Classe, id=classe_id)
    return {
        "id": classe.pk,
        "nom": classe.nom,
        "filiere_id": classe.filiere.id,
        "niveau": classe.niveau
    }

@classes_router.get("/{classe_id}/etudiants")
def list_etudiants_classe(request, classe_id: int):
    """
    Récupère la liste des étudiants d'une classe spécifique.
    
    **Paramètres :**
    - **classe_id** (int) : ID de la classe
    
    **Réponses :**
    - **200** : Liste des étudiants de la classe
    - **404** : Classe non trouvée
    
    **Exemple de réponse :**
    ```json
    [
        {
            "id": 1,
            "matricule": "1234",
            "nom_prenom": "DUPONT Jean",
            "classe_id": 1,
            "actif": true
        }
    ]
    ```
    """
    classe = get_object_or_404(Classe, id=classe_id)
    etudiants = Etudiant.objects.filter(classe=classe)
    
    return [
        {
            "id": etudiant.pk,
            "matricule": etudiant.matricule,
            "nom_prenom": etudiant.nom_prenom,
            "classe_id": etudiant.classe.id,
            "photo": request.build_absolute_uri(etudiant.photo.url) if etudiant.photo else None,
        }
        for etudiant in etudiants
    ]