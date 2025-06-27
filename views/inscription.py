from ninja import Router
from gestion_des_inscriptions.models import DossierEtudiant, PreInscription
from schemas.inscriptionSchema import (
   DossierEtudiantSchemaIn,
   DossierEtudiantSchemaOut,
   PreInscriptionSchemaIn,
   PreInscriptionSchemaOut
)

inscription_route = Router()


@inscription_route.post("/dossiers/", response=DossierEtudiantSchemaOut)
def create_dossier(request, payload: DossierEtudiantSchemaIn):
    dossier = DossierEtudiant.objects.create(**payload.dict())
    return dossier

@inscription_route.post("/preinscriptions/", response=PreInscriptionSchemaOut)
def create_preinscription(request, payload: PreInscriptionSchemaIn):
    preins = PreInscription.objects.create(**payload.dict())
    return preins
