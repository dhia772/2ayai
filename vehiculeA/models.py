from django.db import models
from django.core.validators import MinValueValidator

class Vehicule(models.Model):
    TYPE_CHOICES = [
        ("camionnette", "Camionnette"),
        ("fourgon", "Fourgon"),
        ("camion_porteur", "Camion porteur"),
        ("semi_remorque", "Semi-remorque"),
    ]

    immatriculation = models.CharField(max_length=30, unique=True)
    type_vehicule = models.CharField(max_length=20, choices=TYPE_CHOICES)
    capacite_kg = models.PositiveIntegerField(validators=[MinValueValidator(1, "La capacité doit être supérieure à 0.")])
    disponible = models.BooleanField(default=True)
    entreprise = models.ForeignKey(
        "EntrepriseA.EntrepriseA",
        on_delete=models.CASCADE,
        related_name="vehicules",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.immatriculation
# Create your models here.
