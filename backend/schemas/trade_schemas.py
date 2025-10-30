"""
Schémas Pydantic pour les contrats d'options et produits dérivés.

Ces schémas permettent de valider, sérialiser et désérialiser les contrats
au format JSON pour la communication entre frontend et backend.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import date, datetime
from enum import Enum


# ============================================================================
# ENUMS & CONVENTIONS
# ============================================================================

class DayCountConvention(str, Enum):
    """Day count conventions for year fraction calculations."""
    ACT_360 = "ACT/360"
    ACT_365 = "ACT/365"
    ACT_ACT = "ACT/ACT"
    THIRTY_360 = "30/360"
    THIRTY_E_360 = "30E/360"
    BUS_252 = "BUS/252"


class BusinessDayConvention(str, Enum):
    """Business day adjustment conventions."""
    FOLLOWING = "Following"
    MODIFIED_FOLLOWING = "ModifiedFollowing"
    PRECEDING = "Preceding"
    MODIFIED_PRECEDING = "ModifiedPreceding"
    UNADJUSTED = "Unadjusted"


class CalendarType(str, Enum):
    """Calendar types for business day adjustments."""
    TARGET = "TARGET"  # European Central Bank
    UNITED_STATES = "UnitedStates"
    UNITED_KINGDOM = "UnitedKingdom"
    JAPAN = "Japan"
    NULL_CALENDAR = "NullCalendar"  # No holidays


# ============================================================================
# ENUMS (Original)
# ============================================================================

class AssetType(str, Enum):
    """Types d'actifs sous-jacents."""
    EQUITY = "Equity"
    BOND = "Bond"
    COMMODITY = "Commodity"
    FX = "FX"
    INDEX = "Index"
    INTEREST_RATE = "InterestRate"


class SettlementType(str, Enum):
    """Types de règlement."""
    CASH = "Cash"
    PHYSICAL = "Physical"


# ============================================================================
# SOUS-SCHÉMAS
# ============================================================================

class UnderlyingSchema(BaseModel):
    """Schéma pour le sous-jacent."""
    asset_type: AssetType
    isin: Optional[str] = Field(None, description="Code ISIN de l'actif")
    ticker: Optional[str] = Field(None, description="Ticker de l'actif")
    description: str = Field(..., description="Description de l'actif")
    
    class Config:
        json_schema_extra = {
            "example": {
                "asset_type": "Equity",
                "isin": "US0378331005",
                "ticker": "AAPL",
                "description": "Apple Inc."
            }
        }


class NotionalSchema(BaseModel):
    """Schéma pour le notionnel."""
    amount: float = Field(..., gt=0, description="Montant du notionnel")
    currency: str = Field(..., min_length=3, max_length=3, description="Devise (ISO 4217)")
    
    @validator('currency')
    def currency_uppercase(cls, v):
        """Convertit la devise en majuscules."""
        return v.upper()
    
    class Config:
        json_schema_extra = {
            "example": {
                "amount": 100.0,
                "currency": "USD"
            }
        }


class PremiumSchema(BaseModel):
    """Schéma pour la prime."""
    amount: float = Field(..., description="Montant de la prime")
    currency: str = Field(..., min_length=3, max_length=3, description="Devise (ISO 4217)")
    payment_date: date = Field(..., description="Date de paiement de la prime")
    
    @validator('currency')
    def currency_uppercase(cls, v):
        """Convertit la devise en majuscules."""
        return v.upper()
    
    class Config:
        json_schema_extra = {
            "example": {
                "amount": 5.25,
                "currency": "USD",
                "payment_date": "2025-10-30"
            }
        }


class SettlementSchema(BaseModel):
    """Schéma pour le règlement."""
    settlement_type: SettlementType
    settlement_date: Optional[date] = Field(None, description="Date de règlement (si différente de l'expiration)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "settlement_type": "Cash"
            }
        }


