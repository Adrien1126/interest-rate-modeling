#!/usr/bin/env python3
"""
Script de test pour valider le Monte Carlo avec différentes configurations.
"""

import requests
import json
import time
from datetime import date, timedelta

BASE_URL = "http://localhost:8000/api/pricing/option"

def test_scenario(name, config):
    """Teste un scénario de pricing."""
    print(f"\n{'='*80}")
    print(f"🧪 TEST: {name}")
    print(f"{'='*80}")
    
    # Configuration de base
    today = date.today().isoformat()
    expiration = (date.today() + timedelta(days=365)).isoformat()
    
    payload = {
        "trade": {
            "trade_id": f"TEST-{int(time.time())}",
            "trade_date": today,
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
                "expiration_date": expiration,
                "notional": {"amount": 1.0, "currency": "USD"},
                "settlement": {"settlement_type": "Cash"}
            },
            "parties": {
                "buyer": {"id": "test", "name": "Test"},
                "seller": {"id": "market", "name": "Market"}
            }
        },
        "spot_price": 100.0,
        "valuation_date": today,
        "market_conventions": {
            "day_count_convention": "ACT/365",
            "business_day_convention": "ModifiedFollowing",
            "calendar": "TARGET"
        },
        "model_type": "BlackScholes",
        "volatility": 0.2,
        "risk_free_rate": 0.05,
        "dividend_yield": 0.0,
        "pricing_method": config.get("method", "monte_carlo"),
        "compute_greeks": True,
        "compute_implied_vol": False,
    }
    
    # Ajouter les paramètres spécifiques au scénario
    payload.update(config.get("params", {}))
    
    print(f"\n📋 Configuration:")
    for key, value in config.get("params", {}).items():
        print(f"  • {key}: {value}")
    
    # Appel API
    start_time = time.time()
    try:
        response = requests.post(BASE_URL, json=payload, timeout=120)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ SUCCÈS (temps: {elapsed_time:.2f}s)")
            print(f"\n📊 Résultats:")
            print(f"  • Prix: {result['price']:.4f} USD")
            print(f"  • Temps de calcul: {result.get('computation_time_ms', 0):.2f} ms")
            
            if result.get('greeks'):
                print(f"\n  Greeks:")
                print(f"    - Delta: {result['greeks']['delta']:.4f}")
                print(f"    - Gamma: {result['greeks']['gamma']:.4f}")
                print(f"    - Vega:  {result['greeks']['vega']:.4f}")
                print(f"    - Theta: {result['greeks']['theta']:.4f}")
                print(f"    - Rho:   {result['greeks']['rho']:.4f}")
            
            if result.get('confidence_interval'):
                ci = result['confidence_interval']
                print(f"\n  Intervalle de confiance:")
                print(f"    - Niveau: {ci.get('confidence_level', 0.95)*100:.0f}%")
                print(f"    - Borne inf: {ci.get('lower_bound', 0):.4f}")
                print(f"    - Prix:      {ci.get('price', 0):.4f}")
                print(f"    - Borne sup: {ci.get('upper_bound', 0):.4f}")
                print(f"    - Erreur std: {ci.get('std_error', 0):.4f}")
            
            return True
            
        else:
            print(f"\n❌ ERREUR HTTP {response.status_code}")
            print(f"Temps: {elapsed_time:.2f}s")
            print(f"Détails: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n⏱️ TIMEOUT après {time.time() - start_time:.2f}s")
        return False
    except Exception as e:
        print(f"\n💥 EXCEPTION: {str(e)}")
        return False


def main():
    """Exécute tous les scénarios de test."""
    
    print("\n" + "🚀 " * 20)
    print("TESTS MONTE CARLO - DIFFÉRENTES CONFIGURATIONS")
    print("🚀 " * 20)
    
    scenarios = [
        {
            "name": "Scénario 1: Configuration minimale (rapide)",
            "config": {
                "method": "monte_carlo",
                "params": {
                    "n_simulations": 100,
                    "n_steps": 10,
                    "use_antithetic": False,
                    "random_seed": 42,
                    "compute_confidence_interval": True,
                    "confidence_level": 0.95
                }
            }
        },
        {
            "name": "Scénario 2: Configuration standard",
            "config": {
                "method": "monte_carlo",
                "params": {
                    "n_simulations": 10000,
                    "n_steps": 100,
                    "use_antithetic": True,
                    "random_seed": 42,
                    "compute_confidence_interval": True,
                    "confidence_level": 0.95
                }
            }
        },
        {
            "name": "Scénario 3: Haute précision (lent)",
            "config": {
                "method": "monte_carlo",
                "params": {
                    "n_simulations": 100000,
                    "n_steps": 252,
                    "use_antithetic": True,
                    "random_seed": 42,
                    "compute_confidence_interval": True,
                    "confidence_level": 0.99
                }
            }
        },
        {
            "name": "Scénario 4: Sans antithétiques",
            "config": {
                "method": "monte_carlo",
                "params": {
                    "n_simulations": 50000,
                    "n_steps": 100,
                    "use_antithetic": False,
                    "random_seed": 42,
                    "compute_confidence_interval": True,
                    "confidence_level": 0.95
                }
            }
        },
        {
            "name": "Scénario 5: Seed aléatoire (non reproductible)",
            "config": {
                "method": "monte_carlo",
                "params": {
                    "n_simulations": 10000,
                    "n_steps": 100,
                    "use_antithetic": True,
                    "random_seed": None,
                    "compute_confidence_interval": True,
                    "confidence_level": 0.95
                }
            }
        },
        {
            "name": "Scénario 6: Intervalle de confiance 90%",
            "config": {
                "method": "monte_carlo",
                "params": {
                    "n_simulations": 20000,
                    "n_steps": 100,
                    "use_antithetic": True,
                    "random_seed": 42,
                    "compute_confidence_interval": True,
                    "confidence_level": 0.90
                }
            }
        },
        {
            "name": "COMPARAISON: Méthode Analytique",
            "config": {
                "method": "analytic",
                "params": {}
            }
        }
    ]
    
    results = []
    for scenario in scenarios:
        success = test_scenario(scenario["name"], scenario["config"])
        results.append((scenario["name"], success))
        time.sleep(0.5)  # Petite pause entre les tests
    
    # Résumé final
    print("\n" + "="*80)
    print("📋 RÉSUMÉ DES TESTS")
    print("="*80)
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{'='*80}")
    print(f"TOTAL: {success_count}/{total_count} tests réussis ({success_count/total_count*100:.0f}%)")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
