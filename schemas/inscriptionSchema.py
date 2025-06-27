from ninja import Schema
from datetime import date


class DossierEtudiantSchemaIn(Schema):
    nom: str
    prenom: str
    email: str
    telephone: str
    date_naissance: date
    lieu_naissance: str
    filiere_souhaitee: str
    dernier_diplome: str
    annee_obtention: int
    dernier_etablissement: str
    adresse_complete: str
    ville: str
    motivation: str
    possede_ordinateur: bool

    class Config:
        from_attributes = True



class DossierEtudiantSchemaOut(DossierEtudiantSchemaIn):
    id: int

    class Config:
        from_attributes = True


class PreInscriptionSchemaIn(Schema):
    nom: str
    prenom: str
    email: str
    telephone: str
    filiere_souhaitee: str

    class Config:
        from_attributes = True


class PreInscriptionSchemaOut(PreInscriptionSchemaIn):
    id: int

    class Config:
        from_attributes = True