class PartySchema(BaseModel):
    """Schéma pour une contrepartie."""
    id: str = Field(..., description="Identifiant unique de la partie")
    name: str = Field(..., description="Nom de la partie")
    lei: Optional[str] = Field(None, description="Legal Entity Identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "Bank_A",
                "name": "Bank A",
                "lei": "213800WAVVOPS85N2205"
            }
        }


class PartiesSchema(BaseModel):
    """Schéma pour les contreparties du trade."""
    buyer: PartySchema
    seller: PartySchema
    
    class Config:
        json_schema_extra = {
            "example": {
                "buyer": {
                    "id": "Bank_A",
                    "name": "Bank A"
                },
                "seller": {
                    "id": "Client_B",
                    "name": "Client B"
                }
            }
        }


# ============================================================================
# SCHÉMA OPTION
# ============================================================================

class OptionSchema(BaseModel):
    """Schéma pour une option."""
    option_type: Literal["Call", "Put"] = Field(..., description="Type d'option")
    exercise_type: Literal["European", "American", "Bermudan"] = Field(
        ..., 
        description="Type d'exercice"
    )
    underlying: UnderlyingSchema
    strike: float = Field(..., gt=0, description="Prix d'exercice (strike)")
    expiration_date: date = Field(..., description="Date d'expiration")
    notional: NotionalSchema
    premium: Optional[PremiumSchema] = Field(None, description="Prime payée")
    settlement: SettlementSchema
    
    # Paramètres optionnels pour options exotiques
    barrier: Optional[float] = Field(None, description="Barrière (pour options à barrière)")
    knock_type: Optional[Literal["In", "Out"]] = Field(None, description="Type de knock")
    
    class Config:
        json_schema_extra = {
            "example": {
                "option_type": "Call",
                "exercise_type": "European",
                "underlying": {
                    "asset_type": "Equity",
                    "isin": "US0378331005",
                    "description": "Apple Inc."
                },
                "strike": 150.0,
                "expiration_date": "2026-10-29",
                "notional": {
                    "amount": 100.0,
                    "currency": "USD"
                },
                "premium": {
                    "amount": 5.25,
                    "currency": "USD",
                    "payment_date": "2025-10-30"
                },
                "settlement": {
                    "settlement_type": "Cash"
                }
            }
        }


# ============================================================================
# SCHÉMA TRADE
# ============================================================================

class TradeSchema(BaseModel):
    """Schéma pour un trade complet."""
    trade_id: str = Field(..., description="Identifiant unique du trade")
    trade_date: date = Field(..., description="Date du trade")
    product_type: Literal["Option", "Swap", "Swaption", "Bond", "Forward"] = Field(
        ..., 
        description="Type de produit"
    )
    
    # Produits (un seul doit être renseigné selon product_type)
    option: Optional[OptionSchema] = None
    # swap: Optional[SwapSchema] = None  # À implémenter
    # swaption: Optional[SwaptionSchema] = None  # À implémenter
    
    parties: PartiesSchema
    
    # Métadonnées optionnelles
    portfolio: Optional[str] = Field(None, description="Portefeuille")
    book: Optional[str] = Field(None, description="Book de trading")
    trader: Optional[str] = Field(None, description="Trader responsable")
    
    @validator('option')
    def check_product_consistency(cls, v, values):
        """Vérifie que le produit correspond au product_type."""
        if values.get('product_type') == 'Option' and v is None:
            raise ValueError("L'option doit être renseignée pour product_type='Option'")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "trade_id": "OPT-001",
                "trade_date": "2025-10-29",
                "product_type": "Option",
                "option": {
                    "option_type": "Call",
                    "exercise_type": "European",
                    "underlying": {
                        "asset_type": "Equity",
                        "isin": "US0378331005",
                        "description": "Apple Inc."
                    },
                    "strike": 150.0,
                    "expiration_date": "2026-10-29",
                    "notional": {
                        "amount": 100.0,
                        "currency": "USD"
                    },
                    "premium": {
                        "amount": 5.25,
                        "currency": "USD",
                        "payment_date": "2025-10-30"
                    },
                    "settlement": {
                        "settlement_type": "Cash"
                    }
                },
                "parties": {
                    "buyer": {
                        "id": "Bank_A",
                        "name": "Bank A"
                    },
                    "seller": {
                        "id": "Client_B",
                        "name": "Client B"
                    }
                }
            }
        }


