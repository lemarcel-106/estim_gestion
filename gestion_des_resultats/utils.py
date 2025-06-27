from django.conf import settings
from django.contrib.staticfiles import finders
import os

def link_callback(uri, rel):
    """
    Convertit les URI HTML (static, media) en chemins absolus pour xhtml2pdf.
    """
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = finders.find(uri.replace(settings.STATIC_URL, ""))
    else:
        return uri  # URI absolue (ex. http://), laisser tel quel

    if not os.path.isfile(path):
        raise Exception(f"Fichier introuvable : {path}")
    return path
