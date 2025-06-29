# Generated by Django 5.2 on 2025-05-23 17:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Filiere',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, unique=True)),
                ('date_creation', models.DateField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '-> FILLIÈRES',
                'verbose_name_plural': '-> FILLIÈRES',
                'ordering': ['-nom'],
            },
        ),
        migrations.CreateModel(
            name='Classe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(blank=True, editable=False, max_length=100)),
                ('niveau', models.CharField(choices=[('Licence 1', 'Licence 1'), ('Licence 2', 'Licence 2'), ('Licence 3', 'Licence 3')], max_length=100)),
                ('filiere', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='parametre.filiere')),
            ],
            options={
                'verbose_name': '-> CLASSES',
                'verbose_name_plural': '-> CLASSES',
                'ordering': ['-nom'],
            },
        ),
        migrations.CreateModel(
            name='SemestreExamen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(choices=[('Semestre 1', 'Semestre 1'), ('Semestre 2', 'Semestre 2'), ('Rattrapage', 'Rattrapage')], max_length=100)),
                ('anneee_scolaire', models.CharField(max_length=10)),
                ('date_debut', models.DateField(auto_now_add=True)),
                ('code_session', models.CharField(blank=True, editable=False, max_length=20, unique=True)),
            ],
            options={
                'verbose_name': '-> DEFINIR UN SEMESTRE',
                'verbose_name_plural': '-> SEMESTRES (Créer un semestre académique)',
                'ordering': ['-date_debut'],
                'unique_together': {('titre', 'anneee_scolaire')},
            },
        ),
        migrations.CreateModel(
            name='Etudiant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_prenom', models.CharField(max_length=100)),
                ('date_naissance', models.DateField(blank=True, null=True)),
                ('lieu_naissance', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('matricule', models.CharField(blank=True, editable=False, max_length=20, unique=True)),
                ('photo', models.ImageField(blank=True, default='photos/default.png', null=True, upload_to='photos/')),
                ('actif', models.BooleanField(default=True)),
                ('annee_scolaire', models.CharField(default='2024-2025', max_length=20)),
                ('classe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='etudiants', to='parametre.classe')),
            ],
            options={
                'verbose_name': '-> ETUDIANTS',
                'verbose_name_plural': '-> ETUDIANTS',
                'ordering': ['nom_prenom'],
                'unique_together': {('nom_prenom', 'classe')},
            },
        ),
        migrations.CreateModel(
            name='Matiere',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('abreviation', models.CharField(max_length=10)),
                ('coefficient', models.IntegerField(default=1)),
                ('date_creation', models.DateField(auto_now=True)),
                ('classe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matieres', to='parametre.classe')),
            ],
            options={
                'verbose_name': '-> MATIÈRES',
                'verbose_name_plural': '-> MATIÈRES',
                'ordering': ['-nom'],
                'unique_together': {('nom', 'classe')},
            },
        ),
    ]
