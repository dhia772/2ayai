from django.contrib import admin
from config.admin_utils import SuiviAdmin
from .models import Vehicule


@admin.register(Vehicule)
class VehiculeAdmin(SuiviAdmin):
    list_display = ('immatriculation', 'entreprise', 'type_vehicule', 'capacite_kg', 'disponible')
    list_filter = ('type_vehicule', 'disponible', 'entreprise')
    list_editable = ('disponible',)
    search_fields = ('immatriculation', 'entreprise__raison_sociale')
    autocomplete_fields = ('entreprise',)
    list_select_related = ('entreprise',)
    fieldsets = (
        ('Identification', {'fields': ('immatriculation', 'entreprise', 'type_vehicule')}),
        ('Exploitation', {'fields': ('capacite_kg', 'disponible')}),
        ('Suivi', {'fields': ('created_at', 'updated_at')}),
    )
