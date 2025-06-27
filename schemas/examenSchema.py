from pydantic import BaseModel
from datetime import date

class SessionExamenOut(BaseModel):
    id: int
    titre: str
    anneee_scolaire: str
    date_debut: date

    class Config:
        from_attributes = True

class SessionExamenCreate(BaseModel):
    titre: str
    anneee_scolaire: str

class SessionExamenUpdate(BaseModel):
    titre: str= None
    anneee_scolaire: str = None



class ResultatEtudiantOut(BaseModel):
    id: int
    etudiant: str
    classe: str
    moyenne_generale: float
    mention: str 
    photo: str 

    class Config:
        from_attributes = True

class ResultatEtudiantCreate(BaseModel):
    etudiant_id: int
   




class DevoirOut(BaseModel):
    id: int
    matiere_id: int
    matiere: str
    session_id: int
    session: str
    # date: date

    class Config:
        from_attributes = True

class DevoirCreate(BaseModel):
    matiere_id: int
    session_id: int




class ExamenOut(BaseModel):
    id: int
    matiere_id: int
    matiere: str
    session_id: int
    session: str
    # date: date

    class Config:
        from_attributes = True

class ExamenCreate(BaseModel):
    matiere_id: int
    session_id: int



class NoteDevoirOut(BaseModel):
    id: int
    devoir_id: int
    devoir: str
    etudiant_id: int
    etudiant: str
    note: float

    class Config:
        from_attributes = True

class NoteDevoirCreate(BaseModel):
    devoir_id: int
    etudiant_id: int
    note: float



class NoteExamenOut(BaseModel):
    id: int
    examen_id: int
    examen: str
    etudiant_id: int
    etudiant: str
    note: float

    class Config:
        from_attributes = True

class NoteExamenCreate(BaseModel):
    examen_id: int
    etudiant_id: int
    note: float