class TradeContractSchema(BaseModel):
    """Schéma pour le contrat complet (wrapper)."""
    trade: TradeSchema
    
    class Config:
        json_schema_extra = {
            "example": {
                "trade": {
                    "trade_id": "OPT-001",
                    "trade_date": "2025-10-29",
                    "product_type": "Option",
                    "option": {
                        "option_type": "Call",
                        "exercise_type": "European",
                        "underlying": {
                            "asset_type": "Equity",
                            "isin": "US0378331005",
                            "description": "Apple Inc."
                        },
                        "strike": 150.0,
                        "expiration_date": "2026-10-29",
                        "notional": {
                            "amount": 100.0,
                            "currency": "USD"
                        },
                        "premium": {
                            "amount": 5.25,
                            "currency": "USD",
                            "payment_date": "2025-10-30"
                        },
                        "settlement": {
                            "settlement_type": "Cash"
                        }
                    },
                    "parties": {
                        "buyer": {
                            "id": "Bank_A",
                            "name": "Bank A"
                        },
                        "seller": {
                            "id": "Client_B",
                            "name": "Client B"
                        }
                    }
                }
            }
        }


# ============================================================================
# SCHÉMAS DE RÉPONSE POUR LE PRICING
# ============================================================================

class MarketConventionsSchema(BaseModel):
    """Market conventions for date handling and calculations."""
    day_count_convention: DayCountConvention = Field(
        DayCountConvention.ACT_365,
        description="Day count convention for year fraction calculation"
    )
    business_day_convention: BusinessDayConvention = Field(
        BusinessDayConvention.MODIFIED_FOLLOWING,
        description="Business day adjustment convention"
    )
    calendar: CalendarType = Field(
        CalendarType.TARGET,
        description="Calendar for business day adjustments"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "day_count_convention": "ACT/365",
                "business_day_convention": "ModifiedFollowing",
                "calendar": "TARGET"
            }
        }


