from ninja import Router
from django.contrib.admin.models import LogEntry
from django.db.models import Sum, Count, Q
from datetime import datetime
from parametre.models import Etudiant, Classe
from finances.models import FraisScolarite
from examen_devoir.models import Devoir, Examen
from schemas.apiSchema import (
    EtudiantApiOut, 
    FinanceApiOut, 
    ExamenApiOut, 
    LogEntryOut, 
    StatistiqueFinanceOut,
    StatistiqueClasseOut
)

api_router = Router()

# 1. Récupération de la liste des étudiants (tous les étudiants)
@api_router.get("/etudiants", response=list[EtudiantApiOut])
def list_all_etudiants(request):
    """
    Récupère la liste complète de tous les étudiants
    """
    return [
        {
            "id": etudiant.pk,
            "matricule": etudiant.matricule,
            "nom_prenom": etudiant.nom_prenom,
            "classe_id": etudiant.classe.id,
            "classe_nom": etudiant.classe.nom,
            "date_naissance": etudiant.date_naissance,
            "lieu_naissance": etudiant.lieu_naissance,
            "photo": request.build_absolute_uri(etudiant.photo.url) if etudiant.photo else None,
            "actif": etudiant.actif,
            "annee_scolaire": etudiant.annee_scolaire
        }
        for etudiant in Etudiant.objects.select_related('classe').all()
    ]

# 2. Récupération de la liste des finances
@api_router.get("/finances", response=list[FinanceApiOut])
def list_finances(request):
    """
    Récupère la liste complète des frais de scolarité
    """
    return [
        {
            "id": frais.pk,
            "etudiant_id": frais.etudiant.id,
            "etudiant_nom": frais.etudiant.nom_prenom,
            "etudiant_matricule": frais.etudiant.matricule,
            "classe_nom": frais.etudiant.classe.nom,
            "mois": frais.mois,
            "montant": float(frais.montant),
            "date_paiement": frais.date_paiement,
            "is_complet": frais.is_complet
        }
        for frais in FraisScolarite.objects.select_related('etudiant__classe').all()
    ]

# 3. Récupération de la liste des examens avec paramètre type d'après une classe
@api_router.get("/examens/classe/{classe_id}", response=list[ExamenApiOut])
def list_examens_by_classe_type(request, classe_id: int, type: str = "examen"):
    """
    Récupère la liste des examens ou devoirs pour une classe donnée
    type: 'examen' ou 'devoir'
    """
    if type.lower() == "devoir":
        devoirs = Devoir.objects.filter(matiere__classe_id=classe_id).select_related('matiere', 'session')
        return [
            {
                "id": devoir.pk,
                "type": "devoir",
                "matiere_id": devoir.matiere.id,
                "matiere_nom": devoir.matiere.nom,
                "classe_id": classe_id,
                "session_id": devoir.session.id,
                "session_titre": devoir.session.titre,
                "coefficient": devoir.matiere.coefficient
            }
            for devoir in devoirs
        ]
    else:  # type == "examen"
        examens = Examen.objects.filter(matiere__classe_id=classe_id).select_related('matiere', 'session')
        return [
            {
                "id": examen.pk,
                "type": "examen",
                "matiere_id": examen.matiere.id,
                "matiere_nom": examen.matiere.nom,
                "classe_id": classe_id,
                "session_id": examen.session.id,
                "session_titre": examen.session.titre,
                "coefficient": examen.matiere.coefficient
            }
            for examen in examens
        ]

# 4. Récupération de tous les logs Django
@api_router.get("/logs", response=list[LogEntryOut])
def list_django_logs(request):
    """
    Récupère tous les logs Django de l'administration
    """
    return [
        {
            "id": log.pk,
            "action_time": log.action_time,
            "user_id": log.user_id,
            "user_username": log.user.username if log.user else None,
            "content_type_id": log.content_type_id,
            "content_type": str(log.content_type) if log.content_type else None,
            "object_id": log.object_id,
            "object_repr": log.object_repr,
            "action_flag": log.action_flag,
            "change_message": log.change_message
        }
        for log in LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')
    ]

