# Journal d’utilisation de l’IA

## Entrée 2026-10-26 - Implémentation assistée

- **Outil :** OpenAI Codex.
- **Prompt utilisateur :** « this is a django work can you do it for me and then pushit in my github https://github.com/dhia772/2ayai i want all work but try not to consume so much tokens » ; les deux PDF Models Part 1 et Admin étaient fournis.
- **Sortie obtenue :** modèles corrigés, migrations, règles métier, admin, commandes de démonstration/export, dashboard de six contrôles, tests et documentation.
- **Écarts du dépôt initial :** `user_id` n’était pas la PK et autorisait 100 caractères ; rôles `c/t` au lieu des valeurs demandées ; utilisateur d’entreprise facultatif ; noms `gerant`/`matricule_fiscale` différents du sujet ; restriction email Gmail non demandée ; absence des validations et cascades ; admin vide. Ces écarts ont été corrigés.
- **Hypothèses explicites :** la liste complète des règles métier annoncée dans le PDF Admin n’apparaît pas dans le PDF Models Part 1 fourni. Les règles implémentées découlent des descriptions, des exemples de cascade et des contrôles demandés. Les transitions, la réservation/libération et la protection des conditions acceptées sont documentées et testées. Aucun document Blackboard absent n’a été prétendu consulté.
- **Migrations :** la base historique a été inspectée : zéro utilisateur, entreprise, véhicule, expédition ou offre. Les migrations initiales ont été régénérées ; une installation ancienne nécessite une nouvelle base, comme indiqué dans le README.

### Bug Hunt - quatre anomalies du code fourni dans le PDF

| Anomalie | Correction | Justification |
|---|---|---|
| `prix = CharField(max_length=10)` | `DecimalField(max_digits=10, decimal_places=2)` avec minimum strictement positif | Montant numérique exact, tri/calculs corrects ; éviter les chaînes et les flottants monétaires. |
| `delai_jours = IntegerField()` | `PositiveIntegerField` et `MinValueValidator(1)` | Un délai négatif est invalide ; le validateur exclut aussi zéro. |
| `date_proposition = DateField(auto_now=True)` | `auto_now_add=True` | La date doit enregistrer la proposition initiale, sans changer à chaque modification. |
| FK `vehicule` avec `null=True` | FK obligatoire, sans `null=True` | Toute offre doit désigner un véhicule réel appartenant au transporteur. |

Le `save()` vide du brouillon ne suffit pas non plus à appliquer les cascades : les validations et transactions ont été ajoutées en complément des quatre corrections de champs.

### Opérations en masse et limites de l’IA

Pour les actions métier, l’assistant a directement utilisé une boucle avec `full_clean()` et `save()`. Il n’a pas proposé spontanément `update()`/`bulk_create()` comme remplacement des validations du dashboard. Les six contrôles sont des requêtes ORM en lecture seule avec `Count`, `annotate`, filtres et regroupements.

Un `update(statut='acceptee')` existe **uniquement dans la démonstration demandée** et dans le test qui la vérifie. Un autre `update(created_at=...)` prépare l’ancienneté de la fixture. `bulk_create()` figure uniquement dans un test de protection SQL. Ce sont des usages intentionnels, pas des actions de production.

Une IA peut générer une commande SQL valide qui ignore le métier. Les contraintes SQL simples protègent certains cas (unicité, valeurs positives), tandis que les effets sur plusieurs tables exigent des méthodes validées et des transactions. Le tableau de contrôle détecte le contournement sans modifier les données. Les tests ne prouvent pas à eux seuls la sécurité en concurrence multi-serveur ; SQLite sert à l’atelier et `select_for_update()` doit être évalué sur PostgreSQL pour un déploiement concurrent.

### Revue technique

Une requête de disponibilité initialement rédigée avec un `exclude()` sur une relation multiple a été remplacée par des conditions positives sur la même relation, pour ne pas ignorer un véhicule réutilisé après une livraison historique.

Les changements de code et cette documentation sont générés avec assistance IA. Aucun travail de revue personnelle par l’étudiant, aucune auto-évaluation des acquis, ni validation de l’enseignant ne sont revendiqués.
