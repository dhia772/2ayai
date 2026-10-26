from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from config.model_utils import Horodatage


class Vehicule(Horodatage):
    TYPE_CHOICES = [('camionnette', 'Camionnette'), ('fourgon', 'Fourgon'), ('camion_porteur', 'Camion porteur'), ('semi_remorque', 'Semi-remorque')]
    immatriculation = models.CharField(max_length=30, unique=True)
    type_vehicule = models.CharField(max_length=20, choices=TYPE_CHOICES)
    capacite_kg = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    disponible = models.BooleanField(default=True)
    entreprise = models.ForeignKey('EntrepriseA.EntrepriseA', on_delete=models.PROTECT, related_name='vehicules')

    class Meta:
        ordering = ['immatriculation']
        constraints = [models.CheckConstraint(condition=models.Q(capacite_kg__gt=0), name='capacite_positive')]

    def clean(self):
        super().clean()
        if self.entreprise_id and self.entreprise.type_entreprise != 'transporteur':
            raise ValidationError({'entreprise': 'Seul un transporteur possède des véhicules.'})
        if self.pk:
            actives = self.offres.filter(statut='acceptee', expedition__statut__in=['attribuee', 'en_cours'])
            if self.disponible and actives.exists():
                raise ValidationError({'disponible': 'Ce véhicule est affecté à une expédition active.'})
            if actives.exclude(transporteur_id=self.entreprise_id).exists():
                raise ValidationError({'entreprise': 'Impossible de transférer un véhicule affecté.'})
            if actives.filter(expedition__poids_kg__gt=self.capacite_kg).exists():
                raise ValidationError({'capacite_kg': 'Capacité insuffisante pour le chargement affecté.'})

    def __str__(self):
        return self.immatriculation
