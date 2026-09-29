from django.db import models


class Vehicule(models.Model):
    TYPE_CHOICES = [
        ("camionnette", "Camionnette"),
        ("fourgon", "Fourgon"),
        ("camion_porteur", "Camion porteur"),
        ("semi_remorque", "Semi-remorque"),
    ]

    immatriculation = models.CharField(max_length=30, unique=True)
    type_vehicule = models.CharField(max_length=20, choices=TYPE_CHOICES)
    capacite_kg = models.PositiveIntegerField()
    disponible = models.BooleanField(default=True)
    entreprise = models.ForeignKey(
        "entrepriseA.EntrepriseA",
        on_delete=models.CASCADE,
        related_name="vehicules",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.immatriculation
