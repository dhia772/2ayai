# TransConnect - Workshops Models et Admin

Projet Django de Dhia, complété à partir du dépôt existant. Les quatre applications conservent leurs noms historiques : `entrepriseA`, `vehiculeA`, `expeditionA`, `offreA`. Le modèle `EntrepriseA` possède aussi l’alias Python `Entreprise`.

## Démarrage (PowerShell)

Python 3.10 ou supérieur :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

Ouvrir <http://127.0.0.1:8000/admin/> et se connecter avec le compte créé par `createsuperuser`. Aucun mot de passe administrateur n’est publié. Les comptes métier de démonstration ont un mot de passe inutilisable et ne sont pas staff.

Avec uv, les mêmes commandes sont disponibles via `uv run python manage.py ...`.

## Fonctionnalités

- Cinq modèles, `Utilisateur(AbstractUser)` avec clé primaire `user_id` de 8 caractères maximum, email unique, rôles métier et horodatage.
- Relations 1-1/FK, références générées, montants décimaux et contraintes SQL de positivité/unicité.
- Validation du type d’entreprise, de la propriété/disponibilité/capacité du véhicule et des propositions multiples.
- Acceptation transactionnelle : attribution de l’expédition, refus des offres concurrentes, réservation du véhicule.
- Cycle publié → attribué → en cours → livré, annulation contrôlée et libération du véhicule.
- Admin : cinq classes, filtres/recherche/autocomplétion, sections, dates en lecture seule, badges, édition rapide, flotte en TabularInline et offres en StackedInline non modifiable.
- Filtre « En retard », action de clôture respectant `full_clean()`/`save()`, export CSV, conditions d’une offre acceptée figées et identité TransConnect.
- Six contrôles ORM sur `/admin/health-check/`, export JSON et accès réservé aux utilisateurs staff disposant de toutes les permissions de consultation concernées.

## Démonstration du piège update()

Sur la base de démonstration locale :

```powershell
python manage.py seed_demo --with-anomalies
python manage.py health_report --output docs/integrity-report.json
```

Cette option reproduit **volontairement** le contournement du sujet : `EXP-26-00001` reçoit une offre acceptée par SQL sans cascade. `EXP-26-00002` utilise `full_clean()` puis `save()` et reste cohérente. La troisième publication a 9 jours et un transporteur est encore sans flotte. Le résultat attendu est 5 signalements sur 6 contrôles. Sans l’option, seules la publication ancienne et l’inscription sans flotte sont signalées. La commande est idempotente et ne remet pas à zéro des expéditions déjà traitées.

Le `seed_demo.py` Blackboard n’était pas fourni : son remplacement local reproduit les références et états attendus, puis ajoute les cas propres au rapport. Les données intentionnellement incohérentes sont réservées à la démonstration.

## Vérification

Depuis la racine du projet :

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Les tests couvrent notamment les cascades, erreurs de saisie, contraintes SQL, clôture de statuts mélangés, annulation, admin, CSV, permissions et détection du contournement SQL. Voir [le rapport](docs/RAPPORT_INTEGRITE.md) et [le journal IA](AI_LOG.md).

## Base et migrations

La base reste nommée `dhia.sqlite3`, conformément au sujet. L’ancienne base suivie dans Git était vide de comptes et de données métier. Les migrations initiales ont été régénérées pour corriger le schéma utilisateur (`id` numérique remplacé par `user_id`) et les champs historiques `gerant` / `matricule_fiscale`.

**Pour une ancienne copie du dépôt :** arrêter le serveur, sauvegarder puis renommer l’ancien `dhia.sqlite3`, et exécuter `migrate`. Cette version démarre avec une base neuve ; elle n’effectue pas une migration de données d’une ancienne installation. Ne pas appliquer ces nouvelles migrations initiales par-dessus une ancienne base déjà migrée.

Les bases SQLite, environnements, secrets et caches ne sont plus versionnés. Les autres exercices Python du dépôt sont conservés.

## Configuration

Variables d’environnement facultatives (à définir dans le terminal, aucun fichier `.env` n’est chargé automatiquement) :

- `DJANGO_DB_NAME` : chemin alternatif de la base.
- `DJANGO_SECRET_KEY` : clé stable, à définir pour conserver les sessions entre redémarrages.
- `DJANGO_DEBUG` : `1` en développement, `0` hors développement.
- `DJANGO_ALLOWED_HOSTS` : hôtes séparés par des virgules.

L’interface est en français, fuseau `Africa/Tunis`. Cette livraison concerne les workshops Models/Admin ; elle utilise l’admin pour les opérations et les méthodes du manager pour les contextes d’inscription chargeur/transporteur.

## Repères du sujet

| Livrable | Emplacement |
|---|---|
| Utilisateur et Entreprise | `entrepriseA/models.py` |
| Véhicule, Expédition, Offre | `vehiculeA`, `expeditionA`, `offreA` : `models.py` |
| Migrations | Les quatre dossiers `migrations/` |
| Personnalisation admin | Les quatre fichiers `admin.py`, `config/admin_site.py` |
| Tableau de contrôle | `config/health.py`, `templates/admin/health_check.html` |
| Jeu de données | `entrepriseA/management/commands/seed_demo.py` |
| Résultat réel exporté | `docs/integrity-report.json` |
| Rapport et Bug Hunt | `docs/RAPPORT_INTEGRITE.md`, `AI_LOG.md` |
