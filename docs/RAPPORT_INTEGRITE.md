# Rapport - Contrôle d’intégrité TransConnect

Projet : dépôt `dhia772/2ayai`. Réalisation assistée par Codex le 26 octobre 2026 ; les détails de l’assistance figurent dans `AI_LOG.md`. Ce rapport décrit le résultat technique obtenu ; il reste à l’étudiant de l’expliquer et de le relire avant remise.

## Fonctionnement

La sous-classe `TransConnectAdminSite` ajoute `/admin/health-check/` via `get_urls()`. `admin_view()` impose une session staff active ; la vue vérifie les permissions de consultation des quatre modèles métier. Le template étend l’administration Django. Les contrôles ne réparent ni ne modifient les objets : agrégations SQL, comptages complets, affichage limité aux 50 premières lignes, export JSON disponible depuis la page et la commande `health_report`.

Quatre contrôles proviennent directement de la liste du sujet : publications anciennes, absence de flotte, disponibilité incohérente et doublons. Deux contrôles supplémentaires ciblent précisément les cascades de la manipulation guidée. Le contrôle strict « offre orpheline » proposé dans le sujet n’a pas été retenu : une offre acceptée conservée pour l’historique après livraison est normale. Les contrôles supplémentaires distinguent cette situation d’une véritable acceptation sans attribution.

## Contrôles, règles et scénarios

| Contrôle | Règle protégée / justification | Scénario réaliste | Requête ORM |
|---|---|---|---|
| Expéditions bloquées | Alerte opérationnelle : publication sans attribution depuis plus de 7 jours. Ce seuil ne constitue pas une interdiction de publication. | Dossier oublié, absence de transporteur, cascade d’acceptation contournée. | `filter(statut='publiee', created_at__lt=now()-7j)` |
| Transporteurs sans flotte | Une offre doit associer un véhicule appartenant au transporteur. Une inscription sans flotte est signalée comme avertissement. | Inscription inachevée, dernier véhicule supprimé avant toute offre. | `annotate(nb_vehicules=Count('vehicules')).filter(nb_vehicules=0)` |
| Disponibilité incohérente | Une offre acceptée sur un transport actif réserve le véhicule. | `update()` accepte une offre sans mettre le véhicule indisponible ; restauration partielle. | Jointure véhicule/offre/expédition, statut accepté et expédition publiée/attribuée/en cours. |
| Doublons de proposition | Règle d’unicité d’une proposition par transporteur et expédition. | Import ancien effectué avant la contrainte ou restauration d’une base non conforme. | `values(expedition, transporteur).annotate(nombre=Count('pk')).filter(nombre__gt=1)` |
| Acceptation sans attribution | Accepter une offre doit attribuer son expédition. | Mise à jour SQL directe d’un seul statut. | Offres acceptées dont le statut d’expédition n’est ni attribuée, ni en cours, ni livrée. |
| Propositions concurrentes restantes | L’acceptation refuse les autres propositions ; une proposition exige une publication ouverte. | Import ou `update()` évitant le refus automatique ; annulation SQL sans cascade. | Filtre des propositions sur expédition possédant une acceptation ou n’étant plus publiée, puis `distinct()`. |

## Données propres à la démonstration

Le fichier Blackboard n’était pas joint ; une commande locale `seed_demo` a été écrite. Elle crée Dhia Distribution, Transport Nord, Transport Sud et Transport en inscription, trois véhicules, quatre offres et trois expéditions. Aucune donnée personnelle réelle n’est utilisée.

| Cas | Avant | Après `seed_demo --with-anomalies` |
|---|---|---|
| `EXP-26-00001` | Publiée, deux offres proposées, véhicule DEMO-001 disponible | Offre Nord acceptée par `update()` ; expédition toujours publiée, offre Sud toujours proposée, véhicule toujours disponible. |
| `EXP-26-00002` | Publiée, deux offres proposées | Offre Nord acceptée via `full_clean()`/`save()` ; expédition attribuée, offre Sud refusée, véhicule DEMO-003 indisponible. |
| `EXP-26-00003` | Publication créée par la fixture | Ancienneté de 9 jours, toujours publiée : alerte opérationnelle. |
| Transport en inscription | Compte transporteur sans véhicule | Avertissement de flotte incomplète. |

## Résultat réellement exporté

L’export [integrity-report.json](integrity-report.json) a été produit le 26/10/2026 à 22:36, heure de Tunis, après migration de la base et exécution de `seed_demo --with-anomalies`.

| Contrôle | Résultats |
|---|---:|
| Publications anciennes | 1 |
| Transporteurs sans flotte | 1 |
| Disponibilité incohérente | 1 |
| Doublons de proposition | 0 |
| Acceptation sans attribution | 1 |
| Propositions concurrentes restantes | 1 |
| **Total des signalements** | **5** |

Le total compte des signalements, pas cinq incidents indépendants : la première acceptation SQL est visible dans trois contrôles. Les doublons sont à zéro car la fixture n’en crée pas et une contrainte SQL conditionnelle les interdit, même via `bulk_create()` sur ce schéma. Le contrôle conserve son intérêt pour les anciennes bases/imports sans cette protection.

## Reproduire et vérifier

```text
python manage.py migrate
python manage.py seed_demo --with-anomalies
python manage.py health_report --output docs/integrity-report.json
python manage.py createsuperuser
python manage.py runserver
```

Se connecter à `/admin/health-check/`. Le JSON constitue l’export de résultat demandé ; aucune capture fictive n’est fournie. Une exécution sur une base déjà modifiée peut donner d’autres résultats.

La vérification exécutée inclut `check`, `makemigrations --check --dry-run` et les 26 tests Django, tous réussis. Elle vérifie les transitions, cascades, règles de validation, inlines, listes/formulaires admin, export CSV et permissions. La clôture d’une sélection mixte ne traite que les expéditions en cours et libère le véhicule en passant par les méthodes du modèle.

## Retour sur l’assistance IA

L’assistant n’a pas spontanément proposé d’opération de masse pour remplacer les contrôles ou la clôture. Le seul changement de statut par `update()` appartient à la reproduction explicite du piège du sujet. Le journal IA distingue les corrections du Bug Hunt, les écarts du dépôt initial et les limites des garanties obtenues. Les explications et résultats présentés ici ont été générés avec assistance et doivent être compris par l’étudiant avant soumission.
