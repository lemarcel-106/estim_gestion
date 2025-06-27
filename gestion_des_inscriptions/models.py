from parametre.models import Filiere as Formation, Classe, Etudiant
from django.db import models
from django.utils import timezone


def get_annee_academique():
    current_year = timezone.now().year
    return f"{current_year}-{current_year + 1}"


class EtudiantLambda(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    adresse = models.TextField()
    date_naissance = models.DateField()
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Demande d'inscription"
        verbose_name_plural = "Demandes d'inscription"
        ordering = ['nom']

    def __str__(self):
        return f"{self.prenom} {self.nom}"



class Inscription(models.Model):
    demande = models.OneToOneField(EtudiantLambda, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    annee_academique = models.CharField(max_length=9, default=get_annee_academique)
    date_validation = models.DateTimeField(auto_now_add=True)
    etudiant_cree = models.OneToOneField(Etudiant, on_delete=models.SET_NULL, null=True, blank=True, editable=False)

    class Meta:
        verbose_name = "Validation d'inscription"
        verbose_name_plural = "Validations d'inscription"

    def __str__(self):
        return f"Validation de {self.demande.prenom} {self.demande.nom} ({self.classe})"

    def valider_et_creer_etudiant(self):
        if not self.etudiant_cree:
            nom_complet = f"{self.demande.nom.upper()} {self.demande.prenom}"
            etudiant = Etudiant.objects.create(
                nom_prenom=nom_complet,
                classe=self.classe
            )
            self.etudiant_cree = etudiant
        return self.etudiant_cree

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # On sauvegarde d’abord pour avoir un ID
        if not self.etudiant_cree:
            etudiant = self.valider_et_creer_etudiant()
            super().save(update_fields=['etudiant_cree'])  # Mise à jour après création de l'étudiant



class DossierEtudiant(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=100)
    filiere_souhaitee = models.CharField(max_length=100)
    dernier_diplome = models.CharField(max_length=100)
    annee_obtention = models.PositiveIntegerField()
    dernier_etablissement = models.CharField(max_length=150)
    adresse_complete = models.TextField()
    ville = models.CharField(max_length=100)
    motivation = models.TextField()
    possede_ordinateur = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    class Meta:
        verbose_name = "DEMANDE D'INSCRIPTION | INSCRIPTION COMPLETE"
        verbose_name_plural = "DEMANDE D'INSCRIPTION | INSCRIPTION COMPLETE"


class PreInscription(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    filiere_souhaitee = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.prenom} {self.nom}"
    

    class Meta:
        verbose_name = "DEMANDE D'INSCRIPTION | PRE-INSCRIPTION"
        verbose_name_plural = "DEMANDE D'INSCRIPTION | PRE-INSCRIPTION"

