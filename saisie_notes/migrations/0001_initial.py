# Generated by Django 5.2 on 2025-05-23 17:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('examen_devoir', '0001_initial'),
        ('parametre', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NoteDevoir',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.FloatField()),
                ('devoir', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='examen_devoir.devoir')),
                ('etudiant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes_devoir', to='parametre.etudiant')),
            ],
            options={
                'verbose_name': 'NOTES DE DEVOIRS | SAISIE PAR MATIÈRE',
                'verbose_name_plural': 'NOTES DE DEVOIRS | SAISIE PAR MATIÈRE',
                'unique_together': {('devoir', 'etudiant')},
            },
        ),
        migrations.CreateModel(
            name='NoteExamen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.FloatField()),
                ('etudiant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes_examen', to='parametre.etudiant')),
                ('examen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='examen_devoir.examen')),
            ],
            options={
                'verbose_name': 'NOTES D’EXAMENS | SAISIE PAR MATIÈRE',
                'verbose_name_plural': 'NOTES D’EXAMENS | SAISIE PAR MATIÈRE',
                'unique_together': {('examen', 'etudiant')},
            },
        ),
    ]
