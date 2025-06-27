# views/finances.py
from ninja import Router
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q
from decimal import Decimal
from parametre.models import Etudiant, Classe
from finances.models import FraisScolarite
from schemas.financeSchema import (
    FraisScolariteOut,
    FraisScolariteCreate,
    FraisScolariteBulkCreate,
    EtudiantFinanceOut,
    StatutPaiementOut
)

finance_router = Router()

@finance_router.get("/etudiant/{matricule}", response=EtudiantFinanceOut)
def get_finance_etudiant(request, matricule: str):
    """
    Récupère l'état financier complet d'un étudiant.
    
    **Paramètres :**
    - **matricule** (str) : Matricule de l'étudiant
    
    **Réponses :**
    - **200** : État financier de l'étudiant
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
        "frais_scolarite": [
            {
                "id": 1,
                "mois": "Janvier",
                "montant": 50000.00,
                "date_paiement": "2024-01-15",
                "is_complet": true
            }
        ],
        "total_paye": 150000.00,
        "total_du": 200000.00,
        "solde": -50000.00,
        "mois_impayés": ["Février", "Mars"]
    }
    ```
    """
    etudiant = get_object_or_404(Etudiant, matricule=matricule)
    frais = FraisScolarite.objects.filter(etudiant=etudiant).order_by('mois')
    
    # Calculs financiers
    total_paye = frais.filter(is_complet=True).aggregate(Sum('montant'))['montant__sum'] or Decimal('0')
    total_du = frais.aggregate(Sum('montant'))['montant__sum'] or Decimal('0')
    solde = total_paye - total_du
    mois_impayés = list(frais.filter(is_complet=False).values_list('mois', flat=True))
    
    return {
        "etudiant": {
            "id": etudiant.pk,
            "matricule": etudiant.matricule,
            "nom_prenom": etudiant.nom_prenom,
            "classe": etudiant.classe.nom
        },
        "frais_scolarite": [
            {
                "id": frais_item.pk,
                "mois": frais_item.mois,
                "montant": float(frais_item.montant),
                "date_paiement": frais_item.date_paiement.isoformat(),
                "is_complet": frais_item.is_complet
            }
            for frais_item in frais
        ],
        "total_paye": float(total_paye),
        "total_du": float(total_du),
        "solde": float(solde),
        "mois_impayés": mois_impayés
    }

@finance_router.post("/etudiant/{matricule}/frais", response=FraisScolariteOut)
def create_frais_etudiant(request, matricule: str, data: FraisScolariteCreate):
    """
    Crée un frais de scolarité pour un étudiant spécifique.
    
    **Paramètres :**
    - **matricule** (str) : Matricule de l'étudiant
    
    **Corps de la requête :**
    ```json
    {
        "mois": "Janvier",
        "montant": 50000.00,
        "is_complet": false
    }
    ```
    
    **Réponses :**
    - **200** : Frais créé avec succès
    - **400** : Données invalides ou frais déjà existant pour ce mois
    - **404** : Étudiant non trouvé
    """
    etudiant = get_object_or_404(Etudiant, matricule=matricule)
    
    frais = FraisScolarite.objects.create(
        etudiant=etudiant,
        mois=data.mois,
        montant=data.montant,
        is_complet=data.is_complet
    )
    
    return {
        "id": frais.pk,
        "etudiant_id": frais.etudiant.id,
        "etudiant_nom": frais.etudiant.nom_prenom,
        "mois": frais.mois,
        "montant": float(frais.montant),
        "date_paiement": frais.date_paiement.isoformat(),
        "is_complet": frais.is_complet
    }

@finance_router.post("/classe/{classe_id}/frais-bulk", response=dict)
def create_frais_classe_bulk(request, classe_id: int, data: FraisScolariteBulkCreate):
    """
    Crée des frais de scolarité en masse pour tous les étudiants d'une classe.
    
    **Paramètres :**
    - **classe_id** (int) : ID de la classe
    
    **Corps de la requête :**
    ```json
    {
        "mois": "Janvier",
        "montant": 50000.00,
        "is_complet": false
    }
    ```
    
    **Réponses :**
    - **200** : Frais créés avec succès
    - **400** : Données invalides
    - **404** : Classe non trouvée
    
    **Exemple de réponse :**
    ```json
    {
        "success": true,
        "created_count": 25,
        "classe": "INFO-1",
        "mois": "Janvier",
        "montant": 50000.00,
        "errors": []
    }
    ```
    """
    classe = get_object_or_404(Classe, id=classe_id)
    etudiants = Etudiant.objects.filter(classe=classe, actif=True)
    
    created_count = 0
    errors = []
    
    for etudiant in etudiants:
        try:
            FraisScolarite.objects.create(
                etudiant=etudiant,
                mois=data.mois,
                montant=data.montant,
                is_complet=data.is_complet
            )
            created_count += 1
        except Exception as e:
            errors.append({
                "etudiant": etudiant.nom_prenom,
                "matricule": etudiant.matricule,
                "error": str(e)
            })
    
    return {
        "success": True,
        "created_count": created_count,
        "classe": classe.nom,
        "mois": data.mois,
        "montant": float(data.montant),
        "errors": errors
    }

