from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from entrepriseA.models import Utilisateur, EntrepriseA
from expeditionA.models import Expedition
from offreA.models import Offre
from vehiculeA.models import Vehicule


class Command(BaseCommand):
    help = 'Crée un jeu de démonstration reproductible, sans effacer les données existantes.'

    def add_arguments(self, parser):
        parser.add_argument('--with-anomalies', action='store_true', help='Reproduit volontairement le piège update() du workshop.')

    @transaction.atomic
    def handle(self, *args, **options):
        entreprises = []
        for username, role, nom in [
            ('demo_chargeur', 'chargeur', 'Dhia Distribution'),
            ('demo_nord', 'transporteur', 'Transport Nord'),
            ('demo_sud', 'transporteur', 'Transport Sud'),
            ('demo_sans_flotte', 'transporteur', 'Transport en inscription'),
        ]:
            user, _ = Utilisateur.objects.get_or_create(username=username, defaults={'email': username+'@example.com', 'role': role})
            if not user.password:
                user.set_unusable_password()
                user.save()
            entreprise, _ = EntrepriseA.objects.get_or_create(matricule_fiscal=username[:17], defaults={'raison_sociale': nom, 'type_entreprise': role, 'adresse': 'Avenue de la République, Tunis', 'utilisateur': user})
            entreprises.append(entreprise)
        chargeur, nord, sud, _ = entreprises
        vehicules = []
        for plaque, entreprise in [('DEMO-001', nord), ('DEMO-002', sud), ('DEMO-003', nord)]:
            vehicule, _ = Vehicule.objects.get_or_create(immatriculation=plaque, defaults={'entreprise': entreprise, 'type_vehicule': 'camion_porteur', 'capacite_kg': 5000})
            vehicules.append(vehicule)
        expeditions = []
        for index, ville in enumerate(['Sfax', 'Sousse', 'Bizerte'], 1):
            expedition, created = Expedition.objects.get_or_create(reference=f'EXP-26-{index:05d}', defaults={'entreprise': chargeur, 'ville_depart': 'Tunis', 'ville_arrivee': ville, 'poids_kg': 1200, 'date_souhaitee': timezone.localdate()+timedelta(days=2), 'description': 'Démonstration workshop TransConnect'})
            expeditions.append(expedition)
            if index == 3 and created:
                # Fixture temporelle uniquement, pas une transition métier.
                Expedition.objects.filter(pk=expedition.pk).update(created_at=timezone.now()-timedelta(days=9))
        for expedition, flotte in [(expeditions[0], vehicules[:2]), (expeditions[1], [vehicules[2], vehicules[1]])]:
            for vehicule in flotte:
                if not Offre.objects.filter(expedition=expedition, transporteur=vehicule.entreprise).exists():
                    if expedition.statut != 'publiee':
                        raise CommandError('Une expédition de démo a déjà changé; aucune offre ajoutée.')
                    Offre.objects.create(expedition=expedition, transporteur=vehicule.entreprise, vehicule=vehicule, prix=450, delai_jours=2)
        if options['with_anomalies']:
            # SEUL contournement intentionnel : reproduire la section VII sur la démo.
            cible = Offre.objects.get(expedition=expeditions[0], transporteur=nord)
            if cible.statut == 'proposee':
                Offre.objects.filter(pk=cible.pk).update(statut='acceptee')
            correcte = Offre.objects.get(expedition=expeditions[1], transporteur=nord)
            if correcte.statut == 'proposee':
                correcte.statut = 'acceptee'
                correcte.full_clean()
                correcte.save()
        self.stdout.write(self.style.SUCCESS('Démo prête : EXP-26-00001, EXP-26-00002 et EXP-26-00003.'))
        self.stdout.write('Comptes métier sans mot de passe utilisable; créez votre administrateur avec createsuperuser.')
