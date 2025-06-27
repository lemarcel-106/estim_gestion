from django.db import models
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.db.models import Q
from datetime import date

class Filiere(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    date_creation = models.DateField(auto_now_add=True)
    creer_classe = models.BooleanField(default=False, help_text="Créer automatiquement les classes pour cette filière ? (L1, L2, L3)")

    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        if not self.nom:
            raise ValidationError("Le nom de la filière ne peut pas être vide.")
        super().save(*args, **kwargs)

        # Si l'option de création automatique de classes est activée
        if self.creer_classe:
            niveaux = ['Licence 1', 'Licence 2', 'Licence 3']
            for niveau in niveaux:
                Classe.objects.get_or_create(filiere=self, niveau=niveau)

    class Meta:
        verbose_name = "-> FILLIÈRES"
        verbose_name_plural = "-> FILLIÈRES"
        ordering = ['-nom']


class Matiere(models.Model):
    nom = models.CharField(max_length=100)
    classe = models.ForeignKey('Classe', on_delete=models.CASCADE, related_name='matieres')
    abreviation = models.CharField(max_length=10)
    coefficient = models.IntegerField(default=1)
    date_creation = models.DateField(auto_now=True)


    def __str__(self):
        return f"{self.nom} ({self.abreviation}) - Classe: {self.classe.nom}"

    class Meta:
        unique_together = ('nom', 'classe')
        verbose_name = "-> MATIÈRES"
        verbose_name_plural = "-> MATIÈRES"
        ordering = ['-nom']


class Classe(models.Model):
    nom = models.CharField(max_length=100, blank=True, editable=False)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='classes')
    niveau = models.CharField(max_length=100, choices=[
        ('Licence 1', 'Licence 1'),
        ('Licence 2', 'Licence 2'),
        ('Licence 3', 'Licence 3'),])

    class Meta:
        unique_together = ('filiere', 'niveau')

    def __str__(self):
        return f"{self.nom} ({self.filiere.nom} | {self.niveau})"

    def get_etudiants(self):
        return self.etudiants.filter(actif=True)

    def save(self, *args, **kwargs):
        # Raccourci de la filière : première lettre de chaque mot
        filiere_code = ''.join([mot[0] for mot in self.filiere.nom.split()]).upper()
        # Extraction du numéro de niveau (ex : "Licence 1" -> "1")
        niveau_num = ''.join(filter(str.isdigit, self.niveau))
        self.nom = f"{filiere_code}-{niveau_num}".strip()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "-> CLASSES"
        verbose_name_plural = "-> CLASSES"
        ordering = ['-nom']

