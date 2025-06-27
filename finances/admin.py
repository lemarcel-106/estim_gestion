from django.contrib import admin
from django.core.mail import send_mail
from .models import FraisScolarite
from unfold.admin import ModelAdmin

@admin.register(FraisScolarite)
class DevoirAdmin(ModelAdmin):
    list_display = ('etudiant', 'mois', 'montant', 'date_paiement', 'is_complet')
    search_fields = ['etudiant__nom_prenom']
    list_filter = ['mois', 'is_complet', 'etudiant__classe']
    list_editable = ('montant', 'is_complet')
    autocomplete_fields = ['etudiant']

    def send_notification(self, subject, message):
        send_mail(
            subject=subject,
            message=message,
            from_email='secretariat@estim-online.com',
            recipient_list=['ngoyi@estim-online.com'],
            fail_silently=False,
        )

    def save_model(self, request, obj, form, change):
        action = "mis à jour" if change else "ajouté"
        super().save_model(request, obj, form, change)
        self.send_notification(
            subject=f"[ESTIM-ONLINE] Paiement {action} pour {obj.etudiant}",
            message=(
                f"Un paiement a été {action}.\n\n"
                f"Étudiant : {obj.etudiant.nom_prenom}\n"
                f"Mois : {obj.mois}\n"
                f"Montant : {obj.montant}\n"
                f"Complet : {'Oui' if obj.is_complet else 'Non'}\n"
                f"Date : {obj.date_paiement}"
            )
        )

    def delete_model(self, request, obj):
        self.send_notification(
            subject=f"[ESTIM-ONLINE] Paiement supprimé pour {obj.etudiant}",
            message=(
                f"Un paiement a été supprimé.\n\n"
                f"Étudiant : {obj.etudiant}\n"
                f"Mois : {obj.mois}\n"
                f"Montant : {obj.montant}\n"
                f"Date : {obj.date_paiement}"
            )
        )
        super().delete_model(request, obj)
