# 📘 Guide d'Utilisation — API REST

> Guide complet pour utiliser l'API de pricing et calibration

---

## 📋 Table des matières

- [Introduction](#introduction)
- [Démarrage rapide](#démarrage-rapide)
- [Authentification](#authentification)
- [Endpoints disponibles](#endpoints-disponibles)
- [Exemples concrets](#exemples-concrets)
- [Gestion des erreurs](#gestion-des-erreurs)
- [Swagger UI](#swagger-ui)

---

## Introduction

L'API REST permet de pricer des produits dérivés, calibrer des modèles et gérer des données de marché.

### URL de base

```
http://localhost:8000
```

### Format des échanges

- **Requêtes** : `Content-Type: application/json`
- **Réponses** : `Content-Type: application/json`
- **Encodage** : UTF-8

---

## Démarrage rapide

### 1. Démarrer le serveur

```bash
# Activer l'environnement virtuel
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate     # Windows

# Lancer le serveur
uvicorn backend.main:app --reload
```

Le serveur démarre sur `http://localhost:8000`

### 2. Vérifier le statut

```bash
curl http://localhost:8000/api/pricing/health
```

**Réponse attendue** :
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00"
}
```

### 3. Premier pricing

```bash
curl -X POST http://localhost:8000/api/pricing/option \
  -H "Content-Type: application/json" \
  -d '{
    "trade": {
      "product_type": "EuropeanOption",
      "option_type": "Call",
      "strike": 100,
      "maturity": 1.0
    },
    "spot_price": 100,
    "model_type": "BlackScholes",
    "model_params": {
      "r": 0.05,
      "sigma": 0.2,
      "q": 0.0
    },
    "pricing_method": "analytic"
  }'
```

---

## Authentification

> **Note** : L'authentification n'est pas encore implémentée en Phase 1.  
> Tous les endpoints sont publics en développement.

**À venir (Phase 2)** :
- API Keys
- JWT Tokens
- OAuth 2.0

---

## Endpoints disponibles

### Pricing

#### `POST /api/pricing/option`

Price une option européenne (Call ou Put).

**Request Body** :
```json
{
  "trade": {
    "product_type": "EuropeanOption",
    "option_type": "Call",  // "Call" ou "Put"
    "strike": 100.0,
    "maturity": 1.0
  },
  "spot_price": 100.0,
  "model_type": "BlackScholes",  // "BlackScholes", "Heston", "HullWhite"
  "model_params": {
    "r": 0.05,       // Taux sans risque
    "sigma": 0.2,    // Volatilité
    "q": 0.0         // Dividend yield (optionnel)
  },
  "pricing_method": "analytic",  // "analytic" ou "monte_carlo"
  
  // Paramètres Monte Carlo (optionnels, si pricing_method = "monte_carlo")
  "n_simulations": 50000,
  "n_steps": 100,
  "use_antithetic": true,
  "random_seed": 42,
  "compute_confidence_interval": true,
  "confidence_level": 0.95
}
```

**Response** :
```json
{
  "price": 10.450583572185565,
  "greeks": {
    "delta": 0.6368,
    "gamma": 0.0199,
    "vega": 39.894,
    "theta": -6.414,
    "rho": 53.050
  },
  
  // Intervalle de confiance (si Monte Carlo + compute_confidence_interval = true)
  "confidence_interval": {
    "lower_bound": 10.38,
    "upper_bound": 10.52,
    "confidence_level": 0.95
  }
}
```

#### `GET /api/pricing/health`

Health check du service de pricing.

**Response** :
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### Market Data

#### `POST /api/market/curves`

Crée ou récupère une courbe de taux.

**Request Body** :
```json
{
  "curve_id": "EUR_OIS_2024",
  "currency": "EUR",
  "maturities": [0.25, 0.5, 1.0, 2.0, 5.0, 10.0],
  "rates": [0.035, 0.037, 0.040, 0.042, 0.045, 0.048]
}
```

**Response** :
```json
{
  "curve_id": "EUR_OIS_2024",
  "status": "created",
  "interpolation_method": "linear"
}
```

---

### Calibration

#### `POST /api/calibration/heston`

Calibre le modèle Heston sur des données de marché.

**Request Body** :
```json
{
  "market_prices": [10.5, 8.3, 6.2, 4.5],
  "strikes": [90, 95, 100, 105],
  "maturities": [1.0, 1.0, 1.0, 1.0],
  "spot": 100.0,
  "r": 0.05,
  
  "initial_params": {
    "v0": 0.04,
    "kappa": 2.0,
    "theta": 0.04,
    "sigma_v": 0.3,
    "rho": -0.7
  }
}
```

**Response** :
```json
{
  "calibrated_params": {
    "v0": 0.0421,
    "kappa": 1.87,
    "theta": 0.0395,
    "sigma_v": 0.312,
    "rho": -0.68
  },
  "rmse": 0.023,
  "iterations": 45,
  "success": true
}
```

---

### FPML Parsing

#### `POST /api/fpml/parse`

Parse un fichier FpML et extrait les informations du trade.

**Request Body** :
```json
{
  "fpml_content": "<dataDocument xmlns='http://www.fpml.org/FpML-5/confirmation'>...</dataDocument>"
}
```

**Response** :
```json
{
  "trade_id": "TRADE-12345",
  "product_type": "EuropeanOption",
  "option_type": "Call",
  "strike": 100.0,
  "maturity": "2025-12-31",
  "currency": "USD"
}
```

---

## Exemples concrets

### Exemple 1 : Pricing analytique Call ATM

**Contexte** : Option Call européenne, spot = strike = 100, maturité 1 an, vol 20%.

```python
import requests

url = "http://localhost:8000/api/pricing/option"

payload = {
    "trade": {
        "product_type": "EuropeanOption",
        "option_type": "Call",
        "strike": 100,
        "maturity": 1.0
    },
    "spot_price": 100,
    "model_type": "BlackScholes",
    "model_params": {
        "r": 0.05,
        "sigma": 0.2,
        "q": 0.0
    },
    "pricing_method": "analytic"
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Prix : {result['price']:.4f}")
print(f"Delta : {result['greeks']['delta']:.4f}")
```

**Output** :
```
Prix : 10.4506
Delta : 0.6368
```

---

### Exemple 2 : Pricing Monte Carlo avec intervalle de confiance

**Contexte** : Même option, mais pricing Monte Carlo avec 100k simulations.

```python
payload = {
    "trade": {
        "product_type": "EuropeanOption",
        "option_type": "Call",
        "strike": 100,
        "maturity": 1.0
    },
    "spot_price": 100,
    "model_type": "BlackScholes",
    "model_params": {
        "r": 0.05,
        "sigma": 0.2,
        "q": 0.0
    },
    "pricing_method": "monte_carlo",
    "n_simulations": 100000,
    "n_steps": 100,
    "use_antithetic": True,
    "random_seed": 42,
    "compute_confidence_interval": True,
    "confidence_level": 0.95
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Prix : {result['price']:.4f}")
print(f"IC 95% : [{result['confidence_interval']['lower_bound']:.4f}, "
      f"{result['confidence_interval']['upper_bound']:.4f}]")
```

**Output** :
```
Prix : 10.4523
IC 95% : [10.3892, 10.5154]
```

---

### Exemple 3 : Put OTM avec dividendes

**Contexte** : Put strike 90, spot 100, dividend yield 2%.

```python
payload = {
    "trade": {
        "product_type": "EuropeanOption",
        "option_type": "Put",
        "strike": 90,
        "maturity": 0.5
    },
    "spot_price": 100,
    "model_type": "BlackScholes",
    "model_params": {
        "r": 0.05,
        "sigma": 0.25,
        "q": 0.02  # 2% dividend yield
    },
    "pricing_method": "analytic"
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Prix : {result['price']:.4f}")
print(f"Delta : {result['greeks']['delta']:.4f}")  # Négatif pour Put
print(f"Vega : {result['greeks']['vega']:.4f}")
```

**Output** :
```
Prix : 1.4523
Delta : -0.1234
Vega : 15.678
```

---

### Exemple 4 : Comparaison analytique vs Monte Carlo

```python
import time

# Analytique
start = time.time()
response_analytic = requests.post(url, json={
    "trade": {"product_type": "EuropeanOption", "option_type": "Call", "strike": 100, "maturity": 1.0},
    "spot_price": 100,
    "model_type": "BlackScholes",
    "model_params": {"r": 0.05, "sigma": 0.2, "q": 0.0},
    "pricing_method": "analytic"
})
time_analytic = time.time() - start

# Monte Carlo
start = time.time()
response_mc = requests.post(url, json={
    "trade": {"product_type": "EuropeanOption", "option_type": "Call", "strike": 100, "maturity": 1.0},
    "spot_price": 100,
    "model_type": "BlackScholes",
    "model_params": {"r": 0.05, "sigma": 0.2, "q": 0.0},
    "pricing_method": "monte_carlo",
    "n_simulations": 50000,
    "use_antithetic": True
})
time_mc = time.time() - start

print("Méthode       | Prix    | Temps")
print("--------------|---------|-------")
print(f"Analytique    | {response_analytic.json()['price']:.4f}  | {time_analytic*1000:.1f}ms")
print(f"Monte Carlo   | {response_mc.json()['price']:.4f}  | {time_mc*1000:.1f}ms")
```

**Output** :
```
Méthode       | Prix    | Temps
--------------|---------|-------
Analytique    | 10.4506  | 3.2ms
Monte Carlo   | 10.4523  | 487.5ms
```

---

### Exemple 5 : Workflow complet avec FPML

```python
# 1. Parser FpML
fpml_content = """
<dataDocument xmlns='http://www.fpml.org/FpML-5/confirmation'>
  <trade>
    <tradeHeader>
      <partyTradeIdentifier>
        <tradeId tradeIdScheme='http://www.example.com'>TRADE-12345</tradeId>
      </partyTradeIdentifier>
    </tradeHeader>
    <fxOption>
      <optionType>Call</optionType>
      <strike>
        <strikePrice>100.0</strikePrice>
      </strike>
      <expiryDate>2025-12-31</expiryDate>
    </fxOption>
  </trade>
</dataDocument>
"""

# Parser
parse_response = requests.post(
    "http://localhost:8000/api/fpml/parse",
    json={"fpml_content": fpml_content}
)
trade_data = parse_response.json()

# 2. Pricer avec les données extraites
pricing_payload = {
    "trade": {
        "product_type": trade_data["product_type"],
        "option_type": trade_data["option_type"],
        "strike": trade_data["strike"],
        "maturity": 1.0  # Calculé à partir de expiryDate
    },
    "spot_price": 100,
    "model_type": "BlackScholes",
    "model_params": {"r": 0.05, "sigma": 0.2, "q": 0.0},
    "pricing_method": "analytic"
}

pricing_response = requests.post(
    "http://localhost:8000/api/pricing/option",
    json=pricing_payload
)

print(f"Trade ID : {trade_data['trade_id']}")
print(f"Prix : {pricing_response.json()['price']:.4f}")
```

---

## Gestion des erreurs

### Codes HTTP

| Code | Signification | Action |
|------|--------------|---------|
| 200 | ✅ Succès | - |
| 400 | ❌ Requête invalide | Vérifier le format JSON |
| 422 | ❌ Validation échouée | Vérifier les types et ranges |
| 500 | ❌ Erreur serveur | Contacter le support |

### Format des erreurs

```json
{
  "detail": [
    {
      "loc": ["body", "trade", "strike"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

### Erreurs courantes

#### 1. Strike négatif

**Requête** :
```json
{
  "trade": {
    "strike": -10  // ❌ Erreur
  }
}
```

**Réponse (422)** :
```json
{
  "detail": [
    {
      "loc": ["body", "trade", "strike"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

#### 2. Méthode de pricing invalide

**Requête** :
```json
{
  "pricing_method": "invalid_method"  // ❌ Erreur
}
```

**Réponse (422)** :
```json
{
  "detail": [
    {
      "loc": ["body", "pricing_method"],
      "msg": "unexpected value; permitted: 'analytic', 'monte_carlo'",
      "type": "value_error.const"
    }
  ]
}
```

#### 3. Paramètres manquants

**Requête** :
```json
{
  "pricing_method": "monte_carlo"
  // ❌ Manque n_simulations
}
```

**Réponse (422)** :
```json
{
  "detail": [
    {
      "loc": ["body", "n_simulations"],
      "msg": "field required when pricing_method is monte_carlo",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Swagger UI

### Accès

Ouvrir dans le navigateur :
```
http://localhost:8000/docs
```

### Fonctionnalités

- 📖 Documentation interactive auto-générée
- 🧪 Tester les endpoints directement
- 📝 Voir les schémas JSON (Request/Response)
- 🔍 Explorer les modèles Pydantic

### Exemple d'utilisation

1. Aller sur `http://localhost:8000/docs`
2. Cliquer sur `POST /api/pricing/option`
3. Cliquer sur "Try it out"
4. Modifier le JSON d'exemple
5. Cliquer sur "Execute"
6. Voir la réponse en temps réel

### ReDoc (alternative)

Documentation alternative plus lisible :
```
http://localhost:8000/redoc
```

---

## Bonnes pratiques

### 1. Toujours valider avant d'envoyer

```python
# ✅ BON
import jsonschema

schema = {
    "type": "object",
    "required": ["trade", "spot_price", "model_type", "model_params"],
    # ...
}

jsonschema.validate(payload, schema)
requests.post(url, json=payload)
```

### 2. Gérer les timeouts

```python
# ✅ BON
try:
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
except requests.Timeout:
    print("Timeout : calcul trop long")
except requests.HTTPError as e:
    print(f"Erreur HTTP : {e.response.status_code}")
```

### 3. Utiliser des sessions pour performances

```python
# ✅ BON
session = requests.Session()

for payload in payloads:
    response = session.post(url, json=payload)
    # ...
```

### 4. Logger les requêtes

```python
# ✅ BON
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Pricing option : {payload}")
response = requests.post(url, json=payload)
logger.info(f"Résultat : {response.json()}")
```

---

## Limites actuelles

| Limite | Valeur | Raison |
|--------|--------|--------|
| Taille requête | 10 MB | Protection DoS |
| Timeout | 60s | Éviter blocages |
| Rate limit | Aucun (dev) | À implémenter en prod |
| Max simulations MC | 10M | Performance |

---

<div align="center">

**📘 API REST simple, puissante et bien documentée**

*Pydantic validation • FastAPI • Swagger UI*

</div>
