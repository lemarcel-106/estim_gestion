from django.db import models
from parametre.models import Etudiant

class Attestation(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='attestations')
    type = models.CharField(max_length=50, choices=[
        ('inscription', 'Attestation d\'inscription'),
        ('frequentation', 'Attestation de fréquentation'),
    ])
    date_creation = models.DateTimeField(auto_now_add=True, editable=False)
    date_modification = models.DateTimeField(auto_now=True, editable=False)
    valide = models.BooleanField(default=True)
    numero = models.CharField(max_length=20, unique=True, help_text="Numéro d'identification de l'attestation")

    class Meta:
        verbose_name = "Liste des attestations"
        verbose_name_plural = "Liste des attestations"
        ordering = ['-date_creation']