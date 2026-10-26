from datetime import timedelta
from django.db.models import Count, Q
from django.utils import timezone
from entrepriseA.models import EntrepriseA
from expeditionA.models import Expedition
from offreA.models import Offre
from vehiculeA.models import Vehicule


def integrity_checks():
    # Counts/grouping stay in SQL; only the first 50 result rows are displayed.
    definitions = [
        ('expeditions_bloquees', 'Expéditions publiées depuis plus de 7 jours', 'Suivi des publications', 'Une publication oubliée ou une cascade contournée reste publiée.',
         Expedition.objects.filter(statut='publiee', created_at__lt=timezone.now()-timedelta(days=7)).values('reference', 'created_at')),
        ('transporteurs_sans_flotte', 'Transporteurs sans flotte', 'Un transporteur doit disposer de véhicules pour proposer une offre', 'Inscription incomplète ou suppression de la dernière voiture.',
         EntrepriseA.objects.filter(type_entreprise='transporteur').annotate(nb_vehicules=Count('vehicules')).filter(nb_vehicules=0).values('raison_sociale', 'nb_vehicules')),
        ('disponibilite_incoherente', 'Véhicules disponibles mais affectés', 'Réservation du véhicule lors de l’acceptation', 'Une acceptation par update() ne réserve pas le véhicule.',
         Vehicule.objects.filter(disponible=True, offres__statut='acceptee', offres__expedition__statut__in=['publiee', 'attribuee', 'en_cours']).distinct().values('immatriculation')),
        ('doublons_proposition', 'Propositions en double', 'Une proposition active par transporteur et expédition', 'Import ancien ou base restaurée sans contrainte unique.',
         Offre.objects.filter(statut='proposee').order_by().values('expedition__reference', 'transporteur__raison_sociale').annotate(nombre=Count('pk')).filter(nombre__gt=1)),
        ('acceptation_sans_attribution', 'Offres acceptées sans attribution cohérente', 'L’acceptation attribue l’expédition', 'update(statut="acceptee") contourne save().',
         Offre.objects.filter(statut='acceptee').exclude(expedition__statut__in=['attribuee', 'en_cours', 'livree']).values('id', 'expedition__reference', 'expedition__statut')),
        ('propositions_apres_attribution', 'Propositions concurrentes non refusées', 'L’acceptation refuse les autres propositions', 'Une mise à jour SQL ne déclenche pas la cascade de refus.',
         Offre.objects.filter(statut='proposee').filter(Q(expedition__offres__statut='acceptee') | ~Q(expedition__statut='publiee')).distinct().values('id', 'expedition__reference', 'transporteur__raison_sociale')),
    ]
    return [dict(key=key, title=title, rule=rule, scenario=scenario, count=query.count(), rows=list(query[:50])) for key, title, rule, scenario, query in definitions]
