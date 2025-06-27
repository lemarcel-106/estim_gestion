from django.db import models
from parametre.models import SemestreExamen
from parametre.models import Matiere
from django.core.exceptions import ValidationError


class Devoir(models.Model):
    session = models.ForeignKey(SemestreExamen, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    actif = models.BooleanField("Créer aussi l'examen de cette matiére",default=False)
    

    class Meta:
        unique_together = ('session', 'matiere')
        verbose_name = "-> DEVOIRS"
        verbose_name_plural =  "-> DEVOIRS"

    def __str__(self):
        return f"Devoir : {self.matiere.nom} - ({self.matiere.classe.nom} )"

    def save(self, *args, **kwargs):
        if self.actif and not self.pk:
            try:
                Examen.objects.get(session=self.session, matiere=self.matiere)
            except Examen.DoesNotExist:
                # Créer l'examen associé
                examen = Examen(session=self.session, matiere=self.matiere)
                examen.save()
        super().save(*args, **kwargs)


class Examen(models.Model):
    session = models.ForeignKey(SemestreExamen, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('session', 'matiere')
        verbose_name = "-> EXAMENS"
        verbose_name_plural =  "-> EXAMENS"


    def __str__(self):
            return f"{self.matiere.classe.nom} : Examen {self.matiere.nom} - {self.session.titre} ({self.session.anneee_scolaire})"

