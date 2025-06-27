# schemas/notesSchema.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class EtudiantInfoOut(BaseModel):
    """Informations de base d'un étudiant."""
    id: int
    matricule: str
    nom_prenom: str
    classe: str

    class Config:
        from_attributes = True

class NoteDetailOut(BaseModel):
    """Détail d'une note avec informations de la matière."""
    id: int
    matiere: str
    note: float = Field(..., ge=0, le=20, description="Note entre 0 et 20")
    coefficient: int = Field(..., ge=1, description="Coefficient de la matière")
    session: str

    class Config:
        from_attributes = True

class NotesEtudiantOut(BaseModel):
    """Toutes les notes d'un étudiant."""
    etudiant: EtudiantInfoOut
    notes_devoirs: List[NoteDetailOut]
    notes_examens: List[NoteDetailOut]
    moyenne_generale: float = Field(..., ge=0, le=20)
    nombre_matieres: int = Field(..., ge=0)

    class Config:
        from_attributes = True

class NoteCreateIn(BaseModel):
    """Données pour créer une note individuelle."""
    etudiant_id: int = Field(..., description="ID de l'étudiant")
    note: float = Field(..., ge=0, le=20, description="Note entre 0 et 20")

    class Config:
        from_attributes = True

class NoteBulkCreateIn(BaseModel):
    """Données pour créer plusieurs notes en masse."""
    type: str = Field(..., pattern="^(devoir|examen)$", description="Type d'évaluation")
    evaluation_id: int = Field(..., description="ID du devoir ou de l'examen")
    notes: List[NoteCreateIn] = Field(..., min_items=1, description="Liste des notes à créer")

    class Config:
        from_attributes = True

class NoteUpdateIn(BaseModel):
    """Données pour mettre à jour une note."""
    id: int = Field(..., description="ID de la note")
    note: float = Field(..., ge=0, le=20, description="Nouvelle note entre 0 et 20")

    class Config:
        from_attributes = True

class NoteBulkUpdateIn(BaseModel):
    """Données pour mettre à jour plusieurs notes en masse."""
    type: str = Field(..., pattern="^(devoir|examen)$", description="Type d'évaluation")
    notes: List[NoteUpdateIn] = Field(..., min_items=1, description="Liste des notes à modifier")

    class Config:
        from_attributes = True

class EtudiantNotesResumeOut(BaseModel):
    """Résumé des notes d'un étudiant."""
    etudiant: EtudiantInfoOut
    moyenne_generale: float = Field(..., ge=0, le=20)
    nombre_notes: int = Field(..., ge=0)

    class Config:
        from_attributes = True

class NotesStatsOut(BaseModel):
    """Statistiques des notes d'une classe."""
    classe_id: int
    nombre_etudiants: int = Field(..., ge=0)
    moyenne_classe: float = Field(..., ge=0, le=20)
    note_max: float = Field(..., ge=0, le=20)
    note_min: float = Field(..., ge=0, le=20)
    nombre_admis: int = Field(..., ge=0)
    taux_reussite: float = Field(..., ge=0, le=100, description="Pourcentage de réussite")
    repartition_mentions: Dict[str, int] = Field(..., description="Répartition par mention")

    class Config:
        from_attributes = True

# Schémas pour les endpoints existants améliorés
class NoteDevoirDetailOut(BaseModel):
    """Note de devoir avec détails complets."""
    id: int
    devoir_id: int
    devoir_matiere: str
    devoir_session: str
    etudiant_id: int
    etudiant_nom: str
    etudiant_matricule: str
    etudiant_classe: str
    note: float = Field(..., ge=0, le=20)
    coefficient: int

    class Config:
        from_attributes = True

class NoteExamenDetailOut(BaseModel):
    """Note d'examen avec détails complets."""
    id: int
    examen_id: int
    examen_matiere: str
    examen_session: str
    etudiant_id: int
    etudiant_nom: str
    etudiant_matricule: str
    etudiant_classe: str
    note: float = Field(..., ge=0, le=20)
    coefficient: int

    class Config:
        from_attributes = True

class NoteDevoirFilterOut(BaseModel):
    """Note de devoir avec filtres appliqués."""
    id: int
    devoir_id: int
    matiere: str
    session: str
    etudiant_id: int
    etudiant: str
    note: float
    date_creation: Optional[str] = None

    class Config:
        from_attributes = True

class NoteExamenFilterOut(BaseModel):
    """Note d'examen avec filtres appliqués.""" 
    id: int
    examen_id: int
    matiere: str
    session: str
    etudiant_id: int
    etudiant: str
    note: float
    date_creation: Optional[str] = None

    class Config:
        from_attributes = True