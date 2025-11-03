## Synthèse – Faiblesses critiques de l’architecture et du code (à adresser en priorité)
1) Couche application/service manquante
- Symptômes:
  - Le router FastAPI convertit la requête, instancie modèle/produit, appelle les pricers et formate la réponse.
- Impacts:
  - Couplage web↔domaine, logique dupliquée entre endpoints; tests e2e nécessaires pour valider le cœur; évolutions d’API risquées.
- Correctifs:
  - Introduire un `PricingService` (orchestration) injecté; le router ne fait que valider/parsers et déléguer.
  - Déplacer `api_utils.py` hors de `core` vers `backend/adapters/http/`.
  - Séparer les converters (`pricing_request_converter` API↔domaine vs `trade_converter` JSON↔domaine) et unifier la maturité via `DateUtils` (QuantLib).

2) Gouvernance API
- Symptômes:
  - Pas de versionnage d’API; pas de SDK client.
- Impacts:
  - Évolutions délicates sans casser les intégrations; duplication d’implémentations client.
- Correctifs:
  - Préfixer `/api/v1/...`; générer un mini‑SDK depuis l’OpenAPI; définir une politique de dépréciation.

3) Goulots structurels : absence de parallélisation et couplage fort
- Symptômes:
  - Calculs Monte‑Carlo bloquants en mono‑process, endpoints synchrones.
  - Orchestration métier fortement couplée au router (voir point 1).
  - Pas de file/tâches de fond, ni de backpressure ou mécanisme d’annulation.
- Impacts:
  - Saturation CPU/mémoire, latences non bornées et risque de DoS.
  - Impossibilité de scaler ou de paralléliser sans refactor important.
  - Ordonnancement, tests et débogage rendus plus difficiles.
- Correctifs:
  - Paralléliser les calculs (multi‑process, vectorisation, JIT), ajouter chunking et seed.
  - Externaliser les gros calculs vers des workers/queues (Celery, RQ, etc.).
  - Imposer limites côté API (n_simulations/n_steps, timeouts, rate‑limits) et permettre l’annulation.
  - Exposer métriques (CPU, longueur de queue, latence) et séparer clairement API ↔ workers pour faciliter le scaling.

4) Organisation du dépôt — dégradation progressive
- Symptômes:
  - Scripts/utilitaires et fichiers `test_*.py` dupliqués à la racine; docs/notes éparpillées (ex. `architecture_summary.txt`); multiples points d’entrée; absence de conventions.
- Impacts:
  - Onboarding et revues PR ralentis; CI/tests instables; risques de régressions et déploiements non reproductibles.
- Correctifs:
  - Appliquer l’arborescence cible (scripts → `scripts/`, docs → `docs/`, tests → `tests/`).
  - Migrer/supprimer les doublons, corriger les imports et exécuter les tests.
  - Définir un plan de dépréciation.

5) Failles de test aux frontières
- Symptômes:
  - Excellente couverture cœur, mais peu de tests API (FastAPI TestClient) et pas de tests UI; tests présents à la racine en plus de `tests/`.
- Impacts:
  - Régressions de contrat API/UX non détectées; exécutions de tests incohérentes selon les outils.
- Correctifs:
  - Ajouter des tests d’API pour les endpoints clés et 1 smoke e2e UI (Playwright).
  - Déplacer tous les `test_*.py` de la racine sous `tests/` et supprimer les doublons.

6) Observabilité et gestion d’erreurs minimales
- Symptômes:
  - Logs non structurés, pas d’ID de corrélation, pas de métriques (latence, QPS, error rate).
- Impacts:
  - Investigations difficiles, faible traçabilité (non‑répudiation limitée).
- Correctifs:
  - Middleware de logging JSON avec request_id; niveaux de logs normalisés.
  - Exposer des métriques Prometheus; standardiser le mapping des erreurs (4xx vs 5xx).

7) Sécurité presque inexistante (si exposition hors dev)
- Symptômes:
  - Aucune authentification/autorisation; CORS permissif; pas de rate‑limit ni de timeouts contractuels.
- Impacts:
  - Surface d’attaque large (abus d’API, bruteforce, DoS par calculs MC lourds).
- Correctifs:
  - Auth simple (API key/JWT), CORS par environnement, rate‑limits (ex: slowapi) et timeouts côté serveur.
  - Gestion des secrets par variables d’environnement.

8) Déploiement et gestion d’environnements fragiles
- Symptômes:
  - Dépendances non verrouillées (ex. QuantLib absent), pas de conteneurisation ni d’artefacts reproductibles, scripts OS‑dépendants, absence de CI/CD.
- Impacts:
  - Déploiements non reproductibles, onboarding lent, divergences dev/staging/prod, rollback et maintenance difficiles.
- Correctifs:
  - Lockfiles/wheels pour dépendances natives; Dockerfile (+ docker‑compose) et images de build; pipeline CI pour lint/tests/build/push.
  - Scripts PowerShell équivalents; documentation d’installation.
  - Ranger les fichiers: `architecture_summary.txt` → `docs/`; scripts → `scripts/`.
  - Clarifier le nom du dépôt (ex: `option-pricer`) ou documenter la roadmap IRM.


## Proposition d’arborescence cible
```
.
├─ backend/
│  ├─ core/                 # Domaine pur (sans FastAPI)
│  │  ├─ models/
│  │  ├─ pricing/
│  │  │  ├─ base_pricer.py
│  │  │  ├─ option_pricer.py           # Différences finies génériques (réutilisées)
│  │  │  ├─ analytic_pricer.py         # + AnalyticOptionPricer (formules fermées)
│  │  │  └─ montecarlo_pricer.py       # Réutilise OptionPricer pour les greeks
│  │  ├─ products/
│  │  └─ utils/
│  ├─ app/                  # Application (orchestration)
│  │  ├─ services/
│  │  │  └─ pricing_service.py
│  │  └─ converters/
│  │     ├─ pricing_request_converter.py  # API ↔ domaine (+ conventions marché)
│  │     └─ trade_converter.py            # JSON ↔ domaine
│  ├─ adapters/
│  │  └─ http/
│  │     ├─ routers/
│  │     │  └─ pricing_router.py
│  │     └─ api_utils.py
│  ├─ schemas/
│  └─ main.py
├─ tests/
│  ├─ unit/
│  │  ├─ core/
│  │  ├─ app/
│  │  └─ adapters/
│  ├─ api/
│  └─ e2e/
├─ docs/
├─ examples/
├─ scripts/
│  ├─ start.sh
│  └─ start.ps1
├─ infra/
│  ├─ Dockerfile
│  ├─ docker-compose.yml
│  └─ .dockerignore
├─ README.md
├─ requirements.txt
└─ .env.example
```

Rôles des dossiers
- core: logique métier et quant, indépendante du framework web.
- app: orchestration applicative et conversions; point d’entrée des cas d’usage.
- adapters/http: adaptation FastAPI (routers, gestion erreurs/logs), pas de logique métier.
- schemas: contrats d’IO (Pydantic) partagés.
- tests: séparation nette unit/api/e2e pour une exécution ciblée.
- infra/scripts: conteneurisation et scripts cross‑platform.
