# schemas/financeSchema.py
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
from datetime import date

class EtudiantInfoOut(BaseModel):
    """Informations de base d'un étudiant."""
    id: int
    matricule: str
    nom_prenom: str
    classe: str

    class Config:
        from_attributes = True

class FraisScolariteOut(BaseModel):
    """Frais de scolarité avec informations complètes."""
    id: int
    etudiant_id: int
    etudiant_nom: str
    mois: str
    montant: float = Field(..., ge=0, description="Montant en FCFA")
    date_paiement: str
    is_complet: bool = Field(..., description="Paiement complet ou non")

    class Config:
        from_attributes = True

class FraisScolariteCreate(BaseModel):
    """Données pour créer un frais de scolarité."""
    mois: str = Field(..., description="Mois (ex: Janvier, Février, etc.)")
    montant: Decimal = Field(..., ge=0, description="Montant en FCFA")
    is_complet: bool = Field(default=False, description="Paiement complet")

    class Config:
        from_attributes = True

class FraisScolariteBulkCreate(BaseModel):
    """Données pour créer des frais en masse pour une classe."""
    mois: str = Field(..., description="Mois (ex: Janvier, Février, etc.)")
    montant: Decimal = Field(..., ge=0, description="Montant en FCFA")
    is_complet: bool = Field(default=False, description="Paiement complet par défaut")

    class Config:
        from_attributes = True

class StatutPaiementOut(BaseModel):
    """Mise à jour du statut de paiement."""
    is_complet: Optional[bool] = Field(None, description="Statut du paiement")
    montant: Optional[Decimal] = Field(None, ge=0, description="Nouveau montant")

    class Config:
        from_attributes = True

class EtudiantFinanceOut(BaseModel):
    """État financier complet d'un étudiant."""
    etudiant: EtudiantInfoOut
    frais_scolarite: List[dict]
    total_paye: float = Field(..., ge=0, description="Total payé en FCFA")
    total_du: float = Field(..., ge=0, description="Total dû en FCFA")
    solde: float = Field(..., description="Solde (négatif = dette)")
    mois_impayés: List[str] = Field(..., description="Liste des mois non payés")

    class Config:
        from_attributes = True