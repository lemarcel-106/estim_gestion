from pydantic import BaseModel
from typing import Optional
from datetime import date

# Schéma utilisé pour la lecture (output) avec toutes les infos
class MatiereOut(BaseModel):
    id: int
    nom: str
    classe_id: int
    abreviation: str
    coefficient: int
    classe: str

    class Config:
        from_attributes = True  # Important pour que Django Model fonctionne avec Pydantic

# Schéma utilisé pour la création (input)
class MatiereCreate(BaseModel):
    nom: str
    classe_id: int
    abreviation: str
    coefficient: int = 1


# Schéma utilisé pour la mise à jour (input partiel)
class MatiereUpdate(BaseModel):
    nom: Optional[str] = ""
    classe_id: Optional[int] = 1
    abreviation: Optional[str] = ""
    coefficient: Optional[int] = 1


class ClasseOut(BaseModel):
    id: int
    nom: str
    filiere_id: int
    niveau: str

    class Config:
        from_attributes = True  # Important pour que Django Model fonctionne avec Pydantic
        

class ClasseCreate(BaseModel):
    filiere_id: int
    niveau: str

    class Config:
        from_attributes = True  # Important pour que Django Model fonctionne avec Pydantic


class FilliereOut(BaseModel):
    id: int
    nom: str

    class Config:
        from_attributes = True  # Important pour que Django Model fonctionne avec Pydantic

class FilliereCreate(BaseModel):
    nom: str

    class Config:
        from_attributes = True  # Important pour que Django Model fonctionne avec Pydantic