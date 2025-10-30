"""
Exemple complet d'utilisation du système de trading JSON.

Ce script démontre comment:
1. Créer un trade JSON
2. Le valider
3. Le convertir en objet Option
4. Le pricer
5. Récupérer la réponse JSON
"""

import json
from datetime import date, timedelta

from backend.schemas.trade_schemas import (
    TradeContractSchema,
    PricingRequestSchema
)
from backend.core.utils.trade_converter import TradeConverter, PricingConverter
from backend.core.models.black_scholes import BlackScholesModel
from backend.core.pricing.analytic_pricer import AnalyticOptionPricer


def example_workflow():
    """Exemple complet de workflow."""
    
    print("\n" + "=" * 80)
    print("EXEMPLE COMPLET: CRÉATION, VALIDATION ET PRICING D'UN TRADE")
    print("=" * 80 + "\n")
    
    # ========================================================================
    # ÉTAPE 1: Création d'un trade JSON (comme envoyé par le frontend)
    # ========================================================================
    print("📝 ÉTAPE 1: Création du trade JSON")
    print("-" * 80)
    
    trade_json = {
        "trade": {
            "trade_id": "OPT-AAPL-001",
            "trade_date": "2025-10-29",
            "product_type": "Option",
            "option": {
                "option_type": "Call",
                "exercise_type": "European",
                "underlying": {
                    "asset_type": "Equity",
                    "isin": "US0378331005",
                    "ticker": "AAPL",
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
                    "id": "FUND_XYZ",
                    "name": "XYZ Investment Fund"
                },
                "seller": {
                    "id": "BANK_ABC",
                    "name": "ABC Investment Bank"
                }
            },
            "portfolio": "US_Tech_Equities",
            "book": "OPTIONS_DESK",
            "trader": "John_Smith"
        }
    }
    
    print(f"✅ Trade créé: {trade_json['trade']['trade_id']}")
    print(f"   Produit: {trade_json['trade']['product_type']}")
    print(f"   Sous-jacent: {trade_json['trade']['option']['underlying']['description']}")
    print(f"   Strike: ${trade_json['trade']['option']['strike']}")
    print()
    
    # ========================================================================
    # ÉTAPE 2: Validation du trade
    # ========================================================================
    print("✔️  ÉTAPE 2: Validation du trade")
    print("-" * 80)
    
    try:
        trade_contract = TradeContractSchema(**trade_json)
        print("✅ Trade JSON validé avec succès")
        print(f"   Pydantic validation: OK")
        
        # Extraction des métadonnées
        metadata = TradeConverter.extract_metadata(trade_contract)
        print(f"\n📊 Métadonnées extraites:")
        print(f"   - Buyer: {metadata['buyer']['name']}")
        print(f"   - Seller: {metadata['seller']['name']}")
        print(f"   - Underlying: {metadata['underlying']['description']}")
        print(f"   - Expiration: {metadata['expiration_date']}")
        print(f"   - Currency: {metadata['currency']}")
        print()
        
    except Exception as e:
        print(f"❌ Erreur de validation: {e}")
        return
    
    # ========================================================================
    # ÉTAPE 3: Conversion JSON → Objet Option
    # ========================================================================
    print("🔄 ÉTAPE 3: Conversion en objet Option")
    print("-" * 80)
    
    option = TradeConverter.trade_to_option(trade_contract)
    print(f"✅ Option créée: {option}")
    print(f"   Strike: ${option.strike}")
    print(f"   Maturité: {option.maturity:.4f} ans")
    print(f"   Type: {option.option_type.value.upper()}")
    print(f"   Exercice: {option.exercise_type.value.capitalize()}")
    print(f"   Notionnel: {option.notional}")
    print()
    
    # ========================================================================
    # ÉTAPE 4: Pricing de l'option
    # ========================================================================
    print("💰 ÉTAPE 4: Pricing de l'option")
    print("-" * 80)
    
    # Paramètres de marché
    spot_price = 145.0
    volatility = 0.25
    risk_free_rate = 0.05
    dividend_yield = 0.0
    
    print(f"Paramètres de marché:")
    print(f"   - Spot price: ${spot_price}")
    print(f"   - Volatilité: {volatility * 100}%")
    print(f"   - Taux sans risque: {risk_free_rate * 100}%")
    print(f"   - Dividend yield: {dividend_yield * 100}%")
    print()
    
    # Création du modèle et du pricer
    model = BlackScholesModel(
        volatility=volatility,
        risk_free_rate=risk_free_rate,
        dividend_yield=dividend_yield
    )
    pricer = AnalyticOptionPricer(model)
    
    # Calcul du prix
    price = pricer.price(option, spot=spot_price)
    print(f"✅ Prix calculé: ${price:.4f}")
    
    # Calcul des Greeks
    greeks = pricer.greeks(option, spot=spot_price)
    print(f"\n📊 Greeks calculés:")
    print(f"   - Delta: {greeks['delta']:.6f}")
    print(f"   - Gamma: {greeks['gamma']:.6f}")
    print(f"   - Vega: {greeks['vega']:.6f}")
    print(f"   - Theta: {greeks['theta']:.6f}")
    print(f"   - Rho: {greeks['rho']:.6f}")
    
    # Calcul de la volatilité implicite
    impl_vol = None
    if trade_contract.trade.option.premium:
        market_price = trade_contract.trade.option.premium.amount
        impl_vol = pricer.implied_volatility(
            option,
            spot=spot_price,
            market_price=market_price
        )
        if impl_vol is not None:
            print(f"\n🎯 Volatilité implicite:")
            print(f"   - Prix de marché: ${market_price}")
            print(f"   - Vol implicite: {impl_vol * 100:.2f}%")
    print()
    
    # ========================================================================
    # ÉTAPE 5: Création de la réponse JSON
    # ========================================================================
    print("📤 ÉTAPE 5: Création de la réponse JSON")
    print("-" * 80)
    
    response = PricingConverter.create_pricing_response(
        trade_id=trade_contract.trade.trade_id,
        price=price,
        currency=trade_contract.trade.option.notional.currency,
        valuation_date=date.today(),
        model_type="BlackScholes",
        model_parameters=model.get_parameters(),
        pricing_method="analytic",
        greeks=greeks,
        implied_volatility=impl_vol if trade_contract.trade.option.premium else None,
        computation_time_ms=1.23
    )
    
    # Sérialisation en JSON
    response_json = response.model_dump_json(indent=2)
    
    print("✅ Réponse JSON créée:")
    print(response_json)
    print()
    
    # ========================================================================
    # ÉTAPE 6: Exemple de réponse pour le frontend
    # ========================================================================
    print("📱 ÉTAPE 6: Format pour le frontend React")
    print("-" * 80)
    
    frontend_response = {
        "status": "success",
        "trade_id": trade_contract.trade.trade_id,
        "pricing": response.model_dump(),
        "summary": {
            "instrument": f"{option.option_type.value.upper()} on {metadata['underlying']['description']}",
            "strike": option.strike,
            "expiry": str(metadata['expiration_date']),
            "price": f"${price:.2f}",
            "moneyness": "ITM" if option.is_in_the_money(spot_price) else "OTM"
        }
    }
    
    print(json.dumps(frontend_response, indent=2, default=str))
    print()
    
    print("=" * 80)
    print("✅ WORKFLOW COMPLET RÉUSSI!")
    print("=" * 80)
    print()


