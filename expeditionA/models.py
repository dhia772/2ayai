from uuid import uuid4
from django.db import models


def generer_reference():
    return f"EXP-{uuid4().hex[:12].upper()}"


class Expedition(models.Model):
    STATUT_CHOICES = [
        ("publiee", "Publiée"),
        ("attribuee", "Attribuée"),
        ("en_cours", "En cours"),
        ("livree", "Livrée"),
        ("annulee", "Annulée"),
    ]

    reference = models.CharField(
        max_length=16, unique=True, default=generer_reference, editable=False
    )
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    poids_kg = models.DecimalField(max_digits=10, decimal_places=2)
    date_souhaitee = models.DateField()
    description = models.TextField()
    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default="publiee"
    )
    entreprise = models.ForeignKey(
        "entrepriseA.EntrepriseA",
        on_delete=models.CASCADE,
        related_name="expeditions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.reference
