"""
Tests pour le système de gestion de trades JSON.

Teste:
- Conversion JSON → objet Option
- Conversion objet Option → JSON
- Validation des schémas
- Extraction des métadonnées
"""

import json
from datetime import date, timedelta

from backend.schemas.trade_schemas import (
    TradeContractSchema,
    PricingRequestSchema
)
from backend.core.utils.trade_converter import TradeConverter, PricingConverter
from backend.core.products.base_product import OptionType, ExerciseType


def test_json_parsing():
    """Test du parsing JSON → Pydantic."""
    print("=" * 70)
    print("TEST 1: PARSING JSON → PYDANTIC")
    print("=" * 70)
    
    json_str = '''
    {
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
    '''
    
    # Parsing (Pydantic V2)
    trade_contract = TradeContractSchema.model_validate_json(json_str)
    
    print(f"✅ JSON parsé avec succès")
    print(f"   Trade ID: {trade_contract.trade.trade_id}")
    print(f"   Product: {trade_contract.trade.product_type}")
    print(f"   Option Type: {trade_contract.trade.option.option_type}")
    print(f"   Strike: {trade_contract.trade.option.strike}")
    print(f"   Expiration: {trade_contract.trade.option.expiration_date}")
    print()


def test_json_to_option():
    """Test de la conversion JSON → Option."""
    print("=" * 70)
    print("TEST 2: CONVERSION JSON → OBJET OPTION")
    print("=" * 70)
    
    # Création d'un trade JSON
    trade_dict = {
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
        }
    }
    
    trade_contract = TradeContractSchema(**trade_dict)
    option = TradeConverter.trade_to_option(trade_contract)
    
    print(f"✅ Option créée: {option}")
    print(f"   Strike: {option.strike}")
    print(f"   Maturité: {option.maturity:.4f} ans")
    print(f"   Type: {option.option_type.value}")
    print(f"   Exercice: {option.exercise_type.value}")
    print(f"   Notionnel: {option.notional}")
    print()
    
    # Vérifications
    assert option.strike == 150.0, "Strike incorrect"
    assert option.option_type == OptionType.CALL, "Type incorrect"
    assert option.exercise_type == ExerciseType.EUROPEAN, "Exercice incorrect"
    assert option.notional == 100.0, "Notionnel incorrect"
    assert 0.9 < option.maturity < 1.1, "Maturité incorrecte (devrait être ~1 an)"
    
    print("✅ Toutes les vérifications passées")
    print()


def test_option_to_json():
    """Test de la conversion Option → JSON."""
    print("=" * 70)
    print("TEST 3: CONVERSION OBJET OPTION → JSON")
    print("=" * 70)
    
    from backend.core.products.option import Option
    
    # Création d'une option
    option = Option(
        strike=100.0,
        maturity=1.0,
        option_type=OptionType.PUT,
        exercise_type=ExerciseType.AMERICAN,
        notional=50.0
    )
    
    print(f"📊 Option créée: {option}")
    
    # Conversion en JSON
    expiration_date = date.today() + timedelta(days=365)
    trade_contract = TradeConverter.option_to_json(
        option=option,
        trade_id="OPT-002",
        underlying_description="Tesla Inc.",
        underlying_isin="US88160R1014",
        expiration_date=expiration_date,
        premium_amount=8.50,
        buyer_id="Hedge_Fund_X",
        seller_id="Bank_Y",
        currency="USD"
    )
    
    print(f"✅ Trade contract créé")
    print(f"   Trade ID: {trade_contract.trade.trade_id}")
    print(f"   Option Type: {trade_contract.trade.option.option_type}")
    print(f"   Strike: {trade_contract.trade.option.strike}")
    print(f"   Premium: {trade_contract.trade.option.premium.amount if trade_contract.trade.option.premium else 'N/A'}")
    print()
    
    # Export JSON (Pydantic V2)
    json_output = trade_contract.model_dump_json(indent=2)
    print("✅ JSON exporté:")
    print(json_output[:500] + "..." if len(json_output) > 500 else json_output)
    print()