# 5. Route statistique pour récupérer les finances par classe étudiant et nombre d'étudiants par classe
@api_router.get("/statistiques/finances", response=list[StatistiqueFinanceOut])
def statistiques_finances_par_classe(request):
    """
    Statistiques des finances par classe:
    - Total payé le mois en cours pour chaque classe
    - Nombre d'étudiants par classe
    """
    # Récupérer le mois actuel
    mois_actuel = datetime.now().strftime('%B')  # Format: 'January', 'February', etc.
    
    # Mapping des mois en français (selon le tuple MOIS_CHOICES du modèle)
    mois_mapping = {
        'January': 'Janvier',
        'February': 'Février',
        'March': 'Mars',
        'April': 'Avril',
        'May': 'Mai',
        'June': 'Juin',
        'July': 'Juillet',
        'August': 'Août',     # Note: Dans le modèle, il n'y a pas 'Août' et 'Septembre'
        'September': 'Septembre',
        'October': 'Octobre',
        'November': 'Novembre',
        'December': 'Décembre'
    }
    
    mois_francais = mois_mapping.get(mois_actuel, 'Janvier')
    
    classes = Classe.objects.all()
    statistiques = []
    
    for classe in classes:
        # Compter le nombre d'étudiants par classe
        nombre_etudiants = Etudiant.objects.filter(classe=classe, actif=True).count()
        
        # Calculer le total payé pour le mois en cours pour cette classe
        total_paye_mois = FraisScolarite.objects.filter(
            etudiant__classe=classe,
            mois=mois_francais,
            is_complet=True
        ).aggregate(total=Sum('montant'))['total'] or 0
        
        # Calculer le total général pour cette classe (tous les mois)
        total_general = FraisScolarite.objects.filter(
            etudiant__classe=classe,
            is_complet=True
        ).aggregate(total=Sum('montant'))['total'] or 0
        
        # Nombre de paiements en attente pour cette classe
        paiements_en_attente = FraisScolarite.objects.filter(
            etudiant__classe=classe,
            is_complet=False
        ).count()
        
        statistiques.append({
            "classe_id": classe.id,
            "classe_nom": classe.nom,
            "nombre_etudiants": nombre_etudiants,
            "mois_actuel": mois_francais,
            "total_paye_mois_actuel": float(total_paye_mois),
            "total_general_paye": float(total_general),
            "paiements_en_attente": paiements_en_attente
        })
    
    return statistiques

# 6. Route statistique additionnelle pour les classes
@api_router.get("/statistiques/classes", response=list[StatistiqueClasseOut])
def statistiques_classes(request):
    """
    Statistiques générales par classe
    """
    classes = Classe.objects.all()
    statistiques = []
    
    for classe in classes:
        nombre_etudiants_actifs = Etudiant.objects.filter(classe=classe, actif=True).count()
        nombre_etudiants_inactifs = Etudiant.objects.filter(classe=classe, actif=False).count()
        total_etudiants = nombre_etudiants_actifs + nombre_etudiants_inactifs
        
        # Calculer le pourcentage de présence
        pourcentage_actifs = (nombre_etudiants_actifs / total_etudiants * 100) if total_etudiants > 0 else 0
        
        statistiques.append({
            "classe_id": classe.id,
            "classe_nom": classe.nom,
            "filiere_nom": classe.filiere.nom,
            "niveau": classe.niveau,
            "total_etudiants": total_etudiants,
            "etudiants_actifs": nombre_etudiants_actifs,
            "etudiants_inactifs": nombre_etudiants_inactifs,
            "pourcentage_actifs": round(pourcentage_actifs, 2)
        })
    
    return statistiques

# 7. Route bonus: Statistiques générales du système
@api_router.get("/statistiques/general")
def statistiques_generales(request):
    """
    Statistiques générales du système
    """
    total_etudiants = Etudiant.objects.count()
    total_etudiants_actifs = Etudiant.objects.filter(actif=True).count()
    total_classes = Classe.objects.count()
    
    # Total des finances
    total_revenus = FraisScolarite.objects.filter(is_complet=True).aggregate(
        total=Sum('montant')
    )['total'] or 0
    
    total_en_attente = FraisScolarite.objects.filter(is_complet=False).aggregate(
        total=Sum('montant')
    )['total'] or 0
    
    # Mois actuel
    mois_actuel = datetime.now().strftime('%B')
    mois_mapping = {
        'January': 'Janvier', 'February': 'Février', 'March': 'Mars',
        'April': 'Avril', 'May': 'Mai', 'June': 'Juin',
        'July': 'Juillet', 'October': 'Octobre', 
        'November': 'Novembre', 'December': 'Décembre'
    }
    mois_francais = mois_mapping.get(mois_actuel, 'Janvier')
    
    revenus_mois_actuel = FraisScolarite.objects.filter(
        mois=mois_francais,
        is_complet=True
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    return {
        "total_etudiants": total_etudiants,
        "etudiants_actifs": total_etudiants_actifs,
        "etudiants_inactifs": total_etudiants - total_etudiants_actifs,
        "total_classes": total_classes,
        "mois_actuel": mois_francais,
        "revenus_totaux": float(total_revenus),
        "revenus_en_attente": float(total_en_attente),
        "revenus_mois_actuel": float(revenus_mois_actuel),
        "taux_paiement_global": round((float(total_revenus) / (float(total_revenus) + float(total_en_attente)) * 100), 2) if (total_revenus + total_en_attente) > 0 else 0
    }