def example_batch_pricing():
    """Exemple de pricing en batch de plusieurs options."""
    
    print("\n" + "=" * 80)
    print("EXEMPLE: PRICING EN BATCH DE PLUSIEURS OPTIONS")
    print("=" * 80 + "\n")
    
    # Création de plusieurs trades
    strikes = [140, 145, 150, 155, 160]
    spot_price = 150.0
    
    model = BlackScholesModel(
        volatility=0.25,
        risk_free_rate=0.05,
        dividend_yield=0.0
    )
    pricer = AnalyticOptionPricer(model)
    
    results = []
    
    for strike in strikes:
        # Création du trade
        trade_dict = {
            "trade": {
                "trade_id": f"OPT-{strike}",
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
                    "strike": float(strike),
                    "expiration_date": "2026-10-29",
                    "notional": {"amount": 100.0, "currency": "USD"},
                    "settlement": {"settlement_type": "Cash"}
                },
                "parties": {
                    "buyer": {"id": "buyer", "name": "Buyer"},
                    "seller": {"id": "seller", "name": "Seller"}
                }
            }
        }
        
        # Conversion et pricing
        trade_contract = TradeContractSchema(**trade_dict)
        option = TradeConverter.trade_to_option(trade_contract)
        price = pricer.price(option, spot=spot_price)
        greeks = pricer.greeks(option, spot=spot_price)
        
        # Moneyness
        if option.is_in_the_money(spot_price):
            moneyness = "ITM"
        elif option.is_at_the_money(spot_price):
            moneyness = "ATM"
        else:
            moneyness = "OTM"
        
        results.append({
            "strike": strike,
            "price": price,
            "delta": greeks['delta'],
            "moneyness": moneyness
        })
    
    # Affichage des résultats
    print(f"Spot Price: ${spot_price}")
    print(f"Volatilité: 25%, Taux: 5%, Maturité: 1 an\n")
    print(f"{'Strike':<10} {'Prix':<12} {'Delta':<12} {'Moneyness':<12}")
    print("-" * 50)
    
    for r in results:
        print(f"${r['strike']:<9} ${r['price']:<11.4f} {r['delta']:<12.6f} {r['moneyness']:<12}")
    
    print()


if __name__ == "__main__":
    example_workflow()
    example_batch_pricing()
