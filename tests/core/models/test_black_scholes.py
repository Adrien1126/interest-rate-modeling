"""
Tests pour la classe BlackScholesModel.

Ces tests vérifient l'implémentation du modèle Black-Scholes incluant
les simulations, la fonction caractéristique, le pricing analytique et les Greeks.
"""

import pytest
import numpy as np
from backend.core.models.black_scholes import BlackScholesModel


class TestBlackScholesInitialization:
    """Tests pour l'initialisation du modèle Black-Scholes."""
    
    def test_init_with_valid_parameters(self):
        """Test l'initialisation avec des paramètres valides."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        assert model.parameters['volatility'] == 0.2
        assert model.parameters['risk_free_rate'] == 0.05
        assert model.parameters['dividend_yield'] == 0.0
        assert model.name == "Black-Scholes"
    
    def test_init_with_dividend_yield(self):
        """Test l'initialisation avec un taux de dividende."""
        model = BlackScholesModel(volatility=0.25, risk_free_rate=0.03, dividend_yield=0.02)
        assert model.parameters['dividend_yield'] == 0.02
    
    def test_init_with_zero_volatility_raises_error(self):
        """Test qu'une volatilité nulle lève une erreur."""
        with pytest.raises(ValueError, match="volatilité doit être strictement positive"):
            BlackScholesModel(volatility=0.0, risk_free_rate=0.05)
    
    def test_init_with_negative_volatility_raises_error(self):
        """Test qu'une volatilité négative lève une erreur."""
        with pytest.raises(ValueError, match="volatilité doit être strictement positive"):
            BlackScholesModel(volatility=-0.2, risk_free_rate=0.05)
    
    def test_init_with_negative_rate_is_allowed(self):
        """Test que des taux négatifs sont autorisés."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=-0.01)
        assert model.parameters['risk_free_rate'] == -0.01


class TestBlackScholesSimulate:
    """Tests pour la méthode simulate."""
    
    def test_simulate_output_shape(self):
        """Test que simulate retourne la bonne forme."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        paths = model.simulate(S0=100.0, T=1.0, n_steps=252, n_paths=1000)
        assert paths.shape == (1000, 253)
    
    def test_simulate_initial_value(self):
        """Test que toutes les trajectoires commencent à S0."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        S0 = 100.0
        paths = model.simulate(S0=S0, T=1.0, n_steps=100, n_paths=100)
        assert np.allclose(paths[:, 0], S0)
    
    def test_simulate_reproducibility(self):
        """Test que simulate est reproductible avec une graine."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        paths1 = model.simulate(S0=100.0, T=1.0, n_steps=10, n_paths=5, random_seed=42)
        paths2 = model.simulate(S0=100.0, T=1.0, n_steps=10, n_paths=5, random_seed=42)
        assert np.allclose(paths1, paths2)
    
    def test_simulate_with_dividend(self):
        """Test simulation avec dividendes."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05, dividend_yield=0.02)
        paths = model.simulate(S0=100.0, T=1.0, n_steps=100, n_paths=100, random_seed=42)
        assert paths.shape == (100, 101)
        assert paths[0, 0] == 100.0
    
    def test_simulate_positive_paths(self):
        """Test que les trajectoires restent positives."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        paths = model.simulate(S0=100.0, T=1.0, n_steps=100, n_paths=100, random_seed=42)
        assert np.all(paths > 0)


