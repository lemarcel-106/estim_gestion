from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

# Schéma pour la liste complète des étudiants
class EtudiantApiOut(BaseModel):
    id: int
    matricule: str
    nom_prenom: str
    classe_id: int
    classe_nom: str
    date_naissance: Optional[date] = None
    lieu_naissance: Optional[str] = None
    photo: Optional[str] = None
    actif: bool
    annee_scolaire: str

    class Config:
        from_attributes = True

# Schéma pour les finances
class FinanceApiOut(BaseModel):
    id: int
    etudiant_id: int
    etudiant_nom: str
    etudiant_matricule: str
    classe_nom: str
    mois: str
    montant: float
    date_paiement: date
    is_complet: bool

    class Config:
        from_attributes = True

# Schéma pour les examens/devoirs avec filtrage par classe
class ExamenApiOut(BaseModel):
    id: int
    type: str  # "examen" ou "devoir"
    matiere_id: int
    matiere_nom: str
    classe_id: int
    session_id: int
    session_titre: str
    coefficient: int

    class Config:
        from_attributes = True

# Schéma pour les logs Django
class LogEntryOut(BaseModel):
    id: int
    action_time: datetime
    user_id: Optional[int] = None
    user_username: Optional[str] = None
    content_type_id: Optional[int] = None
    content_type: Optional[str] = None
    object_id: Optional[str] = None
    object_repr: str
    action_flag: int
    change_message: str

    class Config:
        from_attributes = True

# Schéma pour les statistiques de finances par classe
class StatistiqueFinanceOut(BaseModel):
    classe_id: int
    classe_nom: str
    nombre_etudiants: int
    mois_actuel: str
    total_paye_mois_actuel: float
    total_general_paye: float
    paiements_en_attente: int

    class Config:
        from_attributes = True

# Schéma pour les statistiques de classes
class StatistiqueClasseOut(BaseModel):
    classe_id: int
    classe_nom: str
    filiere_nom: str
    niveau: str
    total_etudiants: int
    etudiants_actifs: int
    etudiants_inactifs: int
    pourcentage_actifs: float

    class Config:
        from_attributes = True

# Schéma pour les statistiques générales (optionnel)
class StatistiqueGeneraleOut(BaseModel):
    total_etudiants: int
    etudiants_actifs: int
    etudiants_inactifs: int
    total_classes: int
    mois_actuel: str
    revenus_totaux: float
    revenus_en_attente: float
    revenus_mois_actuel: float
    taux_paiement_global: float

    class Config:
        from_attributes = True