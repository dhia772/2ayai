from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
def validate_email(email):
    if not email:
        raise ValidationError('L\'adresse e-mail est requise.')
    if not email.endswith('@gmail.com'):
        raise ValidationError('L\'adresse e-mail doit se terminer par @gmail.com.')

class Utilisateur(AbstractUser):
    user_id=models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True, validators=[validate_email])
    telephone = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=[('admin', 'Admin'), ('c', 'Chargeur'), ('t', 'Transporteur')], default='c')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   



class EntrepriseA(models.Model):
    raison_sociale = models.CharField(max_length=200, blank=False, null=False)
    matricule_fiscale = models.CharField(max_length=17, unique=True)
    adresse = models.TextField(validators=[MinLengthValidator(10,"L'adresse doit contenir au moins 10 caractères."),MaxLengthValidator(200,"L'adresse ne doit pas dépasser 200 caractères.")])
    type_entreprise = models.CharField(max_length=100, 
    choices = [
        ('c', 'Chargeur'),
        ('t', 'Transporteur'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    gerant= models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='entreprise', null=True, blank=True)





# Create your models here.
