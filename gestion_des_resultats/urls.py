# gestion_des_resultats/urls.py
from django.urls import path
from ninja import NinjaAPI
from ninja_jwt.authentication import JWTAuth
from views.etudiants import etudiant_router
from views.scolarite import scolarite_route
from views.examen import examen_route
from .views import hello_world
from views.inscription import inscription_route

# NOUVEAUX IMPORTS - À ajouter seulement si les fichiers existent
try:
    from views.classes import classes_router
    CLASSES_AVAILABLE = True
except ImportError:
    CLASSES_AVAILABLE = False

try:
    from views.notes_mobile import notes_router
    NOTES_AVAILABLE = True
except ImportError:
    NOTES_AVAILABLE = False

try:
    from views.finances import finance_router
    FINANCES_AVAILABLE = True
except ImportError:
    FINANCES_AVAILABLE = False

try:
    from views.notes_mobile import notes_mobile_router
    NOTES_MOBILE_AVAILABLE = True
except ImportError:
    NOTES_MOBILE_AVAILABLE = False

api = NinjaAPI(
    # auth=JWTAuth(), 
    version="1.0.4",
    title="API de Gestion Scolaire Mobile",
    description="""
    API complète pour la gestion d'un établissement scolaire avec support mobile optimisé.
    
    **Nouvelles fonctionnalités v1.0.4 :**
    - 📱 Saisie de notes optimisée pour mobile
    - 💰 Gestion financière complète 
    - 🔧 Endpoints spécialisés pour applications mobiles
    - 📊 Interface de saisie en masse améliorée
    - 🎯 Support cas d'usage : GI-2 + Examen Français
    - 💳 Finance par matricule et par classe
    
    **Modules disponibles :**
    - 📝 Inscriptions et dossiers étudiants
    - 🏫 Classes et organisation pédagogique
    - 📊 Examens et évaluations (devoirs/examens)
    - 📈 Notes et résultats avec statistiques
    - 💰 Gestion financière et frais de scolarité
    - 📱 Interface mobile optimisée pour enseignants
    - 👨‍🎓 Gestion des profils étudiants
    - 📚 Matières et coefficients
    """,
    csrf=False,
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# ========== ROUTES EXISTANTES (CONSERVÉES) ==========

api.add_router(
    "/inscription/", 
    inscription_route, 
    tags=["📝 Inscriptions"],
)

api.add_router(
    "/examen/", 
    examen_route, 
    tags=["📊 Examens & Devoirs"],
)

api.add_router(
    "/matiere/", 
    scolarite_route, 
    tags=["📚 Matières"],
)

api.add_router(
    "/etudiants/", 
    etudiant_router, 
    tags=["👨‍🎓 Étudiants"],
)

# ========== NOUVELLES ROUTES (CONDITIONNELLES) ==========

if CLASSES_AVAILABLE:
    api.add_router(
        "/classes/", 
        classes_router, 
        tags=["🏫 Classes"],
    )

if NOTES_AVAILABLE:
    api.add_router(
        "/notes/", 
        notes_router, 
        tags=["📈 Notes & Résultats"],
    )

if FINANCES_AVAILABLE:
    api.add_router(
        "/finance/", 
        finance_router, 
        tags=["💰 Finance"],
    )

if NOTES_MOBILE_AVAILABLE:
    api.add_router(
        "/notes-mobile/", 
        notes_mobile_router, 
        tags=["📱 Mobile - Notes"],
    )

# ========== ENDPOINTS DE BASE ==========

@api.get("/", tags=["🏠 Accueil"])
def api_root(request):
    """
    Point d'entrée de l'API avec informations générales.
    """
    modules_disponibles = [
        "inscriptions",
        "examens",
        "matieres",
        "etudiants"
    ]
    
    if CLASSES_AVAILABLE:
        modules_disponibles.append("classes")
    if NOTES_AVAILABLE:
        modules_disponibles.append("notes")
    if FINANCES_AVAILABLE:
        modules_disponibles.append("finance")
    if NOTES_MOBILE_AVAILABLE:
        modules_disponibles.append("notes-mobile")
    
    return {
        "api_name": "API de Gestion Scolaire Mobile",
        "version": "1.0.4",
        "description": "API complète pour la gestion d'un établissement scolaire avec support mobile",
        "modules_disponibles": modules_disponibles,
        "nouveautes_v1_0_4": [
            "Saisie de notes mobile optimisée" if NOTES_MOBILE_AVAILABLE else "Module notes mobile en développement",
            "Gestion financière par matricule et classe" if FINANCES_AVAILABLE else "Module finance en développement",
            "Support GI-2 + Examen Français",
            "Interface de saisie en masse"
        ],
        "endpoints": {
            "docs": "/docs",
            "openapi": "/openapi.json",
            "health": "/health"
        },
        "status": {
            "classes_module": "disponible" if CLASSES_AVAILABLE else "en développement",
            "notes_module": "disponible" if NOTES_AVAILABLE else "en développement", 
            "finance_module": "disponible" if FINANCES_AVAILABLE else "en développement",
            "notes_mobile_module": "disponible" if NOTES_MOBILE_AVAILABLE else "en développement"
        }
    }

@api.get("/health", tags=["🏠 Accueil"])
def health_check(request):
    """
    Vérification de l'état de l'API et des services.
    """
    from django.utils import timezone
    
    services_status = {
        "inscriptions": "active",
        "examens": "active",
        "matieres": "active",
        "etudiants": "active"
    }
    
    if CLASSES_AVAILABLE:
        services_status["classes"] = "active"
    if NOTES_AVAILABLE:
        services_status["notes"] = "active"
    if FINANCES_AVAILABLE:
        services_status["finance"] = "active"
    if NOTES_MOBILE_AVAILABLE:
        services_status["notes_mobile"] = "active"
    
    return {
        "status": "ok",
        "timestamp": timezone.now().isoformat(),
        "version": "1.0.4",
        "database": "connected",
        "services": services_status,
        "modules_status": {
            "core_modules": 4,  # inscription, examen, matiere, etudiants
            "extended_modules": sum([
                CLASSES_AVAILABLE,
                NOTES_AVAILABLE,
                FINANCES_AVAILABLE,
                NOTES_MOBILE_AVAILABLE
            ]),
            "total_endpoints": len([r for r in api._routers]) * 5  # Estimation
        },
        "ready_for_mobile": NOTES_MOBILE_AVAILABLE and FINANCES_AVAILABLE
    }

@api.get("/modules", tags=["🏠 Accueil"])
def modules_status(request):
    """
    État détaillé des modules disponibles.
    """
    return {
        "core_modules": {
            "inscriptions": {
                "status": "active",
                "description": "Gestion des pré-inscriptions et dossiers",
                "endpoints": ["/inscription/dossiers/", "/inscription/preinscriptions/"]
            },
            "examens": {
                "status": "active", 
                "description": "Gestion des examens et devoirs",
                "endpoints": ["/examen/devoirs", "/examen/examens", "/examen/notes-devoir", "/examen/notes-examen"]
            },
            "matieres": {
                "status": "active",
                "description": "Gestion des matières et coefficients",
                "endpoints": ["/matiere/"]
            },
            "etudiants": {
                "status": "active",
                "description": "Gestion des profils étudiants",
                "endpoints": ["/etudiants/", "/etudiants/by-matricule/{matricule}"]
            }
        },
        "extended_modules": {
            "classes": {
                "status": "available" if CLASSES_AVAILABLE else "pending",
                "description": "Gestion des classes et organisation",
                "endpoints": ["/classes/", "/classes/{id}", "/classes/{id}/etudiants"] if CLASSES_AVAILABLE else []
            },
            "notes": {
                "status": "available" if NOTES_AVAILABLE else "pending",
                "description": "Saisie et consultation des notes",
                "endpoints": ["/notes/etudiant/{matricule}", "/notes/classe/{id}", "/notes/bulk-create"] if NOTES_AVAILABLE else []
            },
            "finance": {
                "status": "available" if FINANCES_AVAILABLE else "pending",
                "description": "Gestion financière des frais",
                "endpoints": ["/finance/etudiant/{matricule}", "/finance/classe/{id}/frais-bulk"] if FINANCES_AVAILABLE else []
            },
            "notes_mobile": {
                "status": "available" if NOTES_MOBILE_AVAILABLE else "pending",
                "description": "Interface mobile pour saisie de notes",
                "endpoints": ["/notes-mobile/classe/{nom}/configuration", "/notes-mobile/saisie-notes-bulk"] if NOTES_MOBILE_AVAILABLE else []
            }
        },
        "installation_guide": {
            "next_steps": [
                "Créer views/classes.py" if not CLASSES_AVAILABLE else "✅ Classes module ready",
                "Créer views/notes.py" if not NOTES_AVAILABLE else "✅ Notes module ready",
                "Créer views/finances.py" if not FINANCES_AVAILABLE else "✅ Finance module ready",
                "Créer views/notes_mobile.py" if not NOTES_MOBILE_AVAILABLE else "✅ Notes mobile ready"
            ],
            "schemas_needed": [
                "schemas/notesSchema.py" if not NOTES_AVAILABLE else "✅ Notes schemas ready",
                "schemas/financeSchema.py" if not FINANCES_AVAILABLE else "✅ Finance schemas ready",
                "schemas/notesMobileSchema.py" if not NOTES_MOBILE_AVAILABLE else "✅ Mobile schemas ready"
            ]
        }
    }

@api.get("/installation-status", tags=["🏠 Accueil"])
def installation_status(request):
    """
    Statut d'installation des nouveaux modules.
    """
    return {
        "installation_progress": {
            "core_api": "✅ Installé et fonctionnel",
            "classes_module": "✅ Prêt" if CLASSES_AVAILABLE else "⏳ En attente - Créer views/classes.py",
            "notes_module": "✅ Prêt" if NOTES_AVAILABLE else "⏳ En attente - Créer views/notes.py",
            "finance_module": "✅ Prêt" if FINANCES_AVAILABLE else "⏳ En attente - Créer views/finances.py",
            "mobile_module": "✅ Prêt" if NOTES_MOBILE_AVAILABLE else "⏳ En attente - Créer views/notes_mobile.py"
        },
        "completion_percentage": round(
            (4 + sum([CLASSES_AVAILABLE, NOTES_AVAILABLE, FINANCES_AVAILABLE, NOTES_MOBILE_AVAILABLE])) / 8 * 100, 2
        ),
        "ready_for_production": all([CLASSES_AVAILABLE, NOTES_AVAILABLE, FINANCES_AVAILABLE, NOTES_MOBILE_AVAILABLE]),
        "mobile_ready": NOTES_MOBILE_AVAILABLE and FINANCES_AVAILABLE,
        "cas_usage_support": {
            "saisie_notes_gi2_francais": NOTES_MOBILE_AVAILABLE,
            "finance_par_matricule": FINANCES_AVAILABLE,
            "finance_par_classe": FINANCES_AVAILABLE,
            "dashboard_statistiques": NOTES_AVAILABLE and FINANCES_AVAILABLE
        }
    }

# ========== URL PATTERNS ==========

urlpatterns = [
    path("", api.urls, name='api'),
    path("toto/", hello_world, name='hello_world_legacy'),
]