@finance_router.put("/frais/{frais_id}/statut")
def update_statut_paiement(request, frais_id: int, data: StatutPaiementOut):
    """
    Met à jour le statut de paiement d'un frais.
    
    **Paramètres :**
    - **frais_id** (int) : ID du frais
    
    **Corps de la requête :**
    ```json
    {
        "is_complet": true,
        "montant": 50000.00
    }
    ```
    
    **Réponses :**
    - **200** : Statut mis à jour
    - **404** : Frais non trouvé
    """
    frais = get_object_or_404(FraisScolarite, id=frais_id)
    
    if hasattr(data, 'montant') and data.montant is not None:
        frais.montant = data.montant
    if hasattr(data, 'is_complet') and data.is_complet is not None:
        frais.is_complet = data.is_complet
    
    frais.save()
    
    return {
        "success": True,
        "id": frais.pk,
        "etudiant": frais.etudiant.nom_prenom,
        "mois": frais.mois,
        "montant": float(frais.montant),
        "is_complet": frais.is_complet
    }

@finance_router.get("/classe/{classe_id}/finances")
def get_finances_classe(request, classe_id: int, mois: str = None):
    """
    Récupère l'état financier de tous les étudiants d'une classe.
    
    **Paramètres :**
    - **classe_id** (int) : ID de la classe
    - **mois** (str, optionnel) : Filtrer par mois
    
    **Réponses :**
    - **200** : Liste des états financiers
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
            "total_paye": 150000.00,
            "total_du": 200000.00,
            "solde": -50000.00,
            "statut": "En retard"
        }
    ]
    ```
    """
    classe = get_object_or_404(Classe, id=classe_id)
    etudiants = Etudiant.objects.filter(classe=classe, actif=True)
    
    result = []
    for etudiant in etudiants:
        frais_query = FraisScolarite.objects.filter(etudiant=etudiant)
        
        if mois:
            frais_query = frais_query.filter(mois=mois)
        
        total_paye = frais_query.filter(is_complet=True).aggregate(Sum('montant'))['montant__sum'] or Decimal('0')
        total_du = frais_query.aggregate(Sum('montant'))['montant__sum'] or Decimal('0')
        solde = total_paye - total_du
        
        # Déterminer le statut
        if solde >= 0:
            statut = "À jour"
        elif solde > -10000:  # Seuil de tolérance
            statut = "Attention"
        else:
            statut = "En retard"
        
        result.append({
            "etudiant": {
                "id": etudiant.pk,
                "matricule": etudiant.matricule,
                "nom_prenom": etudiant.nom_prenom
            },
            "total_paye": float(total_paye),
            "total_du": float(total_du),
            "solde": float(solde),
            "statut": statut
        })
    
    return result

@finance_router.get("/statistiques/classe/{classe_id}")
def get_statistiques_financieres_classe(request, classe_id: int):
    """
    Récupère les statistiques financières d'une classe.
    
    **Paramètres :**
    - **classe_id** (int) : ID de la classe
    
    **Réponses :**
    - **200** : Statistiques financières
    - **404** : Classe non trouvée
    
    **Exemple de réponse :**
    ```json
    {
        "classe": "INFO-1",
        "nombre_etudiants": 25,
        "total_attendu": 1250000.00,
        "total_percu": 800000.00,
        "taux_recouvrement": 64.0,
        "etudiants_a_jour": 15,
        "etudiants_en_retard": 10,
        "montant_impaye": 450000.00
    }
    ```
    """
    classe = get_object_or_404(Classe, id=classe_id)
    etudiants = Etudiant.objects.filter(classe=classe, actif=True)
    
    total_attendu = Decimal('0')
    total_percu = Decimal('0')
    etudiants_a_jour = 0
    etudiants_en_retard = 0
    
    for etudiant in etudiants:
        frais = FraisScolarite.objects.filter(etudiant=etudiant)
        etudiant_du = frais.aggregate(Sum('montant'))['montant__sum'] or Decimal('0')
        etudiant_paye = frais.filter(is_complet=True).aggregate(Sum('montant'))['montant__sum'] or Decimal('0')
        
        total_attendu += etudiant_du
        total_percu += etudiant_paye
        
        if etudiant_paye >= etudiant_du:
            etudiants_a_jour += 1
        else:
            etudiants_en_retard += 1
    
    taux_recouvrement = (float(total_percu) / float(total_attendu) * 100) if total_attendu > 0 else 0
    montant_impaye = total_attendu - total_percu
    
    return {
        "classe": classe.nom,
        "nombre_etudiants": len(etudiants),
        "total_attendu": float(total_attendu),
        "total_percu": float(total_percu),
        "taux_recouvrement": round(taux_recouvrement, 2),
        "etudiants_a_jour": etudiants_a_jour,
        "etudiants_en_retard": etudiants_en_retard,
        "montant_impaye": float(montant_impaye)
    }