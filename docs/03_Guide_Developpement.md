# 🛠️ Guide de Développement

> Guide complet pour contribuer au projet : installation, standards de code et workflow Git

---

## 📋 Table des matières

- [Prérequis](#prérequis)
- [Installation](#installation)
- [Structure du projet](#structure-du-projet)
- [Standards de code](#standards-de-code)
- [Tests](#tests)
- [Workflow Git](#workflow-git)
- [CI/CD](#cicd)
- [Contribution](#contribution)

---

## Prérequis

### Logiciels requis

| Logiciel | Version minimum | Installation |
|----------|----------------|--------------|
| Python | 3.10+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 18.0+ | [nodejs.org](https://nodejs.org/) |
| PostgreSQL | 14.0+ | [postgresql.org](https://www.postgresql.org/download/) |
| Git | 2.30+ | [git-scm.com](https://git-scm.com/) |

### Vérifier les versions

```bash
python --version       # Python 3.10.x
node --version         # v18.x.x
psql --version         # psql 14.x
git --version          # git version 2.x
```

---

## Installation

### 1. Cloner le repository

```bash
git clone https://github.com/your-org/interest-rate-modeling.git
cd interest-rate-modeling
```

### 2. Setup Backend (Python)

```bash
# Créer environnement virtuel
python -m venv venv

# Activer l'environnement
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Vérifier l'installation
python -c "import fastapi, pydantic, numpy; print('✅ Backend OK')"
```

### 3. Setup Frontend (React)

```bash
cd frontend-react

# Installer les dépendances
npm install

# Vérifier l'installation
npm list react       # react@18.x.x
```

### 4. Setup Database (PostgreSQL)

```bash
# Créer la base de données
createdb interest_rate_db

# Appliquer les migrations (si alembic configuré)
alembic upgrade head

# Insérer les données initiales
python database/seeds.py
```

### 5. Variables d'environnement

Créer un fichier `.env` à la racine :

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/interest_rate_db

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Frontend
VITE_API_URL=http://localhost:8000

# Secrets (générer avec openssl rand -hex 32)
SECRET_KEY=your-secret-key-here
```

### 6. Démarrage

**Backend** :
```bash
# Terminal 1
uvicorn backend.main:app --reload
# Serveur sur http://localhost:8000
```

**Frontend** :
```bash
# Terminal 2
cd frontend-react
npm run dev
# App sur http://localhost:5173
```

**Tests** :
```bash
# Terminal 3
pytest
# 292 tests passants
```

---

## Structure du projet

### Organisation des fichiers

```
interest-rate-modeling/
│
├── backend/                  # Backend Python
│   ├── core/                # Business logic (indépendant de l'API)
│   │   ├── models/          # Modèles stochastiques
│   │   ├── products/        # Produits dérivés
│   │   ├── pricing/         # Pricers
│   │   ├── calibration/     # Calibration
│   │   └── utils/           # Utilitaires
│   │
│   ├── routers/             # API endpoints
│   ├── schemas/             # Validation Pydantic
│   └── dependencies/        # Dependencies FastAPI
│
├── frontend-react/           # Frontend React
│   ├── src/
│   │   ├── pages/           # Pages principales
│   │   ├── components/      # Composants réutilisables
│   │   └── hooks/           # Custom hooks
│   └── package.json
│
├── tests/                    # Tests (292 tests)
│   ├── backend/             # Tests API
│   ├── core/                # Tests business logic
│   └── integration/         # Tests end-to-end
│
├── database/                 # Database layer
├── docs/                     # Documentation
├── fiches/                   # Fiches théoriques
└── notebooks/                # Notebooks Jupyter
```

### Conventions de nommage

| Type | Convention | Exemple |
|------|-----------|---------|
| Fichiers Python | `snake_case.py` | `black_scholes.py` |
| Classes | `PascalCase` | `BlackScholesModel` |
| Fonctions | `snake_case()` | `price_option()` |
| Variables | `snake_case` | `spot_price` |
| Constantes | `UPPER_CASE` | `DEFAULT_SIMULATIONS` |
| Fichiers React | `PascalCase.jsx` | `Pricing.jsx` |
| Composants | `PascalCase` | `OptionForm` |

---

## Standards de code

### Python (Backend)

#### 1. Type Hints (100% du code)

```python
# ✅ BON
def price(
    self,
    option: EuropeanOption,
    spot: float,
    **kwargs
) -> float:
    """Calculate option price."""
    return self._calculate(option, spot)

# ❌ MAUVAIS
def price(self, option, spot):
    return self._calculate(option, spot)
```

#### 2. Docstrings (style Google)

```python
# ✅ BON
def generate_brownian_paths(
    n_paths: int,
    n_steps: int,
    dt: float
) -> np.ndarray:
    """
    Generate Brownian motion paths.
    
    Args:
        n_paths: Number of paths to generate
        n_steps: Number of time steps per path
        dt: Time step size
        
    Returns:
        Array of shape (n_paths, n_steps) with Brownian increments
        
    Raises:
        ValueError: If n_paths or n_steps <= 0
        
    Example:
        >>> paths = generate_brownian_paths(1000, 100, 0.01)
        >>> paths.shape
        (1000, 100)
    """
    if n_paths <= 0 or n_steps <= 0:
        raise ValueError("n_paths and n_steps must be positive")
    
    return np.random.randn(n_paths, n_steps) * np.sqrt(dt)
```

#### 3. Formatage (Black)

```bash
# Installer Black
pip install black

# Formater tout le code
black backend/ tests/

# Vérifier sans modifier
black --check backend/
```

Configuration `.black.toml` :
```toml
[tool.black]
line-length = 88
target-version = ['py310']
include = '\.pyi?$'
```

#### 4. Linting (Flake8)

```bash
# Installer Flake8
pip install flake8

# Vérifier le code
flake8 backend/ tests/
```

Configuration `.flake8` :
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = venv/,__pycache__/,.git/
```

#### 5. Import sorting (isort)

```bash
# Installer isort
pip install isort

# Trier les imports
isort backend/ tests/

# Vérifier
isort --check-only backend/
```

Configuration `.isort.cfg` :
```ini
[settings]
profile = black
line_length = 88
```

#### 6. Type checking (mypy)

```bash
# Installer mypy
pip install mypy

# Vérifier les types
mypy backend/
```

Configuration `mypy.ini` :
```ini
[mypy]
python_version = 3.10
strict = True
warn_return_any = True
warn_unused_configs = True
```

---

### JavaScript/React (Frontend)

#### 1. ESLint

```bash
# Installer ESLint
npm install --save-dev eslint

# Vérifier le code
npm run lint
```

Configuration `.eslintrc.json` :
```json
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended"
  ],
  "rules": {
    "react/prop-types": "off",
    "no-unused-vars": "warn"
  }
}
```

#### 2. Prettier

```bash
# Installer Prettier
npm install --save-dev prettier

# Formater le code
npm run format
```

Configuration `.prettierrc` :
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

---

## Tests

### Structure des tests

```
tests/
├── backend/                  # Tests API (routers)
│   ├── test_pricing_router.py
│   └── test_market_router.py
│
├── core/                     # Tests business logic
│   ├── pricing/
│   │   ├── test_analytic_pricer.py
│   │   └── test_montecarlo_pricer.py
│   ├── models/
│   │   └── test_black_scholes.py
│   └── products/
│       └── test_option.py
│
├── integration/              # Tests end-to-end
│   ├── test_end_to_end_pricing.py
│   └── test_api_vs_core_consistency.py
│
└── conftest.py              # Fixtures pytest
```

### Écrire un test

#### Test unitaire (backend/core)

```python
# tests/core/pricing/test_analytic_pricer.py
import pytest
from backend.core.models.black_scholes import BlackScholesModel
from backend.core.products.option import EuropeanOption
from backend.core.pricing.analytic_pricer import AnalyticOptionPricer


def test_call_price_atm():
    """Test pricing Call ATM with Black-Scholes."""
    # Arrange
    model = BlackScholesModel(r=0.05, sigma=0.2, q=0.0)
    option = EuropeanOption(option_type="Call", strike=100, maturity=1.0)
    pricer = AnalyticOptionPricer(model)
    spot = 100.0
    
    # Act
    price = pricer.price(option, spot)
    
    # Assert
    assert price > 0
    assert 10 < price < 11  # Valeur attendue ~10.45


def test_put_call_parity():
    """Test put-call parity for European options."""
    model = BlackScholesModel(r=0.05, sigma=0.2, q=0.0)
    pricer = AnalyticOptionPricer(model)
    
    call = EuropeanOption(option_type="Call", strike=100, maturity=1.0)
    put = EuropeanOption(option_type="Put", strike=100, maturity=1.0)
    spot = 100.0
    
    call_price = pricer.price(call, spot)
    put_price = pricer.price(put, spot)
    
    # C - P = S - K * exp(-r*T)
    parity = call_price - put_price
    expected = spot - 100 * np.exp(-0.05 * 1.0)
    
    assert abs(parity - expected) < 1e-10
```

#### Test d'intégration (API)

```python
# tests/backend/test_pricing_router.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_price_option_analytic(client):
    """Test POST /api/pricing/option with analytic method."""
    # Arrange
    payload = {
        "trade": {
            "product_type": "EuropeanOption",
            "option_type": "Call",
            "strike": 100,
            "maturity": 1.0
        },
        "spot_price": 100,
        "model_type": "BlackScholes",
        "model_params": {"r": 0.05, "sigma": 0.2, "q": 0.0},
        "pricing_method": "analytic"
    }
    
    # Act
    response = client.post("/api/pricing/option", json=payload)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "price" in data
    assert "greeks" in data
    assert data["price"] > 0
    assert 10 < data["price"] < 11
```

### Lancer les tests

```bash
# Tous les tests
pytest

# Tests avec couverture
pytest --cov=backend --cov-report=html

# Tests d'un fichier spécifique
pytest tests/core/pricing/test_analytic_pricer.py

# Tests d'une fonction spécifique
pytest tests/core/pricing/test_analytic_pricer.py::test_call_price_atm

# Tests avec output verbeux
pytest -v

# Tests en parallèle (plus rapide)
pytest -n auto
```

### Fixtures pytest

```python
# conftest.py
import pytest
from backend.core.models.black_scholes import BlackScholesModel
from backend.core.products.option import EuropeanOption


@pytest.fixture
def bs_model():
    """Black-Scholes model with default parameters."""
    return BlackScholesModel(r=0.05, sigma=0.2, q=0.0)


@pytest.fixture
def call_atm():
    """Call option at-the-money."""
    return EuropeanOption(option_type="Call", strike=100, maturity=1.0)


@pytest.fixture
def put_otm():
    """Put option out-of-the-money."""
    return EuropeanOption(option_type="Put", strike=90, maturity=1.0)


# Utilisation
def test_with_fixtures(bs_model, call_atm):
    pricer = AnalyticOptionPricer(bs_model)
    price = pricer.price(call_atm, spot=100)
    assert price > 0
```

### Objectifs de couverture

| Module | Couverture minimum | Actuel |
|--------|-------------------|--------|
| `core/` | 90% | 92% |
| `routers/` | 80% | 85% |
| `schemas/` | 95% | 98% |
| **Total** | **85%** | **87%** |

---

## Workflow Git

### Branches

| Type | Nom | Exemple |
|------|-----|---------|
| Développement principal | `main` | - |
| Feature | `feature/description` | `feature/heston-calibration` |
| Bugfix | `fix/description` | `fix/montecarlo-seed` |
| Release | `release/x.y.z` | `release/1.2.0` |

### Workflow standard

```bash
# 1. Créer une branche feature
git checkout -b feature/add-heston-model

# 2. Développer + commit réguliers
git add backend/core/models/heston.py
git commit -m "feat: add Heston stochastic volatility model"

# 3. Tests + formatage
pytest
black backend/
flake8 backend/

# 4. Push
git push origin feature/add-heston-model

# 5. Pull Request sur GitHub
# → Code review
# → Merge dans main
```

### Conventions de commit (Conventional Commits)

```bash
# Format : <type>(<scope>): <description>

# Types
feat:     # Nouvelle fonctionnalité
fix:      # Correction de bug
docs:     # Documentation
style:    # Formatage (pas de changement de logique)
refactor: # Refactoring
test:     # Ajout/modification de tests
chore:    # Tâches de maintenance

# Exemples
git commit -m "feat(pricing): add Monte Carlo confidence interval"
git commit -m "fix(greeks): correct Gamma calculation for Put options"
git commit -m "docs(api): update Swagger documentation"
git commit -m "test(heston): add calibration integration tests"
```

### Pull Request template

Créer `.github/pull_request_template.md` :

```markdown
## Description
<!-- Décrire les changements -->

## Type de changement
- [ ] Feature (nouvelle fonctionnalité)
- [ ] Bugfix (correction)
- [ ] Refactoring
- [ ] Documentation
- [ ] Tests

## Tests
- [ ] Tests unitaires ajoutés
- [ ] Tests d'intégration ajoutés
- [ ] Tous les tests passent (`pytest`)

## Checklist
- [ ] Code formaté (`black`, `isort`)
- [ ] Pas d'erreurs de linting (`flake8`)
- [ ] Type hints ajoutés (`mypy`)
- [ ] Documentation à jour
- [ ] Couverture >= 85%
```

---

## CI/CD

### GitHub Actions

Créer `.github/workflows/ci.yml` :

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov black flake8 mypy
      
      - name: Black formatting
        run: black --check backend/ tests/
      
      - name: Flake8 linting
        run: flake8 backend/ tests/
      
      - name: MyPy type checking
        run: mypy backend/
      
      - name: Run tests
        run: pytest --cov=backend --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

## Contribution

### Processus

1. **Fork** le repository
2. **Clone** votre fork
3. **Créer** une branche feature
4. **Développer** + tests
5. **Push** sur votre fork
6. **Pull Request** vers `main`

### Code review

**Critères** :
- ✅ Tests passants (292/292)
- ✅ Couverture >= 85%
- ✅ Code formaté (Black)
- ✅ Pas d'erreurs linting (Flake8)
- ✅ Type hints (mypy)
- ✅ Documentation à jour

### Bonnes pratiques

- 🎯 **1 PR = 1 feature** (petits PRs faciles à review)
- 📝 **Documentation** (docstrings + README si besoin)
- 🧪 **Tests** (unitaires + intégration)
- 🔄 **Commit réguliers** (petits commits atomiques)
- 💬 **Communication** (expliquer les choix techniques)

---

<div align="center">

**🛠️ Code propre, testé et maintenable**

*Black • Pytest • Type Hints • CI/CD*

</div>
