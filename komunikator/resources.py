from import_export import resources
from .models import Projekt


class ProjektResource(resources.ModelResource):
    class Meta:
        model = Projekt