class Etudiant(models.Model):
    nom_prenom = models.CharField(max_length=100)
    classe = models.ForeignKey("Classe", on_delete=models.CASCADE, related_name='etudiants')
    date_naissance = models.DateField(null=True, blank=True)
    lieu_naissance = models.CharField(max_length=100, null=True, blank=True, default="")
    matricule = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True, default='photos/default.png')
    actif = models.BooleanField(default=True)
    annee_scolaire = models.CharField(max_length=20, default="2024-2025")

    class Meta:
        verbose_name = "-> ETUDIANTS"
        verbose_name_plural = "-> ETUDIANTS"
        unique_together = ('nom_prenom', 'classe')
        ordering = ['nom_prenom']

    def __str__(self):
        return f"{self.nom_prenom} - ({self.matricule}) - {self.classe.nom}"

    def generate_unique_matricule(self):
        from random import randint
        matricule = f"{randint(1000, 9999)}"
        while Etudiant.objects.filter(matricule=matricule).exists():
            matricule = f"{randint(1000, 9999)}"
        return matricule

    def save(self, *args, **kwargs):
        if not self.id:
            self.annee_scolaire = "2024-2025"
            self.matricule = self.generate_unique_matricule() if not self.matricule else self.matricule
        super().save(*args, **kwargs)
        

    # Méthodes pour obtenir les notes
    def get_note_examen(self, matiere, session):
        return self.notes_examen.filter(examen__matiere=matiere, examen__session=session).first()

    def get_note_devoir(self, matiere, session):
        return self.notes_devoir.filter(devoir__matiere=matiere, devoir__session=session).first()

    def moyenne_par_matiere(self, matiere, code_session):
        try:
            note_examen_obj = self.get_note_examen(matiere, code_session)
            note_devoir_obj = self.get_note_devoir(matiere, code_session)

            if not note_examen_obj or not note_devoir_obj:
                return None

            note_examen = note_examen_obj.note
            note_devoir = note_devoir_obj.note

            moyenne_brute = (note_devoir * 0.3) + (note_examen * 0.7)
            moyenne_ponderee = moyenne_brute * matiere.coefficient

            return {
                "matiere": matiere.nom,
                "note_devoir": round(note_devoir, 2),
                "note_examen": round(note_examen, 2),
                "moyenne_brute": round(moyenne_brute, 2),
                "coefficient": matiere.coefficient,
                "moyenne_ponderee": round(moyenne_ponderee, 2),
            }
        except Exception as e:
            print("Erreur dans moyenne_par_matiere:", e)
            return {
                "matiere": matiere.nom,
                "note_devoir": 0,
                "note_examen": 0,
                "moyenne_brute": 0,
                "coefficient": matiere.coefficient,
                "moyenne_ponderee": 0,
            }

    def matieres_non_valides(self, code_session):
        """
        Retourne la liste des matières où la moyenne brute est < 10.
        """
        matieres = Matiere.objects.filter(classe=self.classe)
        non_valides = []
        for matiere in matieres:
            result = self.moyenne_par_matiere(matiere, code_session)
            if result and result["moyenne_brute"] < 10:
                non_valides.append(result)
        return non_valides

    def matieres_valides(self, code_session):
        """
        Retourne les matières validées (moyenne brute >= 10).
        """
        matieres = Matiere.objects.filter(classe=self.classe)
        valides = []
        for matiere in matieres:
            result = self.moyenne_par_matiere(matiere, code_session)
            if result and result["moyenne_brute"] >= 10:
                valides.append(result)
        return valides

    def get_matieres_avec_notes(self, code_session):
        """
        Retourne les matières pour lesquelles l’étudiant a des notes pour la session donnée.
        """
        return Matiere.objects.filter(
            Q(classe=self.classe) &
            (
                Q(examen__noteexamen__examen__session=code_session) |
                Q(devoir__notedevoir__devoir__session=code_session)
            )
        ).distinct()

    def moyenne_generale(self, code_session):
        matieres = Matiere.objects.filter(classe=self.classe)
        total_ponderee = 0
        total_coef = 0
        for matiere in matieres:
            result = self.moyenne_par_matiere(matiere, code_session)
            if result:
                total_ponderee += result["moyenne_ponderee"]
                total_coef += matiere.coefficient
        if total_coef == 0:
            return None
        return round(total_ponderee / total_coef, 2)

    def generer_bulletin(self, code_session):
        matieres = Matiere.objects.filter(classe=self.classe)
        lignes = []
        total_ponderee = 0
        total_coef = 0
        for matiere in matieres:
            result = self.moyenne_par_matiere(matiere, code_session)
            if result:
                lignes.append(result)
                total_ponderee += result["moyenne_ponderee"]
                total_coef += matiere.coefficient
        moyenne_generale = round(total_ponderee / total_coef, 2) if total_coef else None
        return {
            "etudiant": self.nom_prenom,
            "classe": self.classe.nom,
            "matieres": lignes,
            "moyenne_generale": moyenne_generale,
        }



class SemestreExamen(models.Model):
    session_choices = (
        ('Semestre 1', 'Semestre 1'),
        ('Semestre 2', 'Semestre 2'),
        ('Rattrapage', 'Rattrapage'),
    )

    titre = models.CharField(max_length=100, choices=session_choices)
    anneee_scolaire = models.CharField(max_length=10)
    date_debut = models.DateField(auto_now_add=True)
    code_session = models.CharField(max_length=20, unique=True, editable=False, blank=True)

    class Meta:
        unique_together = ('titre', 'anneee_scolaire')
        ordering = ['-date_debut']
        verbose_name = "-> DEFINIR UN SEMESTRE"
        verbose_name_plural = "-> SEMESTRES (Créer un semestre académique)"



    def save(self, *args, **kwargs):
        if not self.code_session:
            prefix = self.titre.replace(" ", "").upper()[:3]  # Exemple: 'SEM' ou 'RAT'
            annee = self.anneee_scolaire.replace("-", "")
            suffix = get_random_string(length=4).upper()
            self.code_session = f"{prefix}-{annee}-{suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.titre} - ({self.anneee_scolaire})"