class PricingRequestSchema(BaseModel):
    """Schéma pour une demande de pricing."""
    trade: TradeSchema
    
    # Paramètres de marché
    spot_price: float = Field(..., gt=0, description="Prix spot du sous-jacent")
    valuation_date: Optional[date] = Field(None, description="Date de valorisation (si None, utilise trade_date)")
    
    # Conventions de marché (NOUVEAU)
    market_conventions: MarketConventionsSchema = Field(
        default=MarketConventionsSchema(
            day_count_convention=DayCountConvention.ACT_365,
            business_day_convention=BusinessDayConvention.MODIFIED_FOLLOWING,
            calendar=CalendarType.TARGET
        ),
        description="Conventions de marché pour calculs de dates"
    )
    
    # Paramètres du modèle
    model_type: Literal["BlackScholes", "Heston", "SABR"] = Field(
        "BlackScholes",
        description="Type de modèle"
    )
    volatility: Optional[float] = Field(None, ge=0, le=5, description="Volatilité (pour Black-Scholes)")
    risk_free_rate: Optional[float] = Field(None, description="Taux sans risque")
    dividend_yield: Optional[float] = Field(0.0, description="Rendement du dividende")
    
    # Méthode de pricing
    pricing_method: Literal["analytic", "monte_carlo"] = Field(
        "analytic",
        description="Méthode de pricing"
    )
    
    # Paramètres Monte Carlo (optionnels)
    n_simulations: Optional[int] = Field(10000, ge=100, le=1000000, description="Nombre de simulations Monte Carlo")
    n_steps: Optional[int] = Field(100, ge=10, le=1000, description="Nombre de pas de temps Monte Carlo")
    use_antithetic: Optional[bool] = Field(True, description="Utiliser variables antithétiques")
    random_seed: Optional[int] = Field(None, description="Graine aléatoire pour reproductibilité")
    
    # Options de calcul
    compute_greeks: bool = Field(True, description="Calculer les Greeks")
    compute_implied_vol: bool = Field(False, description="Calculer la volatilité implicite")
    compute_confidence_interval: bool = Field(False, description="Calculer l'intervalle de confiance (Monte Carlo uniquement)")
    confidence_level: Optional[float] = Field(0.95, ge=0.5, le=0.999, description="Niveau de confiance")
    
    class Config:
        json_schema_extra = {
            "example": {
                "trade": {
                    "trade_id": "OPT-001",
                    "trade_date": "2025-10-29",
                    "product_type": "Option",
                    "option": {
                        "option_type": "Call",
                        "exercise_type": "European",
                        "underlying": {
                            "asset_type": "Equity",
                            "isin": "US0378331005",
                            "description": "Apple Inc."
                        },
                        "strike": 150.0,
                        "expiration_date": "2026-10-29",
                        "notional": {
                            "amount": 100.0,
                            "currency": "USD"
                        },
                        "settlement": {
                            "settlement_type": "Cash"
                        }
                    },
                    "parties": {
                        "buyer": {"id": "Bank_A", "name": "Bank A"},
                        "seller": {"id": "Client_B", "name": "Client B"}
                    }
                },
                "spot_price": 145.0,
                "valuation_date": "2025-10-29",
                "market_conventions": {
                    "day_count_convention": "ACT/365",
                    "business_day_convention": "ModifiedFollowing",
                    "calendar": "TARGET"
                },
                "model_type": "BlackScholes",
                "volatility": 0.25,
                "risk_free_rate": 0.05,
                "dividend_yield": 0.0,
                "pricing_method": "analytic",
                "compute_greeks": True
            }
        }


class GreeksSchema(BaseModel):
    """Schéma pour les Greeks."""
    delta: Optional[float] = None
    gamma: Optional[float] = None
    vega: Optional[float] = None
    theta: Optional[float] = None
    rho: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "delta": 0.636,
                "gamma": 0.019,
                "vega": 0.375,
                "theta": -0.018,
                "rho": 0.532
            }
        }


class PricingResponseSchema(BaseModel):
    """Schéma pour la réponse de pricing."""
    trade_id: str
    price: float = Field(..., description="Prix du produit")
    currency: str
    valuation_date: date
    
    # Détails du modèle
    model_type: str
    model_parameters: dict
    
    # Greeks (optionnels)
    greeks: Optional[GreeksSchema] = None
    
    # Volatilité implicite (optionnel)
    implied_volatility: Optional[float] = None
    
    # Intervalle de confiance Monte Carlo (optionnel)
    confidence_interval: Optional[dict] = Field(
        None, 
        description="Intervalle de confiance pour Monte Carlo"
    )
    
    # Métadonnées
    pricing_method: str = Field(..., description="Méthode de pricing utilisée")
    computation_time_ms: Optional[float] = Field(None, description="Temps de calcul en millisecondes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "trade_id": "OPT-001",
                "price": 10.45,
                "currency": "USD",
                "valuation_date": "2025-10-29",
                "model_type": "BlackScholes",
                "model_parameters": {
                    "volatility": 0.25,
                    "risk_free_rate": 0.05,
                    "dividend_yield": 0.0
                },
                "greeks": {
                    "delta": 0.636,
                    "gamma": 0.019,
                    "vega": 0.375,
                    "theta": -0.018,
                    "rho": 0.532
                },
                "pricing_method": "analytic",
                "computation_time_ms": 1.23
            }
        }
