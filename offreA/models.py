from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from config.model_utils import Horodatage


class Offre(Horodatage):
    STATUT_CHOICES = [('proposee', 'Proposée'), ('acceptee', 'Acceptée'), ('refusee', 'Refusée'), ('retiree', 'Retirée')]
    prix = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    delai_jours = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='proposee')
    date_proposition = models.DateField(auto_now_add=True)
    expedition = models.ForeignKey('ExpeditionA.Expedition', on_delete=models.PROTECT, related_name='offres')
    transporteur = models.ForeignKey('EntrepriseA.EntrepriseA', on_delete=models.PROTECT, related_name='offres')
    vehicule = models.ForeignKey('VehiculeA.Vehicule', on_delete=models.PROTECT, related_name='offres')

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(condition=models.Q(prix__gt=0), name='prix_positif'),
            models.CheckConstraint(condition=models.Q(delai_jours__gt=0), name='delai_positif'),
            models.UniqueConstraint(fields=['expedition', 'transporteur'], condition=models.Q(statut='proposee'), name='une_proposition_par_transporteur'),
            models.UniqueConstraint(fields=['expedition'], condition=models.Q(statut='acceptee'), name='une_offre_acceptee_par_expedition'),
        ]

    def clean(self):
        super().clean()
        old = type(self).objects.filter(pk=self.pk).first() if self.pk else None
        if old and old.statut == 'acceptee':
            if any(getattr(old, f) != getattr(self, f) for f in ('prix', 'delai_jours', 'expedition_id', 'transporteur_id', 'vehicule_id')):
                raise ValidationError('Les conditions et relations d’une offre acceptée sont figées.')
            if self.statut != 'acceptee' and not (self.statut == 'refusee' and self.expedition.statut == 'annulee'):
                raise ValidationError({'statut': 'Une offre acceptée ne peut être retirée.'})
        if old and old.statut in {'refusee', 'retiree'} and old.statut != self.statut:
            raise ValidationError({'statut': 'Une offre terminée ne peut pas être réactivée.'})
        if self.transporteur_id and self.transporteur.type_entreprise != 'transporteur':
            raise ValidationError({'transporteur': 'Choisissez une entreprise transporteur.'})
        if self.vehicule_id:
            if self.vehicule.entreprise_id != self.transporteur_id:
                raise ValidationError({'vehicule': 'Le véhicule doit appartenir au transporteur.'})
            if self.expedition_id and self.vehicule.capacite_kg < self.expedition.poids_kg:
                raise ValidationError({'vehicule': 'Capacité insuffisante.'})
        if self.statut in {'proposee', 'acceptee'} and not (old and old.statut == 'acceptee'):
            if self.expedition_id and self.expedition.statut != 'publiee':
                raise ValidationError({'expedition': 'L’expédition doit être publiée.'})
            if self.vehicule_id and not self.vehicule.disponible:
                raise ValidationError({'vehicule': 'Ce véhicule est indisponible.'})
        if self.statut == 'proposee' and type(self).objects.filter(expedition_id=self.expedition_id, transporteur_id=self.transporteur_id, statut='proposee').exclude(pk=self.pk).exists():
            raise ValidationError('Une seule proposition active par transporteur et expédition.')

    @transaction.atomic
    def save(self, *args, **kwargs):
        from expeditionA.models import Expedition
        from vehiculeA.models import Vehicule
        # Refresh cached relations inside the transaction before validating acceptance.
        if self.expedition_id:
            self.expedition = Expedition.objects.select_for_update().get(pk=self.expedition_id)
        if self.vehicule_id:
            self.vehicule = Vehicule.objects.select_for_update().get(pk=self.vehicule_id)
        old_status = type(self).objects.filter(pk=self.pk).values_list('statut', flat=True).first() if self.pk else None
        result = super().save(*args, **kwargs)
        if self.statut == 'acceptee' and old_status != 'acceptee':
            for autre in type(self).objects.filter(expedition_id=self.expedition_id, statut='proposee').exclude(pk=self.pk):
                autre.statut = 'refusee'
                autre.save()
            self.expedition.statut = 'attribuee'
            self.expedition.save()
            self.vehicule.disponible = False
            self.vehicule.save()
        return result

    def __str__(self):
        return f'{self.expedition.reference} - {self.transporteur} ({self.prix})'
