from django.urls import path
from ninja import NinjaAPI
from ninja_jwt.authentication import JWTAuth
from views.etudiants import etudiant_router
from views.scolarite import scolarite_route
from views.examen import examen_route
from .views import hello_world
from views.inscription import inscription_route

api = NinjaAPI(
    # auth=JWTAuth(), 
    version="1.0.2",
    title="API",
    description="API for managing students and teachers",
    csrf=False,
    docs_url="/docs",
    openapi_url="/openapi.json",
)


api.add_router("/inscription/", inscription_route, tags=["Les inscriptions (Pré-inscription et Dossier étudiant)"])

api.add_router("/examen/", examen_route, tags=["Les examens (Devoirs et Examens)"])
api.add_router("/matiere/", scolarite_route, tags=["Les matieres (Matieres et coefficients)"])
api.add_router("/etudiants/", etudiant_router, tags=["Gestion des étudiants"])

urlpatterns = [
    path("", api.urls, name='api'),
    path("toto/", hello_world, name='api'),
]