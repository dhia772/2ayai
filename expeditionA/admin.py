from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from config.admin_utils import SuiviAdmin, badge
from offreA.models import Offre
from .models import Expedition


class EnRetardFilter(admin.SimpleListFilter):
    title = 'en retard'
    parameter_name = 'en_retard'

    def lookups(self, request, model_admin):
        return [('oui', 'Oui'), ('non', 'Non')]

    def queryset(self, request, queryset):
        condition = dict(statut='publiee', date_souhaitee__lt=timezone.localdate())
        if self.value() == 'oui':
            return queryset.filter(**condition)
        if self.value() == 'non':
            return queryset.exclude(**condition)
        return queryset


class OffreInline(admin.StackedInline):
    model = Offre
    extra = 0
    fields = ('transporteur', 'vehicule', 'prix', 'delai_jours', 'statut', 'date_proposition')
    readonly_fields = fields
    show_change_link = True
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.action(description='Clôturer les expéditions sélectionnées', permissions=['change'])
def cloturer_expeditions(modeladmin, request, queryset):
    traitees = erreurs = 0
    for pk in queryset.filter(statut='en_cours').values_list('pk', flat=True):
        try:
            with transaction.atomic():
                expedition = Expedition.objects.select_for_update().get(pk=pk)
                if expedition.statut != 'en_cours':
                    continue
                expedition.statut = 'livree'
                expedition.full_clean()
                expedition.save()
                traitees += 1
        except ValidationError:
            erreurs += 1
    modeladmin.message_user(request, f'{traitees} expédition(s) clôturée(s). {erreurs} erreur(s); autres statuts ignorés.', messages.WARNING if erreurs else messages.SUCCESS)


@admin.register(Expedition)
class ExpeditionAdmin(SuiviAdmin):
    list_display = ('reference', 'entreprise', 'ville_depart', 'ville_arrivee', 'statut_colore', 'statut', 'date_souhaitee')
    list_filter = ('statut', 'ville_depart', EnRetardFilter)
    list_editable = ('statut',)
    search_fields = ('reference', 'entreprise__raison_sociale', 'ville_depart', 'ville_arrivee')
    list_select_related = ('entreprise',)
    date_hierarchy = 'date_souhaitee'
    autocomplete_fields = ('entreprise',)
    readonly_fields = SuiviAdmin.readonly_fields + ('reference', 'statut_colore')
    inlines = (OffreInline,)
    actions = (cloturer_expeditions,)
    fieldsets = (
        ('Expédition', {'fields': ('reference', 'entreprise', 'ville_depart', 'ville_arrivee')}),
        ('Chargement et planning', {'fields': ('poids_kg', 'date_souhaitee', 'description')}),
        ('Suivi', {'fields': ('statut', 'statut_colore', 'created_at', 'updated_at')}),
    )

    @admin.display(description='État', ordering='statut')
    def statut_colore(self, obj):
        return badge(obj)
