from django.db import models
from parametre.models import Etudiant, Classe, SemestreExamen
from django.core.exceptions import ValidationError
from django.db import models


class ResultatAdmissionClasseSession(models.Model):
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    session = models.ForeignKey(SemestreExamen, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('classe', 'session')
        verbose_name = "Résultat d'admission par classe et session".upper()
        verbose_name_plural = "Résultats d'admission par classe et session".upper()

    def __str__(self):
        return f"{self.classe.nom} | {self.session.titre}"



class MatiereRattrapage(models.Model):
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    session = models.ForeignKey(SemestreExamen, on_delete=models.CASCADE)
    

    class Meta:
        unique_together = ('classe', 'session')
        verbose_name = "RATTRAPAGE | MATIERE RATTRAPAGE PAR CLASSE ET SESSION"
        verbose_name_plural = "RATTRAPAGE | MATIERE NON VALIDÉE PAR CLASSE ET SESSION"


class ResultatEtudiant(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    moyenne_generale = models.FloatField(editable=False, null=True, blank=True, default=0)
    mention = models.CharField(max_length=20, blank=True, null=True, editable=False)
    
    class Meta:
        unique_together = ('etudiant', 'moyenne_generale')
        ordering = ['-moyenne_generale']
        verbose_name = "LISTE DES BULLETINS | RÉSULTATS DES ÉTUDIANTS"
        verbose_name_plural =  "LISTE DES BULLETINS | RÉSULTATS DES ÉTUDIANTS"
        
    def __str__(self):
        return f"{self.etudiant.nom_prenom} : {self.moyenne_generale}"
    
    def save(self, *args, **kwargs):
        etudiant = self.etudiant
        self.moyenne_generale = etudiant.moyenne_generale(code_session=ParametreResultat.objects.all().first().session) or None
        super().save(*args, **kwargs)



class ParametreResultat(models.Model):
    session = models.OneToOneField(SemestreExamen, on_delete=models.CASCADE)

    def clean(self):
        if not self.pk and ParametreResultat.objects.exists():
            raise ValidationError("Il ne peut y avoir qu'une seule instance de ParametreResultat.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Appelle `clean()` avant de sauvegarder
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "PARAMÈTRE RÉSULTAT | SÉLECTIONNEZ UN SEMESTRE"
        verbose_name_plural = "PARAMÈTRE RÉSULTAT | SÉLECTIONNEZ UN SEMESTRE"