class TestBlackScholesCharacteristicFunction:
    """Tests pour la fonction caractéristique."""
    
    def test_characteristic_function_at_zero(self):
        """Test la fonction caractéristique en u=0."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        result = model.characteristic_function(u=0, t=1.0, S0=100.0)
        # phi(0) = 1
        assert np.isclose(result, 1.0)
    
    def test_characteristic_function_returns_complex(self):
        """Test que la fonction caractéristique retourne un complexe."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        result = model.characteristic_function(u=1.0+2.0j, t=1.0, S0=100.0)
        assert isinstance(result, (complex, np.complexfloating))
    
    def test_characteristic_function_with_dividend(self):
        """Test avec dividendes."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05, dividend_yield=0.02)
        result = model.characteristic_function(u=1.0, t=1.0, S0=100.0)
        assert isinstance(result, (complex, np.complexfloating))


class TestBlackScholesPrice:
    """Tests pour le pricing analytique Black-Scholes."""
    
    def test_price_call_atm(self):
        """Test pricing d'un call ATM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        price = model.black_scholes_price(S=100.0, K=100.0, T=1.0, option_type='call')
        # Prix ATM devrait être > 0
        assert price > 0
        # Approximativement 10.45 pour ces paramètres
        assert 9.0 < price < 12.0
    
    def test_price_put_atm(self):
        """Test pricing d'un put ATM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        price = model.black_scholes_price(S=100.0, K=100.0, T=1.0, option_type='put')
        assert price > 0
        # Approximativement 5.57 pour ces paramètres
        assert 4.0 < price < 7.0
    
    def test_price_call_itm(self):
        """Test pricing d'un call ITM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        price = model.black_scholes_price(S=120.0, K=100.0, T=1.0, option_type='call')
        # ITM call devrait être > valeur intrinsèque
        assert price > 20.0
    
    def test_price_put_itm(self):
        """Test pricing d'un put ITM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        price = model.black_scholes_price(S=80.0, K=100.0, T=1.0, option_type='put')
        # ITM put devrait être > 0 et avoir une valeur temporelle
        # Valeur intrinsèque = 20, mais le prix est environ 17 à cause de l'actualisation
        assert price > 15.0
        assert price < 22.0
    
    def test_price_call_otm(self):
        """Test pricing d'un call OTM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        price = model.black_scholes_price(S=80.0, K=100.0, T=1.0, option_type='call')
        # OTM call devrait être > 0 mais < intrinsèque
        assert price > 0
        assert price < 5.0
    
    def test_price_at_maturity_call(self):
        """Test pricing à maturité (T=0) pour un call."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        price = model.black_scholes_price(S=110.0, K=100.0, T=0.0, option_type='call')
        assert price == 10.0  # Payoff intrinsèque
    
    def test_price_at_maturity_put(self):
        """Test pricing à maturité (T=0) pour un put."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        price = model.black_scholes_price(S=90.0, K=100.0, T=0.0, option_type='put')
        assert price == 10.0
    
    def test_price_invalid_type_raises_error(self):
        """Test qu'un type d'option invalide lève une erreur."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        with pytest.raises(ValueError, match="Type d'option invalide"):
            model.black_scholes_price(S=100.0, K=100.0, T=1.0, option_type='invalid')
    
    def test_put_call_parity(self):
        """Test la parité put-call."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05, dividend_yield=0.0)
        S, K, T = 100.0, 100.0, 1.0
        
        call_price = model.black_scholes_price(S, K, T, 'call')
        put_price = model.black_scholes_price(S, K, T, 'put')
        
        # Put-Call Parity: C - P = S - K*exp(-rT)
        parity_lhs = call_price - put_price
        parity_rhs = S - K * np.exp(-0.05 * T)
        assert np.isclose(parity_lhs, parity_rhs, rtol=1e-10)