def test_metadata_extraction():
    """Test de l'extraction des métadonnées."""
    print("=" * 70)
    print("TEST 4: EXTRACTION DES MÉTADONNÉES")
    print("=" * 70)
    
    trade_dict = {
        "trade": {
            "trade_id": "OPT-003",
            "trade_date": "2025-10-29",
            "product_type": "Option",
            "option": {
                "option_type": "Call",
                "exercise_type": "European",
                "underlying": {
                    "asset_type": "Equity",
                    "isin": "FR0000120073",
                    "ticker": "AIR",
                    "description": "Airbus SE"
                },
                "strike": 120.0,
                "expiration_date": "2026-04-29",
                "notional": {
                    "amount": 1000.0,
                    "currency": "EUR"
                },
                "premium": {
                    "amount": 12.50,
                    "currency": "EUR",
                    "payment_date": "2025-10-30"
                },
                "settlement": {
                    "settlement_type": "Cash"
                }
            },
            "parties": {
                "buyer": {
                    "id": "FUND_001",
                    "name": "Global Investment Fund",
                    "lei": "213800WAVVOPS85N2205"
                },
                "seller": {
                    "id": "BANK_001",
                    "name": "European Bank"
                }
            },
            "portfolio": "Europe_Equity",
            "book": "AIRBUS_DERIVATIVES",
            "trader": "John_Doe"
        }
    }
    
    trade_contract = TradeContractSchema(**trade_dict)
    metadata = TradeConverter.extract_metadata(trade_contract)
    
    print("✅ Métadonnées extraites:")
    for key, value in metadata.items():
        print(f"   {key}: {value}")
    print()


def test_pricing_request():
    """Test de la création d'une requête de pricing."""
    print("=" * 70)
    print("TEST 5: CRÉATION REQUÊTE DE PRICING")
    print("=" * 70)
    
    pricing_request = PricingRequestSchema(
        trade={
            "trade_id": "OPT-004",
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
        spot_price=145.0,
        model_type="BlackScholes",
        volatility=0.25,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        compute_greeks=True,
        compute_implied_vol=False
    )
    
    print("✅ Requête de pricing créée:")
    print(f"   Trade ID: {pricing_request.trade.trade_id}")
    print(f"   Spot: {pricing_request.spot_price}")
    print(f"   Modèle: {pricing_request.model_type}")
    print(f"   Volatilité: {pricing_request.volatility}")
    print(f"   Taux sans risque: {pricing_request.risk_free_rate}")
    print(f"   Compute Greeks: {pricing_request.compute_greeks}")
    print()
    
    # Export JSON (Pydantic V2)
    json_request = pricing_request.model_dump_json(indent=2)
    print("✅ JSON de la requête:")
    print(json_request[:500] + "..." if len(json_request) > 500 else json_request)
    print()


def test_pricing_response():
    """Test de la création d'une réponse de pricing."""
    print("=" * 70)
    print("TEST 6: CRÉATION RÉPONSE DE PRICING")
    print("=" * 70)
    
    response = PricingConverter.create_pricing_response(
        trade_id="OPT-001",
        price=10.45,
        currency="USD",
        valuation_date=date.today(),
        model_type="BlackScholes",
        model_parameters={
            "volatility": 0.25,
            "risk_free_rate": 0.05,
            "dividend_yield": 0.0
        },
        pricing_method="analytic",
        greeks={
            "delta": 0.636,
            "gamma": 0.019,
            "vega": 0.375,
            "theta": -0.018,
            "rho": 0.532
        },
        computation_time_ms=1.23
    )
    
    print("✅ Réponse de pricing créée:")
    print(f"   Trade ID: {response.trade_id}")
    print(f"   Prix: {response.price} {response.currency}")
    print(f"   Modèle: {response.model_type}")
    print(f"   Greeks: {response.greeks}")
    print(f"   Temps de calcul: {response.computation_time_ms} ms")
    print()
    
    # Export JSON (Pydantic V2)
    json_response = response.model_dump_json(indent=2)
    print("✅ JSON de la réponse:")
    print(json_response)
    print()


def main():
    """Lance tous les tests."""
    print("\n")
    print("🧪 TESTS DU SYSTÈME DE GESTION DE TRADES JSON")
    print("=" * 70)
    print()
    
    try:
        test_json_parsing()
        test_json_to_option()
        test_option_to_json()
        test_metadata_extraction()
        test_pricing_request()
        test_pricing_response()
        
        print("=" * 70)
        print("✅ TOUS LES TESTS ONT RÉUSSI!")
        print("=" * 70)
        print()
        
    except AssertionError as e:
        print(f"\n❌ ERREUR D'ASSERTION: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ ERREUR: {e}\n")
        raise


if __name__ == "__main__":
    main()
