from django.db import models
from parametre.models import Etudiant

# soit un modele pour la gestion des finances (frais de scolarité des étudiants par mois )
# soit un tuple a utiliser pour les champs choices contenant la liste des mois


class FraisScolarite(models.Model):

    MOIS_CHOICES = [
        ('Janvier', 'Janvier'),
        ('Février', 'Février'),
        ('Mars', 'Mars'),
        ('Avril', 'Avril'),
        ('Mai', 'Mai'),
        ('Juin', 'Juin'),
        ('Juillet', 'Juillet'),
        ('Octobre', 'Octobre'),
        ('Novembre', 'Novembre'),
        ('Décembre', 'Décembre'),
    ]
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='frais_scolarite')
    mois = models.CharField(max_length=20, choices=MOIS_CHOICES)  # Ex: 'Janvier', 'Février', etc.
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateField(auto_now=True)
    is_complet = models.BooleanField("Paiement total ? ", default=False)  # Indique si le paiement est complet ou non


    class Meta:
        unique_together = ('etudiant', 'mois')

    def __str__(self):
        return f"{self.etudiant.nom_prenom} - {self.mois} - {self.montant} FCFA"
    def is_paye(self):
        return self.date_paiement is not None
    def montant_paye(self):
        return self.montant if self.is_paye() else 0
    def montant_restant(self):
        return 0 if self.is_paye() else self.montant
    def mois_annee(self):
        return f"{self.mois} {self.annee}"
    def mois_annee_paye(self):
        return f"{self.mois} {self.annee} - Payé" if self.is_paye() else f"{self.mois} {self.annee} - Non payé"
    def mois_annee_restant(self):
        return f"{self.mois} {self.annee} - Restant: {self.montant_restant()} FCFA" if not self.is_paye() else f"{self.mois} {self.annee} - Payé"
    def mois_annee_montant(self):
        return f"{self.mois} {self.annee} - {self.montant} FCFA"
    def mois_annee_montant_paye(self):
        return f"{self.mois} {self.annee} - {self.montant_paye()} FCFA" if self.is_paye() else f"{self.mois} {self.annee} - Non payé"
