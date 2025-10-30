# 🏗️ Architecture — Interest Rate Modeling Platform

> Architecture complète de la plateforme : composants, flux de données et principes de conception

---

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture globale](#architecture-globale)
- [Composants principaux](#composants-principaux)
- [Flux de données](#flux-de-données)
- [Principes de conception](#principes-de-conception)
- [Structure des dossiers](#structure-des-dossiers)

---

## Vue d'ensemble

La plateforme suit une **architecture full-stack moderne en 3 couches** :

```
┌─────────────────────────────────────────────────────┐
│              FRONTEND (React)                       │
│          Interface utilisateur                      │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP REST
                   │ JSON
┌──────────────────▼──────────────────────────────────┐
│              BACKEND (FastAPI)                      │
│          API REST + Business Logic                  │
└──────────────────┬──────────────────────────────────┘
                   │ SQL
                   │
┌──────────────────▼──────────────────────────────────┐
│            DATABASE (PostgreSQL)                    │
│          Persistance des données                    │
└─────────────────────────────────────────────────────┘
```

### Chiffres clés

- **292 tests unitaires** (100% passants)
- **85% de couverture** de code
- **2 méthodes de pricing** (Analytique + Monte Carlo)
- **5 grecques** calculées (Delta, Gamma, Vega, Theta, Rho)
- **< 1ms** pour pricing analytique
- **< 500ms** pour Monte Carlo (50k simulations)

---

## Architecture globale

### Architecture en couches

```
Frontend (React)
    │
    ├─── Pages (Pricing, Calibration, Market)
    ├─── Components (Forms, Charts, Results)
    └─── Hooks (API calls, State management)
         │
         ▼ HTTP REST API (JSON)
         │
Backend (FastAPI)
    │
    ├─── API Layer
    │    ├─── Routers (endpoints)
    │    ├─── Schemas (validation Pydantic)
    │    └─── Dependencies (auth, DB)
    │         │
    ├─── Business Layer
    │    ├─── Core (logique métier)
    │    │    ├─── Models (Black-Scholes, Heston, Hull-White)
    │    │    ├─── Products (Options, Swaps, Swaptions)
    │    │    ├─── Pricing (Analytique, Monte Carlo, PDE)
    │    │    ├─── Calibration (Surfaces, Courbes)
    │    │    ├─── Market (Yield curves, Vol surfaces)
    │    │    └─── Utils (Stochastic, Converters, Math)
    │    │
    │    └─── FPML Parser
    │         │
    └─── Data Layer
         ├─── Database (models SQLAlchemy)
         ├─── CRUD (opérations DB)
         └─── Seeds (données initiales)
```

---

## Composants principaux

### 1. Frontend React

**Responsabilité** : Interface utilisateur interactive

**Technologies** :
- React 18 (UI framework)
- Vite (build tool)
- Material-UI (composants)
- Axios (HTTP client)

**Structure** :
```
frontend-react/
├── src/
│   ├── pages/
│   │   ├── Pricing.jsx          # Page de pricing
│   │   ├── Calibration.jsx      # Calibration (à venir)
│   │   └── Market.jsx            # Données de marché (à venir)
│   ├── components/
│   │   ├── OptionForm.jsx       # Formulaire options
│   │   ├── ResultsDisplay.jsx   # Affichage résultats
│   │   └── MonteCarloParams.jsx # Paramètres Monte Carlo
│   ├── hooks/
│   │   └── usePricing.js        # Hook pour pricing API
│   └── App.jsx
```

**Fonctionnalités** :
- ✅ Formulaire de pricing interactif
- ✅ Sélection méthode (Analytique / Monte Carlo)
- ✅ Paramètres Monte Carlo avancés
- ✅ Affichage prix + grecques
- ✅ Intervalle de confiance (Monte Carlo)

---

### 2. Backend FastAPI

**Responsabilité** : API REST + Moteur quantitatif

**Technologies** :
- Python 3.10+
- FastAPI (framework API)
- Pydantic (validation)
- NumPy, SciPy (calculs)
- SQLAlchemy (ORM)

**Structure détaillée** :

#### a) API Layer (`routers/`, `schemas/`)

```python
# routers/pricing_router.py
@router.post("/option")
async def price_option(request: PricingRequestSchema):
    """
    Endpoint de pricing d'option
    Supporte : analytique et Monte Carlo
    """
    # 1. Validation (Pydantic)
    # 2. Conversion schema → objets métier
    # 3. Création du pricer
    # 4. Calcul prix + grecques
    # 5. Construction réponse
    # 6. Retour JSON
```

**Endpoints disponibles** :
- `POST /api/pricing/option` — Pricing options
- `GET /api/pricing/health` — Health check
- `POST /api/market/curves` — Courbes de taux
- `POST /api/calibration/heston` — Calibration Heston
- `POST /api/fpml/parse` — Parser FpML

#### b) Business Layer (`core/`)

**Modèles stochastiques** (`core/models/`) :
```python
# Black-Scholes
class BlackScholesModel:
    def __init__(self, r: float, sigma: float, q: float = 0.0):
        self.r = r          # Taux sans risque
        self.sigma = sigma  # Volatilité
        self.q = q          # Dividend yield

# Heston (volatilité stochastique)
class HestonModel:
    def __init__(self, r, v0, kappa, theta, sigma_v, rho, q=0.0):
        # ...

# Hull-White (taux stochastiques)
class HullWhiteModel:
    def __init__(self, a, sigma):
        # ...
```

**Produits dérivés** (`core/products/`) :
```python
# Option européenne
class EuropeanOption:
    def __init__(
        self,
        option_type: Literal["Call", "Put"],
        strike: float,
        maturity: float
    ):
        self.option_type = option_type
        self.strike = strike
        self.maturity = maturity
```

**Pricers** (`core/pricing/`) :
```python
# Pricer analytique (formules fermées)
class AnalyticOptionPricer:
    def price(self, option, spot):
        # Formule Black-Scholes
        
    def greeks(self, option, spot):
        # Calcul Delta, Gamma, Vega, Theta, Rho

# Pricer Monte Carlo (simulations)
class MonteCarloOptionPricer:
    def __init__(
        self,
        model,
        n_simulations=10000,
        n_steps=100,
        use_antithetic=True,
        random_seed=None
    ):
        # ...
        
    def price(self, option, spot):
        # Simulation de trajectoires
        # Payoff moyen
        
    def confidence_interval(self, option, spot, confidence_level=0.95):
        # Intervalle de confiance statistique
```

**Utilitaires** (`core/utils/`) :
```python
# Générateur brownien
def generate_brownian_paths(
    n_paths: int,
    n_steps: int,
    dt: float,
    random_seed: Optional[int] = None,
    antithetic: bool = False
) -> np.ndarray:
    """Génère des trajectoires browniennes"""
    # ...

# Convertisseurs JSON ↔ Python
class TradeConverter:
    @staticmethod
    def from_json(json_data: dict) -> Trade:
        """JSON → Objet Trade"""
        
    @staticmethod
    def to_json(trade: Trade) -> dict:
        """Trade → JSON"""
```

#### c) Data Layer (`database/`)

```python
# models.py - Modèles SQLAlchemy
class TradeDB(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True)
    trade_id = Column(String, unique=True)
    product_type = Column(String)
    # ...

# crud.py - Opérations CRUD
def create_trade(db: Session, trade: TradeDB):
    # INSERT
    
def get_trade(db: Session, trade_id: str):
    # SELECT
```

---

### 3. Database PostgreSQL

**Responsabilité** : Persistance des données

**Tables principales** :
- `trades` — Trades enregistrés
- `market_data` — Données de marché
- `calibration_results` — Résultats de calibration
- `pricing_results` — Cache des pricings

---

## Flux de données

### Flux de pricing d'option (end-to-end)

```
1. FRONTEND (Pricing.jsx)
   │
   ├─ Utilisateur saisit :
   │  - Type option (Call/Put)
   │  - Spot, Strike, Maturity
   │  - Volatilité, Taux, Dividend
   │  - Méthode (analytique / Monte Carlo)
   │  - Paramètres MC (si MC sélectionné)
   │
   ├─ handleSubmit() construit JSON :
   │  {
   │    "trade": { ... },
   │    "spot_price": 100,
   │    "model_type": "BlackScholes",
   │    "pricing_method": "monte_carlo",
   │    "n_simulations": 50000,
   │    ...
   │  }
   │
   └─ POST http://localhost:8000/api/pricing/option
      │
      ▼
2. BACKEND (pricing_router.py)
   │
   ├─ FastAPI reçoit requête
   │
   ├─ Pydantic valide JSON → PricingRequestSchema
   │  (validation types, ranges, required fields)
   │
   ├─ TradeConverter.from_json_schema()
   │  PricingRequestSchema → Trade object
   │
   ├─ Création du modèle :
   │  model = BlackScholesModel(r, sigma, q)
   │
   ├─ Création du pricer :
   │  if pricing_method == "analytic":
   │      pricer = AnalyticOptionPricer(model)
   │  else:
   │      pricer = MonteCarloOptionPricer(
   │          model,
   │          n_simulations=50000,
   │          use_antithetic=True,
   │          random_seed=42
   │      )
   │
   ├─ Calcul pricing :
   │  price = pricer.price(option, spot)
   │  greeks = pricer.greeks(option, spot)
   │  
   │  if Monte Carlo + CI:
   │      ci = pricer.confidence_interval(...)
   │
   ├─ Construction réponse :
   │  response = {
   │      "price": 10.45,
   │      "greeks": { "delta": 0.64, ... },
   │      "confidence_interval": { ... }
   │  }
   │
   ├─ Pydantic sérialise → PricingResponseSchema
   │
   └─ Retour JSON
      │
      ▼
3. FRONTEND (Pricing.jsx)
   │
   ├─ Réception réponse JSON
   │
   ├─ setState(result)
   │
   └─ Affichage :
      - Prix
      - Grecques (Delta, Gamma, Vega, Theta, Rho)
      - Intervalle de confiance (si Monte Carlo)
      - Temps de calcul
```

### Flux détaillé du pricing Monte Carlo

```
MonteCarloOptionPricer.price(option, spot)
    │
    ├─ 1. Génération trajectoires browniennes
    │     generate_brownian_paths()
    │     → array shape (n_simulations, n_steps)
    │
    ├─ 2. Simulation prix sous-jacent
    │     S(t) = S0 * exp((r-q-σ²/2)*T + σ*√T*Z)
    │     → array shape (n_simulations,)
    │
    ├─ 3. Calcul payoffs
    │     if Call: max(S(T) - K, 0)
    │     if Put: max(K - S(T), 0)
    │
    ├─ 4. Actualisation
    │     PV = exp(-r*T) * mean(payoffs)
    │
    └─ 5. Retour prix
          → float
```

---

## Principes de conception

### 1. Séparation des responsabilités (SoC)

- **Frontend** : UI uniquement, pas de logique métier
- **API Layer** : Validation et routing
- **Business Layer** : Logique quantitative pure
- **Data Layer** : Persistance uniquement

### 2. Inversion de dépendances (DIP)

```python
# ✅ BON : Core indépendant de l'API
# core/pricing/base_pricer.py
class BasePricer(ABC):
    @abstractmethod
    def price(self, product, spot):
        pass

# backend/routers/pricing_router.py (dépend de core/)
from backend.core.pricing import AnalyticOptionPricer
```

### 3. DRY (Don't Repeat Yourself)

- Pas de duplication de code
- Utilitaires réutilisables (`core/utils/`)
- Base classes abstraites (`BasePricer`, `BaseModel`)

### 4. Type Safety

```python
# 100% du code typé avec mypy
def price(
    self,
    option: EuropeanOption,
    spot: float,
    **kwargs
) -> float:
    """Type hints partout"""
```

### 5. Testabilité

- Tests unitaires pour chaque module
- Mocks et fixtures pytest
- Tests d'intégration end-to-end

---

## Structure des dossiers

```
interest-rate-modeling/
│
├── backend/                          # Backend FastAPI
│   ├── main.py                      # Point d'entrée
│   │
│   ├── core/                        # Business logic (indépendant API)
│   │   ├── models/                  # Modèles stochastiques
│   │   │   ├── __init__.py
│   │   │   ├── base_model.py       # BaseModel abstrait
│   │   │   ├── black_scholes.py    # Black-Scholes
│   │   │   ├── heston.py           # Heston
│   │   │   └── hull_white.py       # Hull-White
│   │   │
│   │   ├── products/                # Produits dérivés
│   │   │   ├── __init__.py
│   │   │   ├── base_product.py     # BaseProduct abstrait
│   │   │   ├── option.py           # Options
│   │   │   ├── swap.py             # Swaps
│   │   │   └── swaption.py         # Swaptions
│   │   │
│   │   ├── pricing/                 # Pricers
│   │   │   ├── __init__.py
│   │   │   ├── base_pricer.py      # BasePricer abstrait
│   │   │   ├── analytic_pricer.py  # Analytique
│   │   │   ├── montecarlo_pricer.py # Monte Carlo
│   │   │   └── pde_pricer.py       # PDE (à venir)
│   │   │
│   │   ├── calibration/             # Calibration
│   │   │   ├── base_calibrator.py
│   │   │   ├── heston_calibrator.py
│   │   │   └── vol_surface_calibrator.py
│   │   │
│   │   ├── market/                  # Données de marché
│   │   │   ├── yield_curve.py
│   │   │   └── vol_surface.py
│   │   │
│   │   └── utils/                   # Utilitaires
│   │       ├── stochastic_utils.py  # Monte Carlo utils
│   │       ├── trade_converter.py   # JSON ↔ Python
│   │       └── math_utils.py        # Fonctions maths
│   │
│   ├── routers/                     # API Layer
│   │   ├── pricing_router.py       # /api/pricing/*
│   │   ├── market_router.py        # /api/market/*
│   │   ├── calibration_router.py   # /api/calibration/*
│   │   └── fpml_router.py          # /api/fpml/*
│   │
│   ├── schemas/                     # Validation Pydantic
│   │   ├── trade_schemas.py        # Trade, Option, Swap
│   │   ├── pricing_schemas.py      # PricingRequest/Response
│   │   ├── market_schemas.py       # Market data
│   │   └── calibration_schemas.py  # Calibration
│   │
│   └── dependencies/                # Dependencies injection
│       ├── auth.py                 # Authentification
│       └── database.py             # DB session
│
├── frontend-react/                  # Frontend React
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── App.jsx
│   └── package.json
│
├── database/                        # Data Layer
│   ├── models.py                   # Modèles SQLAlchemy
│   ├── crud.py                     # Opérations CRUD
│   ├── connection.py               # Connexion DB
│   └── seeds.py                    # Données initiales
│
├── tests/                           # Tests (292 tests)
│   ├── backend/                    # Tests API
│   ├── core/                       # Tests business logic
│   │   ├── pricing/
│   │   ├── models/
│   │   └── products/
│   ├── integration/                # Tests end-to-end
│   └── conftest.py                 # Fixtures pytest
│
├── docs/                            # Documentation
│   ├── README.md                   # Index
│   ├── 01_Architecture.md          # Ce fichier
│   ├── 02_Guide_Utilisation.md     # Guide API
│   ├── 03_Guide_Developpement.md   # Guide dev
│   └── 04_Reference_Technique.md   # Référence
│
├── fiches/                          # Fiches théoriques
├── notebooks/                       # Notebooks Jupyter
├── requirements.txt                 # Dépendances Python
├── README.md                        # README principal
└── QUICKSTART.md                    # Guide démarrage
```

---

## Patterns appliqués

### Factory Pattern

```python
# core/pricing/pricer_factory.py
class PricerFactory:
    @staticmethod
    def create(
        pricing_method: str,
        model: BaseModel,
        **kwargs
    ) -> BasePricer:
        if pricing_method == "analytic":
            return AnalyticOptionPricer(model)
        elif pricing_method == "monte_carlo":
            return MonteCarloOptionPricer(model, **kwargs)
        # ...
```

### Strategy Pattern

```python
# Différentes stratégies de pricing
class BasePricer(ABC):
    @abstractmethod
    def price(self, product, spot): pass

class AnalyticOptionPricer(BasePricer):
    def price(self, option, spot):
        # Stratégie analytique (Black-Scholes)

class MonteCarloOptionPricer(BasePricer):
    def price(self, option, spot):
        # Stratégie Monte Carlo (simulations)
```

### Repository Pattern

```python
# database/crud.py
class TradeRepository:
    def create(self, trade: TradeDB) -> TradeDB:
        # INSERT
        
    def get(self, trade_id: str) -> Optional[TradeDB]:
        # SELECT
        
    def update(self, trade_id: str, **kwargs):
        # UPDATE
        
    def delete(self, trade_id: str):
        # DELETE
```

---

## Prochaines évolutions architecturales

### Court terme

- [ ] Cache Redis pour les pricings
- [ ] Queue RabbitMQ pour calculs longs
- [ ] Microservices (pricing, calibration, market data)

### Moyen terme

- [ ] Event sourcing pour historique
- [ ] CQRS (Command Query Responsibility Segregation)
- [ ] GraphQL en complément de REST

### Long terme

- [ ] Architecture serverless (AWS Lambda)
- [ ] Kubernetes pour orchestration
- [ ] Service mesh (Istio)

---

<div align="center">

**🏗️ Architecture moderne, scalable et maintenable**

*Clean Architecture • SOLID • DRY • Type Safety*

</div>