class TestBlackScholesGreeks:
    """Tests pour le calcul des Greeks."""
    
    def test_greeks_call_atm(self):
        """Test les Greeks d'un call ATM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        greeks = model.black_scholes_greeks(S=100.0, K=100.0, T=1.0, option_type='call')
        
        # Delta d'un call ATM devrait être proche de 0.5
        assert 0.4 < greeks['delta'] < 0.7
        # Gamma devrait être > 0
        assert greeks['gamma'] > 0
        # Vega devrait être > 0
        assert greeks['vega'] > 0
        # Theta devrait être < 0 (décroissance temporelle)
        assert greeks['theta'] < 0
        # Rho devrait être > 0 pour un call
        assert greeks['rho'] > 0
    
    def test_greeks_put_atm(self):
        """Test les Greeks d'un put ATM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        greeks = model.black_scholes_greeks(S=100.0, K=100.0, T=1.0, option_type='put')
        
        # Delta d'un put ATM devrait être proche de -0.5
        assert -0.7 < greeks['delta'] < -0.3
        # Gamma devrait être > 0
        assert greeks['gamma'] > 0
        # Vega devrait être > 0
        assert greeks['vega'] > 0
        # Theta devrait être < 0
        assert greeks['theta'] < 0
        # Rho devrait être < 0 pour un put
        assert greeks['rho'] < 0
    
    def test_greeks_call_itm_delta(self):
        """Test que delta d'un call ITM approche 1."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        greeks = model.black_scholes_greeks(S=150.0, K=100.0, T=1.0, option_type='call')
        # Delta devrait être proche de 1 pour un call deep ITM
        assert greeks['delta'] > 0.9
    
    def test_greeks_put_itm_delta(self):
        """Test que delta d'un put ITM approche -1."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        greeks = model.black_scholes_greeks(S=50.0, K=100.0, T=1.0, option_type='put')
        # Delta devrait être proche de -1 pour un put deep ITM
        assert greeks['delta'] < -0.9
    
    def test_greeks_at_maturity_are_zero(self):
        """Test que les Greeks sont 0 à maturité."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        greeks = model.black_scholes_greeks(S=100.0, K=100.0, T=0.0, option_type='call')
        
        assert greeks['delta'] == 0.0
        assert greeks['gamma'] == 0.0
        assert greeks['vega'] == 0.0
        assert greeks['theta'] == 0.0
        assert greeks['rho'] == 0.0
    
    def test_greeks_gamma_same_for_call_and_put(self):
        """Test que gamma est identique pour call et put."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        
        call_greeks = model.black_scholes_greeks(S=100.0, K=100.0, T=1.0, option_type='call')
        put_greeks = model.black_scholes_greeks(S=100.0, K=100.0, T=1.0, option_type='put')
        
        assert np.isclose(call_greeks['gamma'], put_greeks['gamma'])
    
    def test_greeks_vega_same_for_call_and_put(self):
        """Test que vega est identique pour call et put."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        
        call_greeks = model.black_scholes_greeks(S=100.0, K=100.0, T=1.0, option_type='call')
        put_greeks = model.black_scholes_greeks(S=100.0, K=100.0, T=1.0, option_type='put')
        
        assert np.isclose(call_greeks['vega'], put_greeks['vega'])


class TestBlackScholesEdgeCases:
    """Tests pour les cas limites."""
    
    def test_very_low_volatility(self):
        """Test avec une volatilité très faible."""
        model = BlackScholesModel(volatility=0.01, risk_free_rate=0.05)
        price = model.black_scholes_price(S=100.0, K=100.0, T=1.0, option_type='call')
        # Prix devrait être proche de la valeur actualisée
        assert price > 0
    
    def test_very_high_volatility(self):
        """Test avec une volatilité très élevée."""
        model = BlackScholesModel(volatility=1.0, risk_free_rate=0.05)
        price = model.black_scholes_price(S=100.0, K=100.0, T=1.0, option_type='call')
        # Prix devrait être significatif
        assert price > 20.0
    
    def test_very_short_maturity(self):
        """Test avec une maturité très courte."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        price = model.black_scholes_price(S=100.0, K=100.0, T=0.01, option_type='call')
        # Prix devrait être proche de 0 pour ATM
        assert 0 < price < 1.0
    
    def test_very_long_maturity(self):
        """Test avec une maturité très longue."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        price = model.black_scholes_price(S=100.0, K=100.0, T=10.0, option_type='call')
        # Prix devrait être significatif
        assert price > 30.0
    
    def test_negative_rates(self):
        """Test avec des taux négatifs."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=-0.01)
        price = model.black_scholes_price(S=100.0, K=100.0, T=1.0, option_type='call')
        assert price > 0


class TestBlackScholesIntegration:
    """Tests d'intégration."""
    
    def test_full_workflow(self):
        """Test un workflow complet."""
        # Créer un modèle
        model = BlackScholesModel(volatility=0.25, risk_free_rate=0.05, dividend_yield=0.02)
        
        # Simuler des trajectoires
        paths = model.simulate(S0=100.0, T=1.0, n_steps=252, n_paths=100, random_seed=42)
        assert paths.shape == (100, 253)
        
        # Pricer une option
        call_price = model.black_scholes_price(S=100.0, K=100.0, T=1.0, option_type='call')
        assert call_price > 0
        
        # Calculer les Greeks
        greeks = model.black_scholes_greeks(S=100.0, K=100.0, T=1.0, option_type='call')
        assert all(key in greeks for key in ['delta', 'gamma', 'vega', 'theta', 'rho'])
    
    def test_get_parameters(self):
        """Test la récupération des paramètres."""
        model = BlackScholesModel(volatility=0.3, risk_free_rate=0.04, dividend_yield=0.01)
        params = model.get_parameters()
        
        assert params['volatility'] == 0.3
        assert params['risk_free_rate'] == 0.04
        assert params['dividend_yield'] == 0.01
    
    def test_set_parameters(self):
        """Test la modification des paramètres."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        
        # Modifier la volatilité
        model.set_parameters({'volatility': 0.3})
        assert model.parameters['volatility'] == 0.3
        
        # Pricing devrait changer
        price1 = model.black_scholes_price(S=100.0, K=100.0, T=1.0, option_type='call')
        
        model.set_parameters({'volatility': 0.4})
        price2 = model.black_scholes_price(S=100.0, K=100.0, T=1.0, option_type='call')
        
        assert price2 > price1  # Plus de volatilité = prix plus élevé
