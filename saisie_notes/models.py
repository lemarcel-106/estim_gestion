from django.db import models
from parametre.models import  Etudiant
from examen_devoir.models import Devoir, Examen


class NoteDevoir(models.Model):
    devoir = models.ForeignKey(Devoir, on_delete=models.CASCADE)
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='notes_devoir')
    note = models.FloatField()

    class Meta:
        unique_together = ('devoir', 'etudiant')
        verbose_name = "NOTES DE DEVOIRS | SAISIE PAR MATIÈRE"
        verbose_name_plural =  "NOTES DE DEVOIRS | SAISIE PAR MATIÈRE"


    def __str__(self):
        return f"{self.etudiant.nom_prenom} - {self.devoir.matiere.nom} : {self.note}"


class NoteExamen(models.Model):
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='notes_examen')
    note = models.FloatField()

    class Meta:
        unique_together = ('examen', 'etudiant')
        verbose_name = "NOTES D’EXAMENS | SAISIE PAR MATIÈRE"
        verbose_name_plural =  "NOTES D’EXAMENS | SAISIE PAR MATIÈRE"


    def __str__(self):
        return f"{self.etudiant.nom_prenom} - {self.examen.matiere.nom} : {self.note}"
    