from ninja import Schema
from datetime import date
from typing import Optional

class EtudiantBase(Schema):
    actif: Optional[bool] = False
    nom_prenom: str
    matricule: str
    classe: Optional[int] = 1
    photo: Optional[str] = ""

class EtudiantCreate(Schema):
    nom_prenom: str
    classe_id: int


class EtudiantDateLieu(Schema):
    date_naissance: date
    lieu_naissance: str

class EtudiantUpdate(Schema):
    nom_prenom: str
    classe_id: Optional[int] = None

class EtudiantOut(EtudiantBase):
    id: int
    class Config:
        from_attributes = True
