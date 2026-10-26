import csv
from django.contrib import admin
from django.http import HttpResponse
from config.admin_utils import SuiviAdmin, badge
from .models import Offre


def cellule_csv(value):
    value = str(value)
    return "'" + value if value.startswith(('=', '+', '-', '@', '\t', '\r', '\n')) else value


@admin.action(description='Exporter la sélection en CSV', permissions=['view'])
def exporter_offres_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="offres.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['reference_expedition', 'transporteur', 'prix', 'statut'])
    for offre in queryset.select_related('expedition', 'transporteur'):
        writer.writerow([cellule_csv(offre.expedition.reference), cellule_csv(offre.transporteur.raison_sociale), offre.prix, offre.statut])
    return response


@admin.register(Offre)
class OffreAdmin(SuiviAdmin):
    list_display = ('id', 'expedition', 'transporteur', 'vehicule', 'prix', 'delai_jours', 'statut_colore', 'statut', 'date_proposition')
    list_filter = ('statut', 'date_proposition')
    list_editable = ('statut',)
    search_fields = ('expedition__reference', 'transporteur__raison_sociale', 'vehicule__immatriculation')
    autocomplete_fields = ('expedition', 'transporteur', 'vehicule')
    list_select_related = ('expedition', 'transporteur', 'vehicule')
    date_hierarchy = 'date_proposition'
    readonly_fields = SuiviAdmin.readonly_fields + ('date_proposition', 'statut_colore')
    actions = (exporter_offres_csv,)
    fieldsets = (
        ("Détails de l'offre", {'fields': ('expedition', 'transporteur', 'vehicule')}),
        ('Conditions', {'fields': ('prix', 'delai_jours')}),
        ('Suivi', {'fields': ('statut', 'statut_colore', 'date_proposition', 'created_at', 'updated_at')}),
    )

    def has_delete_permission(self, request, obj=None):
        # Preserve the audit trail and avoid removing an accepted assignment.
        return False

    def get_readonly_fields(self, request, obj=None):
        base = list(super().get_readonly_fields(request, obj))
        return base + ['prix', 'delai_jours', 'expedition', 'transporteur', 'vehicule'] if obj and obj.statut == 'acceptee' else base

    @admin.display(description='État', ordering='statut')
    def statut_colore(self, obj):
        return badge(obj)
