from django.contrib import admin
from django.utils.html import format_html


class SuiviAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'


def badge(obj):
    couleurs = {'publiee': '#315caa', 'attribuee': '#6941a5', 'en_cours': '#9a5200', 'livree': '#237443', 'annulee': '#595959', 'proposee': '#9a5200', 'acceptee': '#237443', 'refusee': '#b02d35', 'retiree': '#595959'}
    return format_html('<span style="color:white;background:{};padding:3px 8px;border-radius:4px;white-space:nowrap">{}</span>', couleurs.get(obj.statut, '#595959'), obj.get_statut_display())
