import datetime
from import_export.widgets import Widget

class CustomExcelDateWidget(Widget):
    """
    Convertit les nombres Excel (ex : 36545) en objets date Python.
    Excel compte les jours depuis le 30/12/1899.
    """

    def clean(self, value, row=None, *args, **kwargs):
        if value in (None, ''):
            return None
        try:
            days = float(value)
            # Correction de la base de date Excel (30/12/1899)
            base_date = datetime.date(1899, 12, 30)
            return base_date + datetime.timedelta(days=days)
        except Exception:
            # Si ce n'est pas un nombre, on tente un format texte
            try:
                return datetime.datetime.strptime(value, '%Y-%m-%d').date()
            except Exception:
                return None

    def render(self, value, obj=None):
        if value:
            return value.strftime('%Y-%m-%d')
        return ''
