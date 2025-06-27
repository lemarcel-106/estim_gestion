# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models.utilisateurs import ProfilAdmin

@receiver(post_save, sender=User)
def create_user_profil(sender, instance, created, **kwargs):
    if created:
        ProfilAdmin.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profil(sender, instance, **kwargs):
    instance.profil.save()
