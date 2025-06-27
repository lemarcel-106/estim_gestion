from django.contrib import admin
from .models import Etudiant, Filiere , Classe, Matiere, SemestreExamen
# from unfold.admin import ModelAdmin
from examen_devoir.models import Devoir
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm

#####################################################################
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.utils.html import format_html
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateWidget
from .xls import CustomExcelDateWidget  # adapte le chemin si besoin
from gestion_des_resultats.views import attestation_inscription, attestation_frequentation
from django.shortcuts import redirect

# class EtudiantResourceResultat(resources.ModelResource):
#     class Meta:
#         model = EtudiantResultat
#         fields = ('nom_prenom', 'classe_etudiant', 'moyenne_generale')
#         export_order = ('nom_prenom', 'classe_etudiant', 'matricule', 'moyenne_generale')
#         import_order = ('nom_prenom', 'classe_etudiant', 'moyenne_generale')
#         import_id_fields = ('nom_prenom',)  # <- Ce champ sert à identifier l’étudiant à mettre à jour # Pas de champ ID attendu
#         exclude = ('matricule', 'id', 'actif', 'photo')  # optionnel, si ces champs ne sont pas dans fields






class EtudiantResource(resources.ModelResource):
    classe = fields.Field(
        column_name='classe',
        attribute='classe',
        widget=ForeignKeyWidget(Classe, 'nom')  # Utilise le nom de la classe comme clé d'import
    )

    # date_naissance = fields.Field(
    #     column_name='date_naissance',
    #     attribute='date_naissance',
    #     # widget=CustomExcelDateWidget  # Utilise DateWidget pour les dates
    # )

    lieu_naissance = fields.Field(
        column_name='lieu_naissance',
        attribute='lieu_naissance',
        default='Non renseigné'
    )

    class Meta:
        model = Etudiant
        fields = ('nom_prenom', 'classe', 'date_naissance', 'lieu_naissance')
        import_id_fields = ('nom_prenom', 'classe')  # Pour mise à jour des lignes existantes
        skip_unchanged = True
        report_skipped = True


################################################################

@admin.register(Etudiant)
class EtudiantAdmin(ModelAdmin, ImportExportModelAdmin):
    resource_class = EtudiantResource
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('photo_etudiant', 'nom_prenom', 'classe', 'date_naissance', 'lieu_naissance', 'matricule', 'actif')
    list_filter = ('classe__nom', 'classe__filiere', 'classe__niveau', 'actif')
    list_editable = ('actif',)
    list_per_page = 10
    ordering = ('nom_prenom',)
    list_display_links = ('nom_prenom','photo_etudiant')
    search_fields = ('nom_prenom', 'classe__nom', 'classe__filiere__nom')
    autocomplete_fields = ['classe']
    actions = ['attestation_inscription', 'attestation_frequentation']




    @admin.action(description="🖨️ Imprimer l'attestation d'inscription (PDF)")
    def attestation_inscription(self, request, queryset):
        if queryset.count() == 1:
            resultat = queryset.first()
            return attestation_inscription(request, resultat)
        else:
            self.message_user(request, "Veuillez sélectionner un seul étudiant à la fois.", level="warning")
            return redirect(request.get_full_path())

    @admin.action(description="🖨️ Imprimer l'attestation d'inscription (PDF)")
    def attestation_frequentation(self, request, queryset):
        if queryset.count() == 1:
            resultat = queryset.first()
            return attestation_frequentation(request, resultat)
        else:
            self.message_user(request, "Veuillez sélectionner un seul étudiant à la fois.", level="warning")
            return redirect(request.get_full_path())



    def photo_etudiant(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.photo.url)
        return "-"
    
    photo_etudiant.short_description = "Photo de l'étudiant"
    attestation_inscription.short_description = "Imprimer l'attestation d'inscription (PDF)"
    attestation_frequentation.short_description = "Imprimer l'attestation de fréquentation (PDF)"


    # def get_search_results(self, request, queryset, search_term):
    #     devoir_id = request.GET.get('devoir')  # transmis automatiquement par forward

    #     if devoir_id:
    #         try:
    #             devoir = Devoir.objects.get(id=devoir_id)
    #             queryset = queryset.filter(classe=devoir.matiere.classe)
    #         except Devoir.DoesNotExist:
    #             queryset = queryset.none()

    #     return super().get_search_results(request, queryset, search_term)



@admin.register(Classe)
class ClasseAdmin(ModelAdmin):
    list_display = ('nom', 'filiere', 'niveau')
    list_filter = ('filiere__nom', 'niveau')
    search_fields = ['nom']
    ordering = ('filiere__nom', 'niveau')
    list_per_page = 20
    autocomplete_fields = ['filiere']



@admin.register(Matiere)
class MatiereAdmin(ModelAdmin):
    list_display = ('nom', 'abreviation', 'classe', 'coefficient', 'date_creation')
    list_filter = ('classe__nom', 'classe__filiere__nom', 'classe__niveau')
    search_fields = ('nom', 'abreviation', 'classe__nom')
    ordering = ('classe__nom', 'nom')
    list_per_page = 20
    readonly_fields = ('date_creation',)
    autocomplete_fields = ['classe']




@admin.register(Filiere)
class FiliereAdmin(ModelAdmin):
    search_fields = ['nom']


@admin.register(SemestreExamen)
class SemestreExamenAdmin(ModelAdmin):
    list_display = ('titre', 'anneee_scolaire', 'code_session')
    list_display_links = ('titre','code_session')
