# schemas/notesMobileSchema.py
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal

class ClasseInfoOut(BaseModel):
    """Informations de base d'une classe."""
    id: int
    nom: str = Field(..., description="Nom de la classe (ex: GI-2, INFO-1)")
    niveau: str = Field(..., description="Niveau (ex: Licence 1, Licence 2)")

    class Config:
        from_attributes = True

class MatiereInfoOut(BaseModel):
    """Informations d'une matière."""
    id: int
    nom: str = Field(..., description="Nom de la matière")
    abreviation: str = Field(..., description="Abréviation de la matière")
    coefficient: int = Field(..., ge=1, description="Coefficient de la matière")

    class Config:
        from_attributes = True

class SessionInfoOut(BaseModel):
    """Informations d'une session d'examens."""
    id: int
    titre: str = Field(..., description="Titre de la session")

    class Config:
        from_attributes = True

class EtudiantNoteEntryOut(BaseModel):
    """Étudiant avec possibilité de saisie de note."""
    id: int
    matricule: str
    nom_prenom: str
    note_existante: Optional[float] = Field(None, ge=0, le=20, description="Note déjà saisie")
    evaluation_id: Optional[int] = Field(None, description="ID de l'évaluation existante")

    class Config:
        from_attributes = True

class ClasseNotesConfigOut(BaseModel):
    """Configuration complète pour la saisie de notes d'une classe."""
    classe: ClasseInfoOut
    matieres: List[MatiereInfoOut]
    sessions: List[SessionInfoOut]
    etudiants: List[EtudiantNoteEntryOut]
    type_evaluation: str = Field(..., pattern="^(devoir|examen)$")
    nombre_etudiants: int = Field(..., ge=0)

    class Config:
        from_attributes = True

class NoteSaisieRequest(BaseModel):
    """Requête pour saisir une note individuelle."""
    type_evaluation: str = Field(..., pattern="^(devoir|examen)$", description="Type d'évaluation")
    evaluation_id: int = Field(..., description="ID de l'évaluation")
    etudiant_id: int = Field(..., description="ID de l'étudiant")
    note: Decimal = Field(..., ge=0, le=20, description="Note entre 0 et 20")

    class Config:
        from_attributes = True

class NoteBulkEntryRequest(BaseModel):
    """Entrée pour saisie en masse."""
    etudiant_id: int = Field(..., description="ID de l'étudiant")
    note: Decimal = Field(..., ge=0, le=20, description="Note entre 0 et 20")

    class Config:
        from_attributes = True

class NoteBulkSaisieRequest(BaseModel):
    """Requête pour saisie en masse de notes."""
    type_evaluation: str = Field(..., pattern="^(devoir|examen)$", description="Type d'évaluation")
    evaluation_id: int = Field(..., description="ID de l'évaluation")
    notes: List[NoteBulkEntryRequest] = Field(..., min_items=1, description="Liste des notes à saisir")

    class Config:
        from_attributes = True

class NoteSuccesDetail(BaseModel):
    """Détail d'une note saisie avec succès."""
    etudiant_id: int
    etudiant_nom: str
    note: float
    action: str = Field(..., description="'créée' ou 'mise à jour'")

    class Config:
        from_attributes = True

class NoteErreurDetail(BaseModel):
    """Détail d'une erreur de saisie."""
    etudiant_id: int
    erreur: str = Field(..., description="Description de l'erreur")
    note_tentee: float

    class Config:
        from_attributes = True

class SaisieNotesResponseOut(BaseModel):
    """Réponse de la saisie en masse."""
    success: bool
    total_notes: int = Field(..., ge=0)
    notes_creees: int = Field(..., ge=0)
    notes_mises_a_jour: int = Field(..., ge=0)
    erreurs: int = Field(..., ge=0)
    details_succes: List[NoteSuccesDetail]
    details_erreurs: List[NoteErreurDetail]

    class Config:
        from_attributes = True

class ClasseDisponibleOut(BaseModel):
    """Classe disponible pour saisie."""
    id: int
    nom: str
    niveau: str
    filiere: str
    nombre_etudiants: int = Field(..., ge=0)
    nombre_matieres: int = Field(..., ge=0)

    class Config:
        from_attributes = True

class MatiereAvecStatsOut(BaseModel):
    """Matière avec statistiques d'évaluations."""
    id: int
    nom: str
    abreviation: str
    coefficient: int
    devoirs_existants: int = Field(..., ge=0)
    examens_existants: int = Field(..., ge=0)

    class Config:
        from_attributes = True