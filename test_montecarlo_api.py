"""
Script de test pour l'API de pricing Monte Carlo.

Usage:
    python test_montecarlo_api.py
"""

import requests
import json
from datetime import date, timedelta

# URL de l'API
BASE_URL = "http://localhost:8000"

# Trade d'exemple
today = date.today()
expiry = today + timedelta(days=365)

trade_analytic = {
    "trade": {
        "trade_id": "OPT-MC-001",
        "trade_date": today.isoformat(),
        "product_type": "Option",
        "option": {
            "option_type": "Call",
            "exercise_type": "European",
            "underlying": {
                "asset_type": "Equity",
                "ticker": "AAPL",
                "description": "Apple Inc."
            },
            "strike": 150.0,
            "expiration_date": expiry.isoformat(),
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
    "model_type": "BlackScholes",
    "volatility": 0.25,
    "risk_free_rate": 0.05,
    "dividend_yield": 0.0,
    "pricing_method": "analytic",
    "compute_greeks": True
}

trade_montecarlo = {
    **trade_analytic,
    "pricing_method": "monte_carlo",
    "n_simulations": 50000,
    "n_steps": 100,
    "use_antithetic": True,
    "random_seed": 42,
    "compute_confidence_interval": True,
    "confidence_level": 0.95
}


def test_health():
    """Test du health check."""
    print("\n" + "="*60)
    print("TEST HEALTH CHECK")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/pricing/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    

def test_analytic_pricing():
    """Test du pricing analytique."""
    print("\n" + "="*60)
    print("TEST PRICING ANALYTIQUE")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/api/pricing/option",
        json=trade_analytic
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"\nRésultat:")
    print(f"  Prix: {result['price']:.4f} {result['currency']}")
    print(f"  Méthode: {result['pricing_method']}")
    print(f"  Temps: {result.get('computation_time_ms', 0):.2f} ms")
    
    if result.get('greeks'):
        print(f"\n  Greeks:")
        for greek, value in result['greeks'].items():
            if value is not None:
                print(f"    {greek}: {value:.4f}")
    
    return result


def test_montecarlo_pricing():
    """Test du pricing Monte Carlo."""
    print("\n" + "="*60)
    print("TEST PRICING MONTE CARLO")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/api/pricing/option",
        json=trade_montecarlo
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"\nRésultat:")
    print(f"  Prix: {result['price']:.4f} {result['currency']}")
    print(f"  Méthode: {result['pricing_method']}")
    print(f"  Temps: {result.get('computation_time_ms', 0):.2f} ms")
    
    if result.get('greeks'):
        print(f"\n  Greeks:")
        for greek, value in result['greeks'].items():
            if value is not None:
                print(f"    {greek}: {value:.4f}")
    
    if result.get('confidence_interval'):
        ci = result['confidence_interval']
        print(f"\n  Intervalle de confiance ({ci['confidence_level']*100}%):")
        print(f"    Borne inf: {ci['lower_bound']:.4f}")
        print(f"    Borne sup: {ci['upper_bound']:.4f}")
        print(f"    Std error: {ci['std_error']:.4f}")
    
    return result


def compare_methods():
    """Compare les deux méthodes."""
    print("\n" + "="*60)
    print("COMPARAISON DES MÉTHODES")
    print("="*60)
    
    # Pricing analytique
    analytic_result = requests.post(
        f"{BASE_URL}/api/pricing/option",
        json=trade_analytic
    ).json()
    
    # Pricing Monte Carlo
    mc_result = requests.post(
        f"{BASE_URL}/api/pricing/option",
        json=trade_montecarlo
    ).json()
    
    print(f"\nPrix analytique:    {analytic_result['price']:.4f}")
    print(f"Prix Monte Carlo:   {mc_result['price']:.4f}")
    print(f"Différence:         {abs(analytic_result['price'] - mc_result['price']):.4f}")
    print(f"Erreur relative:    {abs(analytic_result['price'] - mc_result['price'])/analytic_result['price']*100:.2f}%")
    
    print(f"\nTemps analytique:   {analytic_result.get('computation_time_ms', 0):.2f} ms")
    print(f"Temps Monte Carlo:  {mc_result.get('computation_time_ms', 0):.2f} ms")


if __name__ == "__main__":
    try:
        test_health()
        analytic_result = test_analytic_pricing()
        mc_result = test_montecarlo_pricing()
        compare_methods()
        
        print("\n" + "="*60)
        print("✅ TOUS LES TESTS SONT PASSÉS")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERREUR: Impossible de se connecter à l'API")
        print("Assurez-vous que le serveur FastAPI est démarré:")
        print("  python -m uvicorn backend.main:app --reload --port 8000")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
