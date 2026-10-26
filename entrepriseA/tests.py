from datetime import timedelta
from decimal import Decimal
from io import StringIO
from unittest.mock import patch

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from config.health import integrity_checks
from entrepriseA.models import EntrepriseA, Utilisateur
from expeditionA.admin import cloturer_expeditions
from expeditionA.models import Expedition
from offreA.models import Offre
from vehiculeA.models import Vehicule


class WorkshopTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_demo', stdout=StringIO())
        cls.admin = Utilisateur.objects.create_superuser('admin', 'admin@example.com', 'test-password-419')

    def setUp(self):
        self.exp = Expedition.objects.get(reference='EXP-26-00001')
        self.offre = Offre.objects.get(expedition=self.exp, vehicule__immatriculation='DEMO-001')
        self.autre = Offre.objects.get(expedition=self.exp, vehicule__immatriculation='DEMO-002')
        self.client.force_login(self.admin)

    def accepter(self):
        self.offre.statut = 'acceptee'
        self.offre.full_clean()
        self.offre.save()
        self.exp.refresh_from_db()

    def counts(self):
        return {c['key']: c['count'] for c in integrity_checks()}

    def test_user_primary_key_and_manager_roles(self):
        self.assertEqual(Utilisateur._meta.pk.name, 'user_id')
        self.assertEqual(len(self.admin.pk), 8)
        self.assertEqual(self.admin.role, 'admin')
        user = Utilisateur.objects.create_transporteur('new', 'new@esprit.tn')
        self.assertEqual(user.role, 'transporteur')
        self.assertNotEqual(user.pk, self.admin.pk)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Utilisateur.objects.create_user('duplicate', user.email)

    def test_vehicle_requires_carrier(self):
        vehicule = self.offre.vehicule
        vehicule.entreprise = self.exp.entreprise
        with self.assertRaises(ValidationError):
            vehicule.save()

    def test_shipment_requires_shipper(self):
        self.exp.entreprise = self.offre.transporteur
        with self.assertRaises(ValidationError):
            self.exp.save()

    def test_company_requires_matching_account(self):
        entreprise = self.exp.entreprise
        entreprise.utilisateur = self.offre.transporteur.utilisateur
        with self.assertRaises(ValidationError):
            entreprise.full_clean()

    def test_vehicle_ownership_and_capacity(self):
        self.offre.vehicule = self.autre.vehicule
        with self.assertRaises(ValidationError):
            self.offre.save()
        self.offre.refresh_from_db()
        vehicule = self.offre.vehicule
        vehicule.capacite_kg = 100
        vehicule.save()
        self.offre.vehicule = vehicule
        with self.assertRaises(ValidationError):
            self.offre.save()

    def test_unavailable_vehicle_rejected(self):
        vehicule = self.offre.vehicule
        vehicule.disponible = False
        vehicule.save()
        with self.assertRaises(ValidationError):
            self.offre.save()

    def test_positive_price_delay_weight(self):
        for field in ('prix', 'delai_jours'):
            old = getattr(self.offre, field)
            setattr(self.offre, field, 0)
            with self.assertRaises(ValidationError):
                self.offre.full_clean()
            setattr(self.offre, field, old)
        self.exp.poids_kg = Decimal('0')
        with self.assertRaises(ValidationError):
            self.exp.save()

    def test_duplicate_proposal_rejected_in_model_and_database(self):
        duplicate = Offre(expedition=self.exp, transporteur=self.offre.transporteur, vehicule=self.offre.vehicule, prix=100, delai_jours=1)
        with self.assertRaises(ValidationError):
            duplicate.save()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Offre.objects.bulk_create([duplicate])

    def test_acceptance_cascade_and_idempotence(self):
        self.accepter()
        self.assertEqual(self.exp.statut, 'attribuee')
        self.autre.refresh_from_db()
        self.assertEqual(self.autre.statut, 'refusee')
        self.offre.vehicule.refresh_from_db()
        self.assertFalse(self.offre.vehicule.disponible)
        self.offre.save()
        self.assertEqual(self.exp.offres.filter(statut='acceptee').count(), 1)

    def test_second_acceptance_and_new_proposal_rejected(self):
        self.accepter()
        self.autre.statut = 'acceptee'
        with self.assertRaises(ValidationError):
            self.autre.save()

    def test_accepted_conditions_immutable(self):
        self.accepter()
        self.offre.prix += Decimal('1')
        with self.assertRaises(ValidationError):
            self.offre.save()
        self.assertIn('prix', admin.site._registry[Offre].get_readonly_fields(None, self.offre))

    def test_assignment_cannot_be_forced_and_final_transition(self):
        self.exp.statut = 'attribuee'
        with self.assertRaises(ValidationError):
            self.exp.save()
        self.exp.statut = 'livree'
        with self.assertRaises(ValidationError):
            self.exp.save()

    def test_closing_mixed_selection_runs_business_rules(self):
        self.accepter()
        self.exp.statut = 'en_cours'
        self.exp.save()
        modeladmin = admin.site._registry[Expedition]
        with patch.object(modeladmin, 'message_user') as message:
            cloturer_expeditions(modeladmin, None, Expedition.objects.all())
        self.exp.refresh_from_db()
        self.offre.vehicule.refresh_from_db()
        self.assertEqual(self.exp.statut, 'livree')
        self.assertTrue(self.offre.vehicule.disponible)
        self.assertEqual(Expedition.objects.filter(statut='publiee').count(), 2)
        self.assertIn('1 expédition', message.call_args.args[1])

    def test_cancel_releases_vehicle_and_refuses_offers(self):
        self.accepter()
        self.exp.statut = 'annulee'
        self.exp.save()
        self.offre.refresh_from_db()
        self.offre.vehicule.refresh_from_db()
        self.assertEqual(self.offre.statut, 'refusee')
        self.assertTrue(self.offre.vehicule.disponible)

    def test_reservation_cannot_be_overridden(self):
        self.accepter()
        self.offre.vehicule.disponible = True
        with self.assertRaises(ValidationError):
            self.offre.vehicule.save()

    def test_proposition_date_is_not_updated(self):
        before = self.offre.date_proposition
        self.offre.prix += 1
        self.offre.save()
        self.offre.refresh_from_db()
        self.assertEqual(self.offre.date_proposition, before)

    def test_bulk_demo_detects_missing_cascades(self):
        Offre.objects.filter(pk=self.offre.pk).update(statut='acceptee')
        self.exp.refresh_from_db()
        self.assertEqual(self.exp.statut, 'publiee')
        checks = self.counts()
        self.assertEqual(checks['acceptation_sans_attribution'], 1)
        self.assertEqual(checks['disponibilite_incoherente'], 1)
        self.assertEqual(checks['propositions_apres_attribution'], 1)

    def test_seed_idempotent_and_anomaly_option(self):
        before = (Utilisateur.objects.count(), Offre.objects.count(), Expedition.objects.count())
        call_command('seed_demo', stdout=StringIO())
        self.assertEqual(before, (Utilisateur.objects.count(), Offre.objects.count(), Expedition.objects.count()))
        call_command('seed_demo', with_anomalies=True, stdout=StringIO())
        checks = self.counts()
        self.assertEqual(sum(checks.values()), 5)
        self.assertEqual(checks['doublons_proposition'], 0)

    def test_health_dashboard_and_export(self):
        response = self.client.get(reverse('admin:health_check'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contrôle d’intégrité')
        payload = self.client.get(reverse('admin:health_check')+'?format=json').json()
        self.assertEqual(len(payload['checks']), 6)
        self.assertEqual(payload['total'], 2)

    def test_health_access_control(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse('admin:health_check')).status_code, 302)
        user = Utilisateur.objects.create_user('staff', 'staff@example.com', is_staff=True)
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse('admin:health_check')).status_code, 403)
        self.client.force_login(self.offre.transporteur.utilisateur)
        self.assertEqual(self.client.get(reverse('admin:health_check')).status_code, 302)

    def test_admin_changelists_and_change_forms(self):
        for model, obj in [(Utilisateur, self.admin), (EntrepriseA, self.exp.entreprise), (Vehicule, self.offre.vehicule), (Expedition, self.exp), (Offre, self.offre)]:
            prefix = f'admin:{model._meta.app_label}_{model._meta.model_name}'
            self.assertEqual(self.client.get(reverse(prefix+'_changelist')).status_code, 200)
            self.assertEqual(self.client.get(reverse(prefix+'_change', args=[obj.pk])).status_code, 200)
            self.assertEqual(self.client.get(reverse(prefix+'_add')).status_code, 200)

    def test_overdue_filter(self):
        Expedition.objects.filter(pk=self.exp.pk).update(date_souhaitee=timezone.localdate()-timedelta(days=1))
        url = reverse('admin:ExpeditionA_expedition_changelist')
        response = self.client.get(url, {'en_retard': 'oui'})
        self.assertContains(response, self.exp.reference)
        self.assertNotContains(response, 'EXP-26-00002')

    def test_csv_export(self):
        entreprise = self.offre.transporteur
        entreprise.raison_sociale = '=1+1'
        entreprise.save()
        url = reverse('admin:OffreA_offre_changelist')
        response = self.client.post(url, {'action': 'exporter_offres_csv', '_selected_action': [self.offre.pk]})
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response['Content-Type'])
        self.assertContains(response, "'=1+1")
        self.assertContains(response, 'reference_expedition')

    def test_inline_is_read_only_and_no_add(self):
        from expeditionA.admin import OffreInline
        inline = OffreInline(Expedition, admin.site)
        self.assertFalse(inline.has_add_permission(None, self.exp))
        self.assertFalse(inline.can_delete)
        self.assertEqual(inline.fields, inline.readonly_fields)

    def test_generated_reference(self):
        exp = Expedition.objects.create(entreprise=self.exp.entreprise, ville_depart='Tunis', ville_arrivee='Gabès', poids_kg=10, date_souhaitee=timezone.localdate(), description='Test')
        self.assertTrue(exp.reference.startswith('EXP-'))
        self.assertNotEqual(exp.reference, self.exp.reference)
        self.assertLessEqual(len(exp.reference), 16)
