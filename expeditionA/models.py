from decimal import Decimal
from uuid import uuid4
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone
from config.model_utils import Horodatage


def generer_reference():
    return f'EXP-{timezone.localdate():%y}-{uuid4().hex[:8].upper()}'


class Expedition(Horodatage):
    STATUT_CHOICES = [('publiee', 'Publiée'), ('attribuee', 'Attribuée'), ('en_cours', 'En cours'), ('livree', 'Livrée'), ('annulee', 'Annulée')]
    reference = models.CharField(max_length=16, unique=True, default=generer_reference, editable=False)
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    poids_kg = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    date_souhaitee = models.DateField()
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='publiee')
    entreprise = models.ForeignKey('EntrepriseA.EntrepriseA', on_delete=models.PROTECT, related_name='expeditions')

    class Meta:
        ordering = ['-created_at']
        constraints = [models.CheckConstraint(condition=models.Q(poids_kg__gt=0), name='poids_positif')]

    def clean(self):
        super().clean()
        if self.entreprise_id and self.entreprise.type_entreprise != 'chargeur':
            raise ValidationError({'entreprise': 'Seul un chargeur publie une expédition.'})
        if self.ville_depart and self.ville_depart.casefold() == self.ville_arrivee.casefold():
            raise ValidationError({'ville_arrivee': 'Choisissez une ville différente du départ.'})
        old = type(self).objects.filter(pk=self.pk).first() if self.pk else None
        if not old and self.statut != 'publiee':
            raise ValidationError({'statut': 'Une nouvelle expédition doit être publiée.'})
        transitions = {'publiee': {'attribuee', 'annulee'}, 'attribuee': {'en_cours', 'annulee'}, 'en_cours': {'livree', 'annulee'}, 'livree': set(), 'annulee': set()}
        if old and old.statut != self.statut and self.statut not in transitions[old.statut]:
            raise ValidationError({'statut': f'Transition {old.statut} → {self.statut} interdite.'})
        if old and old.statut != 'publiee' and any(getattr(old, f) != getattr(self, f) for f in ('entreprise_id', 'poids_kg', 'ville_depart', 'ville_arrivee')):
            raise ValidationError('Le chargement attribué ne peut plus être modifié.')
        if self.statut in {'attribuee', 'en_cours', 'livree'}:
            if not self.pk or self.offres.filter(statut='acceptee').count() != 1:
                raise ValidationError({'statut': "L'attribution exige exactement une offre acceptée."})

    @transaction.atomic
    def save(self, *args, **kwargs):
        old = type(self).objects.select_for_update().filter(pk=self.pk).first() if self.pk else None
        result = super().save(*args, **kwargs)
        if old and old.statut != self.statut and self.statut in {'livree', 'annulee'}:
            for offre in self.offres.select_related('vehicule').filter(statut='acceptee'):
                if self.statut == 'annulee':
                    offre.statut = 'refusee'
                    offre.save()
                vehicule = offre.vehicule
                vehicule.disponible = True
                vehicule.save()
            if self.statut == 'annulee':
                for offre in self.offres.filter(statut='proposee'):
                    offre.statut = 'refusee'
                    offre.save()
        return result

    def __str__(self):
        return self.reference
