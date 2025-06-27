from django.contrib.auth.models import User
from django.apps import apps
from unfold.contrib.filters import Card, Grid

def get_cards(request):
    # Statistiques
    user_count = User.objects.count()
    article_model = apps.get_model('blog', 'Article')  # adapter selon ton app
    article_count = article_model.objects.count()

    return Grid(children=[
        Card(title="Utilisateurs", value=user_count, icon="users"),
        # Card(title="Articles", value=article_count, icon="file-text"),
    ])
