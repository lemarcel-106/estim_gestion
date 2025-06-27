from dal import autocomplete
from parametre.models import Etudiant
from examen_devoir.models import Devoir

class EtudiantAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Sécurité
        if not self.request.user.is_authenticated:
            return Etudiant.objects.none()

        qs = Etudiant.objects.all()

        devoir_id = self.forwarded.get('devoir', None)
        print("Devoir ID:", devoir_id)

        
        if devoir_id:
            try:
                devoir = Devoir.objects.get(id=devoir_id)
                classe = devoir.matiere.classe
                qs = qs.filter(classe=classe)
            except Devoir.DoesNotExist:
                qs = Etudiant.objects.none()
        else:
            qs = Etudiant.objects.none()

        return qs
