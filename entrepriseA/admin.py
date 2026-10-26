from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from config.admin_utils import SuiviAdmin
from vehiculeA.models import Vehicule
from .models import EntrepriseA, Utilisateur


class VehiculeInline(admin.TabularInline):
    model = Vehicule
    extra = 0
    fields = ('immatriculation', 'type_vehicule', 'capacite_kg', 'disponible')
    show_change_link = True


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('user_id', 'username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    list_editable = ('is_active',)
    search_fields = ('user_id', 'username', 'email', 'first_name', 'last_name')
    readonly_fields = ('user_id', 'created_at', 'updated_at', 'date_joined', 'last_login')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    fieldsets = (
        ('Compte et profil', {'fields': ('user_id', 'username', 'password', 'first_name', 'last_name', 'email', 'telephone', 'role')}),
        ('Autorisations', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Suivi', {'fields': ('created_at', 'updated_at', 'date_joined', 'last_login')}),
    )
    add_fieldsets = (('Nouveau compte', {'fields': ('username', 'email', 'telephone', 'role', 'password1', 'password2')}),)


@admin.register(EntrepriseA)
class EntrepriseAdmin(SuiviAdmin):
    list_display = ('raison_sociale', 'matricule_fiscal', 'type_entreprise', 'utilisateur', 'adresse')
    list_filter = ('type_entreprise',)
    list_editable = ('adresse',)
    search_fields = ('raison_sociale', 'matricule_fiscal', 'utilisateur__username')
    autocomplete_fields = ('utilisateur',)
    inlines = (VehiculeInline,)
    fieldsets = (
        ('Identité', {'fields': ('raison_sociale', 'matricule_fiscal', 'type_entreprise')}),
        ('Contact', {'fields': ('utilisateur', 'adresse')}),
        ('Suivi', {'fields': ('created_at', 'updated_at')}),
    )
