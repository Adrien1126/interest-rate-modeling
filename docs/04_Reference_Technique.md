# 📚 Référence Technique

> Documentation détaillée des modules, classes et fonctions

---

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Backend Core](#backend-core)
- [API Layer](#api-layer)
- [Database Layer](#database-layer)
- [Frontend](#frontend)
- [Constantes et configuration](#constantes-et-configuration)

---

## Vue d'ensemble

Cette référence documente tous les modules principaux du projet avec leurs signatures, paramètres et exemples d'utilisation.

---

## Backend Core

### Modèles Stochastiques (`backend/core/models/`)

#### `BlackScholesModel`

Modèle Black-Scholes pour prix d'actifs avec volatilité constante.

```python
class BlackScholesModel(BaseModel):
    def __init__(
        self,
        r: float,
        sigma: float,
        q: float = 0.0
    ):
        """
        Args:
            r: Taux sans risque (ex: 0.05 pour 5%)
            sigma: Volatilité (ex: 0.2 pour 20%)
            q: Dividend yield (optionnel, défaut 0.0)
        """
```

**Méthodes** :
```python
def simulate(
    self,
    S0: float,
    T: float,
    n_paths: int,
    n_steps: int,
    random_seed: Optional[int] = None
) -> np.ndarray:
    """
    Simule des trajectoires de prix.
    
    Args:
        S0: Prix initial
        T: Maturité (en années)
        n_paths: Nombre de trajectoires
        n_steps: Nombre de pas de temps
        random_seed: Seed aléatoire (optionnel)
        
    Returns:
        Array (n_paths, n_steps+1) de prix simulés
    """
```

**Exemple** :
```python
model = BlackScholesModel(r=0.05, sigma=0.2, q=0.02)
paths = model.simulate(S0=100, T=1.0, n_paths=1000, n_steps=252)
# paths.shape = (1000, 253)
```

---

#### `HestonModel`

Modèle Heston avec volatilité stochastique.

```python
class HestonModel(BaseModel):
    def __init__(
        self,
        r: float,
        v0: float,
        kappa: float,
        theta: float,
        sigma_v: float,
        rho: float,
        q: float = 0.0
    ):
        """
        Args:
            r: Taux sans risque
            v0: Variance initiale
            kappa: Vitesse de retour à la moyenne
            theta: Variance long terme
            sigma_v: Volatilité de la variance
            rho: Corrélation spot-variance
            q: Dividend yield (optionnel)
        """
```

**Exemple** :
```python
model = HestonModel(
    r=0.05,
    v0=0.04,
    kappa=2.0,
    theta=0.04,
    sigma_v=0.3,
    rho=-0.7,
    q=0.0
)
```

---

#### `HullWhiteModel`

Modèle Hull-White à 1 facteur pour taux d'intérêt.

```python
class HullWhiteModel(BaseModel):
    def __init__(
        self,
        a: float,
        sigma: float
    ):
        """
        Args:
            a: Vitesse de retour à la moyenne
            sigma: Volatilité du taux court
        """
```

**Exemple** :
```python
model = HullWhiteModel(a=0.1, sigma=0.01)
```

---

### Produits dérivés (`backend/core/products/`)

#### `EuropeanOption`

Option européenne (Call ou Put).

```python
class EuropeanOption(BaseProduct):
    def __init__(
        self,
        option_type: Literal["Call", "Put"],
        strike: float,
        maturity: float
    ):
        """
        Args:
            option_type: "Call" ou "Put"
            strike: Prix d'exercice (K > 0)
            maturity: Maturité en années (T > 0)
        """
```

**Méthodes** :
```python
def payoff(self, spot_price: float) -> float:
    """
    Calcule le payoff à maturité.
    
    Args:
        spot_price: Prix du sous-jacent à maturité
        
    Returns:
        max(S - K, 0) pour Call
        max(K - S, 0) pour Put
    """
```

**Exemple** :
```python
call = EuropeanOption(option_type="Call", strike=100, maturity=1.0)
payoff_call = call.payoff(spot_price=110)  # 10.0

put = EuropeanOption(option_type="Put", strike=100, maturity=1.0)
payoff_put = put.payoff(spot_price=90)  # 10.0
```

---

### Pricers (`backend/core/pricing/`)

#### `AnalyticOptionPricer`

Pricer analytique (formules fermées Black-Scholes).

```python
class AnalyticOptionPricer(BasePricer):
    def __init__(self, model: BlackScholesModel):
        """
        Args:
            model: Modèle Black-Scholes
        """
```

**Méthodes** :
```python
def price(
    self,
    option: EuropeanOption,
    spot: float,
    **kwargs
) -> float:
    """
    Calcule le prix de l'option.
    
    Args:
        option: Option européenne
        spot: Prix spot actuel
        
    Returns:
        Prix de l'option (formule Black-Scholes)
    """

def greeks(
    self,
    option: EuropeanOption,
    spot: float,
    **kwargs
) -> dict:
    """
    Calcule les grecques.
    
    Returns:
        {
            "delta": float,   # ∂V/∂S
            "gamma": float,   # ∂²V/∂S²
            "vega": float,    # ∂V/∂σ
            "theta": float,   # ∂V/∂t
            "rho": float      # ∂V/∂r
        }
    """
```

**Exemple** :
```python
model = BlackScholesModel(r=0.05, sigma=0.2, q=0.0)
pricer = AnalyticOptionPricer(model)
option = EuropeanOption(option_type="Call", strike=100, maturity=1.0)

price = pricer.price(option, spot=100)  # 10.45
greeks = pricer.greeks(option, spot=100)
# {"delta": 0.6368, "gamma": 0.0199, ...}
```

---

#### `MonteCarloOptionPricer`

Pricer Monte Carlo (simulations).

```python
class MonteCarloOptionPricer(BasePricer):
    def __init__(
        self,
        model: BaseModel,
        n_simulations: int = 10000,
        n_steps: int = 100,
        use_antithetic: bool = False,
        random_seed: Optional[int] = None
    ):
        """
        Args:
            model: Modèle stochastique (BS, Heston, etc.)
            n_simulations: Nombre de simulations
            n_steps: Nombre de pas de temps
            use_antithetic: Utiliser variables antithétiques
            random_seed: Seed pour reproductibilité
        """
```

**Méthodes** :
```python
def price(
    self,
    option: EuropeanOption,
    spot: float,
    **kwargs
) -> float:
    """
    Prix par Monte Carlo.
    
    Returns:
        Prix = E[exp(-rT) * payoff]
    """

def confidence_interval(
    self,
    option: EuropeanOption,
    spot: float,
    confidence_level: float = 0.95
) -> dict:
    """
    Intervalle de confiance.
    
    Args:
        confidence_level: Niveau de confiance (0.90, 0.95, 0.99)
        
    Returns:
        {
            "lower_bound": float,
            "upper_bound": float,
            "confidence_level": float
        }
    """
```

**Exemple** :
```python
model = BlackScholesModel(r=0.05, sigma=0.2, q=0.0)
pricer = MonteCarloOptionPricer(
    model,
    n_simulations=50000,
    use_antithetic=True,
    random_seed=42
)

option = EuropeanOption(option_type="Call", strike=100, maturity=1.0)
price = pricer.price(option, spot=100)  # 10.45 ± 0.05

ci = pricer.confidence_interval(option, spot=100, confidence_level=0.95)
# {"lower_bound": 10.38, "upper_bound": 10.52, "confidence_level": 0.95}
```

---

### Calibration (`backend/core/calibration/`)

#### `HestonCalibrator`

Calibrateur pour le modèle Heston.

```python
class HestonCalibrator(BaseCalibrator):
    def calibrate(
        self,
        market_prices: List[float],
        strikes: List[float],
        maturities: List[float],
        spot: float,
        r: float,
        initial_params: Optional[dict] = None
    ) -> dict:
        """
        Calibre le modèle Heston.
        
        Args:
            market_prices: Prix de marché observés
            strikes: Strikes correspondants
            maturities: Maturités correspondantes
            spot: Prix spot
            r: Taux sans risque
            initial_params: Paramètres initiaux (optionnel)
            
        Returns:
            {
                "v0": float,
                "kappa": float,
                "theta": float,
                "sigma_v": float,
                "rho": float,
                "rmse": float,
                "success": bool
            }
        """
```

**Exemple** :
```python
calibrator = HestonCalibrator()

result = calibrator.calibrate(
    market_prices=[10.5, 8.3, 6.2, 4.5],
    strikes=[90, 95, 100, 105],
    maturities=[1.0, 1.0, 1.0, 1.0],
    spot=100.0,
    r=0.05
)

print(f"RMSE: {result['rmse']:.4f}")
print(f"v0: {result['v0']:.4f}")
```

---

### Utilitaires (`backend/core/utils/`)

#### `stochastic_utils.py`

Fonctions pour simulations stochastiques.

```python
def generate_brownian_paths(
    n_paths: int,
    n_steps: int,
    dt: float,
    random_seed: Optional[int] = None,
    antithetic: bool = False
) -> np.ndarray:
    """
    Génère des trajectoires browniennes.
    
    Args:
        n_paths: Nombre de trajectoires
        n_steps: Nombre de pas de temps
        dt: Pas de temps (ex: 1/252 pour journalier)
        random_seed: Seed pour reproductibilité
        antithetic: Utiliser variables antithétiques
        
    Returns:
        Array (n_paths, n_steps) d'incréments browniens
        
    Example:
        >>> paths = generate_brownian_paths(1000, 252, 1/252, random_seed=42)
        >>> paths.shape
        (1000, 252)
        >>> paths.mean()  # ~0
        0.0012
    """
```

**Exemple** :
```python
# Générer 10k trajectoires sur 1 an (252 jours)
paths = generate_brownian_paths(
    n_paths=10000,
    n_steps=252,
    dt=1/252,
    random_seed=42,
    antithetic=True
)

# Simuler prix avec Black-Scholes
S0 = 100
r = 0.05
sigma = 0.2
T = 1.0

ST = S0 * np.exp((r - 0.5*sigma**2)*T + sigma*np.sqrt(T)*paths[:, -1])
```

---

#### `trade_converter.py`

Convertisseurs JSON ↔ Python.

```python
class TradeConverter:
    @staticmethod
    def from_json_schema(
        schema: PricingRequestSchema
    ) -> Tuple[BaseProduct, BaseModel]:
        """
        Convertit un schema Pydantic en objets métier.
        
        Args:
            schema: PricingRequestSchema
            
        Returns:
            (product, model)
            
        Raises:
            ValueError: Si product_type ou model_type inconnu
        """
    
    @staticmethod
    def create_pricing_response(
        price: float,
        greeks: dict,
        confidence_interval: Optional[dict] = None
    ) -> PricingResponseSchema:
        """
        Crée une réponse de pricing.
        
        Args:
            price: Prix calculé
            greeks: Dictionnaire des grecques
            confidence_interval: IC (optionnel)
            
        Returns:
            PricingResponseSchema validé
        """
```

**Exemple** :
```python
# JSON → Python
request = PricingRequestSchema(**json_data)
product, model = TradeConverter.from_json_schema(request)

# Python → JSON
response = TradeConverter.create_pricing_response(
    price=10.45,
    greeks={"delta": 0.64, "gamma": 0.02, "vega": 39.89, "theta": -6.41, "rho": 53.05},
    confidence_interval={"lower_bound": 10.38, "upper_bound": 10.52, "confidence_level": 0.95}
)
```

---

## API Layer

### Schemas (`backend/schemas/`)

#### `PricingRequestSchema`

```python
class PricingRequestSchema(BaseModel):
    trade: TradeSchema                        # Informations du trade
    spot_price: float                         # Prix spot (> 0)
    model_type: Literal["BlackScholes", "Heston", "HullWhite"]
    model_params: dict                        # Paramètres du modèle
    pricing_method: Literal["analytic", "monte_carlo"]
    
    # Monte Carlo (optionnels)
    n_simulations: Optional[int] = 10000
    n_steps: Optional[int] = 100
    use_antithetic: Optional[bool] = False
    random_seed: Optional[int] = None
    compute_confidence_interval: Optional[bool] = False
    confidence_level: Optional[float] = 0.95
```

#### `PricingResponseSchema`

```python
class PricingResponseSchema(BaseModel):
    price: float                              # Prix calculé
    greeks: GreeksSchema                      # Grecques
    confidence_interval: Optional[ConfidenceIntervalSchema] = None
```

#### `GreeksSchema`

```python
class GreeksSchema(BaseModel):
    delta: float                              # ∂V/∂S
    gamma: float                              # ∂²V/∂S²
    vega: float                               # ∂V/∂σ
    theta: float                              # ∂V/∂t
    rho: float                                # ∂V/∂r
```

---

### Routers (`backend/routers/`)

#### `pricing_router.py`

```python
@router.post("/option", response_model=PricingResponseSchema)
async def price_option(
    request: PricingRequestSchema
) -> PricingResponseSchema:
    """
    Price une option européenne.
    
    Args:
        request: Schéma de requête validé par Pydantic
        
    Returns:
        Schéma de réponse avec prix et grecques
        
    Raises:
        HTTPException(400): Si validation échoue
        HTTPException(500): Si erreur de calcul
    """
```

**Endpoints** :
- `POST /api/pricing/option` — Pricing options
- `GET /api/pricing/health` — Health check

---

## Database Layer

### Models (`database/models.py`)

#### `TradeDB`

```python
class TradeDB(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True)
    trade_id = Column(String, unique=True, nullable=False)
    product_type = Column(String, nullable=False)
    option_type = Column(String)              # "Call" ou "Put"
    strike = Column(Float)
    maturity = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### CRUD (`database/crud.py`)

```python
def create_trade(db: Session, trade: TradeDB) -> TradeDB:
    """Crée un nouveau trade."""
    
def get_trade(db: Session, trade_id: str) -> Optional[TradeDB]:
    """Récupère un trade par ID."""
    
def update_trade(db: Session, trade_id: str, **kwargs) -> TradeDB:
    """Met à jour un trade."""
    
def delete_trade(db: Session, trade_id: str) -> bool:
    """Supprime un trade."""
```

---

## Frontend

### Pages (`frontend-react/src/pages/`)

#### `Pricing.jsx`

Composant principal pour le pricing d'options.

**Props** : Aucune

**State** :
```javascript
const [formData, setFormData] = useState({
  optionType: 'Call',
  strike: 100,
  maturity: 1.0,
  spot: 100,
  volatility: 0.2,
  rate: 0.05,
  dividend: 0.0,
  pricingMethod: 'analytic',
  // Monte Carlo
  nSimulations: 50000,
  nSteps: 100,
  useAntithetic: true,
  randomSeed: 42,
  computeCI: true,
  confidenceLevel: 0.95
});

const [result, setResult] = useState(null);
```

**Méthodes** :
```javascript
const handleSubmit = async (e) => {
  // POST /api/pricing/option
};

const handleReset = () => {
  // Reset form
};
```

---

## Constantes et configuration

### Constantes par défaut

```python
# backend/core/utils/constants.py

# Monte Carlo
DEFAULT_N_SIMULATIONS = 10000
DEFAULT_N_STEPS = 100
DEFAULT_USE_ANTITHETIC = False
DEFAULT_CONFIDENCE_LEVEL = 0.95

# Pricing
MIN_SPOT_PRICE = 1e-6
MIN_STRIKE = 1e-6
MIN_MATURITY = 1e-6

# Grecques
EPSILON_SPOT = 0.01      # Pour Delta/Gamma (différences finies)
EPSILON_SIGMA = 0.0001   # Pour Vega
EPSILON_TIME = 1/365     # Pour Theta
EPSILON_RATE = 0.0001    # Pour Rho
```

### Configuration environnement

```bash
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/db
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
SECRET_KEY=your-secret-key
```

---

## Hiérarchie des classes

```
BaseModel (ABC)
├── BlackScholesModel
├── HestonModel
└── HullWhiteModel

BaseProduct (ABC)
├── EuropeanOption
├── Swap (à venir)
└── Swaption (à venir)

BasePricer (ABC)
├── AnalyticOptionPricer
├── MonteCarloOptionPricer
└── PDEPricer (à venir)

BaseCalibrator (ABC)
├── HestonCalibrator
├── VolSurfaceCalibrator
└── YieldCurveCalibrator
```

---

## Formules mathématiques

### Black-Scholes

Prix Call :
$$C = S_0 e^{-qT} N(d_1) - K e^{-rT} N(d_2)$$

Prix Put :
$$P = K e^{-rT} N(-d_2) - S_0 e^{-qT} N(-d_1)$$

Avec :
$$d_1 = \frac{\ln(S_0/K) + (r - q + \sigma^2/2)T}{\sigma\sqrt{T}}$$

$$d_2 = d_1 - \sigma\sqrt{T}$$

### Grecques

Delta Call :
$$\Delta_C = e^{-qT} N(d_1)$$

Delta Put :
$$\Delta_P = -e^{-qT} N(-d_1)$$

Gamma :
$$\Gamma = \frac{e^{-qT} \phi(d_1)}{S_0 \sigma \sqrt{T}}$$

Vega :
$$\nu = S_0 e^{-qT} \phi(d_1) \sqrt{T}$$

Theta Call :
$$\Theta_C = -\frac{S_0 \phi(d_1) \sigma e^{-qT}}{2\sqrt{T}} - rKe^{-rT}N(d_2) + qS_0 e^{-qT}N(d_1)$$

Rho Call :
$$\rho_C = K T e^{-rT} N(d_2)$$

---

<div align="center">

**📚 Référence complète pour développeurs**

*Toutes les signatures • Tous les paramètres • Tous les exemples*

</div>
