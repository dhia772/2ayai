from uuid import uuid4
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email  # Historical migration import.
from django.db import models
from config.model_utils import Horodatage


def generer_user_id():
    return uuid4().hex[:8].upper()


class UtilisateurManager(UserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('role', 'chargeur')
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields['role'] = 'admin'
        return super().create_superuser(username, email, password, **extra_fields)

    def create_chargeur(self, username, email, password=None, **extra_fields):
        return self.create_user(username, email, password, role='chargeur', **extra_fields)

    def create_transporteur(self, username, email, password=None, **extra_fields):
        return self.create_user(username, email, password, role='transporteur', **extra_fields)


class Utilisateur(AbstractUser):
    class Role(models.TextChoices):
        CHARGEUR = 'chargeur', 'Chargeur'
        TRANSPORTEUR = 'transporteur', 'Transporteur'
        ADMIN = 'admin', 'Administrateur'

    user_id = models.CharField(primary_key=True, max_length=8, default=generer_user_id, editable=False)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CHARGEUR)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UtilisateurManager()

    def clean(self):
        super().clean()
        if self.pk and EntrepriseA.objects.filter(utilisateur_id=self.pk).exclude(type_entreprise=self.role).exists():
            raise ValidationError({'role': 'Le rôle doit correspondre à votre entreprise.'})

    def __str__(self):
        return self.get_full_name() or self.username


class EntrepriseA(Horodatage):
    class Type(models.TextChoices):
        CHARGEUR = 'chargeur', 'Chargeur'
        TRANSPORTEUR = 'transporteur', 'Transporteur'

    raison_sociale = models.CharField(max_length=200)
    matricule_fiscal = models.CharField(max_length=17, unique=True)
    type_entreprise = models.CharField(max_length=20, choices=Type.choices)
    adresse = models.TextField()
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.PROTECT, related_name='entreprise')

    class Meta:
        verbose_name = 'entreprise'
        verbose_name_plural = 'entreprises'
        ordering = ['raison_sociale']

    def clean(self):
        super().clean()
        if self.utilisateur_id and self.utilisateur.role != self.type_entreprise:
            raise ValidationError({'utilisateur': "Le rôle du compte doit correspondre au type d'entreprise."})
        if self.pk:
            old = type(self).objects.filter(pk=self.pk).values_list('type_entreprise', flat=True).first()
            if old and old != self.type_entreprise and (self.vehicules.exists() or self.expeditions.exists() or self.offres.exists()):
                raise ValidationError({'type_entreprise': "Une entreprise utilisée ne peut pas changer de type."})

    def __str__(self):
        return self.raison_sociale


Entreprise = EntrepriseA
