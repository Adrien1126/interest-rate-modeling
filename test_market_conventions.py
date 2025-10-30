"""
Test simple pour vérifier que les conventions de marché fonctionnent.
"""

import requests
import json

def test_pricing_with_market_conventions():
    """Test de pricing avec les conventions de marché."""
    
    url = "http://localhost:8000/api/pricing/option"
    
    payload = {
        "trade": {
            "trade_id": "TEST-001",
            "trade_date": "2025-10-30",
            "product_type": "Option",
            "option": {
                "option_type": "Call",
                "exercise_type": "European",
                "underlying": {
                    "asset_type": "Equity",
                    "isin": "US0000000000",
                    "description": "Test Asset"
                },
                "strike": 100.0,
                "expiration_date": "2026-10-30",
                "notional": {
                    "amount": 1.0,
                    "currency": "USD"
                },
                "settlement": {
                    "settlement_type": "Cash"
                }
            },
            "parties": {
                "buyer": {"id": "user", "name": "User"},
                "seller": {"id": "market", "name": "Market"}
            }
        },
        "spot_price": 100.0,
        "valuation_date": "2025-10-30",
        "market_conventions": {
            "day_count_convention": "ACT/365",
            "business_day_convention": "ModifiedFollowing",
            "calendar": "TARGET"
        },
        "model_type": "BlackScholes",
        "volatility": 0.2,
        "risk_free_rate": 0.05,
        "dividend_yield": 0.0,
        "pricing_method": "analytic",
        "compute_greeks": True
    }
    
    print("🚀 Envoi de la requête de pricing avec conventions de marché...")
    print(f"📅 Dates: {payload['trade']['trade_date']} → {payload['trade']['option']['expiration_date']}")
    print(f"📊 Conventions: {payload['market_conventions']}")
    
    response = requests.post(url, json=payload)
    
    print(f"\n📡 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS! Pricing result:")
        print(json.dumps(result, indent=2))
        print(f"\n💰 Price: {result['price']:.4f} {result['currency']}")
        if result.get('greeks'):
            print(f"📈 Delta: {result['greeks']['delta']:.4f}")
            print(f"📉 Gamma: {result['greeks']['gamma']:.4f}")
            print(f"⏰ Theta: {result['greeks']['theta']:.4f}")
            print(f"📊 Vega: {result['greeks']['vega']:.4f}")
    else:
        print(f"\n❌ ERROR: {response.text}")

if __name__ == "__main__":
    test_pricing_with_market_conventions()
