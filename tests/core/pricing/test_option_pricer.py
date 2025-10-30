"""
Tests pour la classe OptionPricer.

Ces tests vérifient le calcul des Greeks par différences finies.
"""

import pytest
import numpy as np
from backend.core.pricing.option_pricer import OptionPricer
from backend.core.pricing.base_pricer import PricingMethod
from backend.core.models.black_scholes import BlackScholesModel
from backend.core.products.option import Option
from backend.core.products.base_product import OptionType


# Classe concrète pour tester OptionPricer (classe abstraite)
class ConcreteOptionPricer(OptionPricer):
    """Implémentation concrète de OptionPricer pour les tests."""
    
    def price(self, product, spot, **kwargs):
        """Prix simple basé sur Black-Scholes."""
        if isinstance(self.model, BlackScholesModel) and isinstance(product, Option):
            return self.model.black_scholes_price(
                S=spot,
                K=product.strike,
                T=product.maturity,
                option_type=product.option_type.value
            ) * product.notional
        return 0.0


class TestOptionPricerDelta:
    """Tests pour le calcul du delta par différences finies."""
    
    def test_delta_call_atm(self):
        """Test delta d'un call ATM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.CALL)
        
        delta = pricer.delta(option, spot=100.0)
        
        # Delta call ATM devrait être proche de 0.5
        assert 0.4 < delta < 0.7
    
    def test_delta_put_atm(self):
        """Test delta d'un put ATM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.PUT)
        
        delta = pricer.delta(option, spot=100.0)
        
        # Delta put ATM devrait être proche de -0.5
        assert -0.7 < delta < -0.3
    
    def test_delta_call_itm(self):
        """Test delta d'un call deep ITM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.CALL)
        
        delta = pricer.delta(option, spot=150.0)
        
        # Delta devrait être proche de 1
        assert delta > 0.85
    
    def test_delta_put_otm(self):
        """Test delta d'un put OTM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.PUT)
        
        delta = pricer.delta(option, spot=150.0)
        
        # Delta devrait être proche de 0
        assert abs(delta) < 0.15
    
    def test_delta_with_custom_epsilon(self):
        """Test delta avec epsilon personnalisé."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0)
        
        delta1 = pricer.delta(option, spot=100.0, epsilon=0.01)
        delta2 = pricer.delta(option, spot=100.0, epsilon=0.001)
        
        # Devraient être proches
        assert np.isclose(delta1, delta2, rtol=0.05)


class TestOptionPricerGamma:
    """Tests pour le calcul du gamma par différences finies."""
    
    def test_gamma_call_atm(self):
        """Test gamma d'un call ATM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.CALL)
        
        gamma = pricer.gamma(option, spot=100.0)
        
        # Gamma devrait être > 0 et maximal ATM
        assert gamma > 0
        assert gamma > 0.005
    
    def test_gamma_put_atm(self):
        """Test gamma d'un put ATM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.PUT)
        
        gamma = pricer.gamma(option, spot=100.0)
        
        # Gamma devrait être > 0
        assert gamma > 0
    
    def test_gamma_same_for_call_and_put(self):
        """Test que gamma est identique pour call et put."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        
        call = Option(strike=100.0, maturity=1.0, option_type=OptionType.CALL)
        put = Option(strike=100.0, maturity=1.0, option_type=OptionType.PUT)
        
        gamma_call = pricer.gamma(call, spot=100.0)
        gamma_put = pricer.gamma(put, spot=100.0)
        
        # Gamma devrait être identique
        assert np.isclose(gamma_call, gamma_put, rtol=0.01)
    
    def test_gamma_itm_smaller_than_atm(self):
        """Test que gamma ITM < gamma ATM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0)
        
        gamma_atm = pricer.gamma(option, spot=100.0)
        gamma_itm = pricer.gamma(option, spot=120.0)
        
        # Gamma est maximal ATM
        assert gamma_atm > gamma_itm


class TestOptionPricerVega:
    """Tests pour le calcul du vega par différences finies."""
    
    def test_vega_call_atm(self):
        """Test vega d'un call ATM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.CALL)
        
        vega = pricer.vega(option, spot=100.0)
        
        # Vega devrait être > 0
        assert vega > 0
        # Approximativement 0.4 pour ces paramètres
        assert 0.3 < vega < 0.5
    
    def test_vega_put_atm(self):
        """Test vega d'un put ATM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.PUT)
        
        vega = pricer.vega(option, spot=100.0)
        
        assert vega > 0
    
    def test_vega_same_for_call_and_put(self):
        """Test que vega est identique pour call et put."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        
        call = Option(strike=100.0, maturity=1.0, option_type=OptionType.CALL)
        put = Option(strike=100.0, maturity=1.0, option_type=OptionType.PUT)
        
        vega_call = pricer.vega(call, spot=100.0)
        vega_put = pricer.vega(put, spot=100.0)
        
        assert np.isclose(vega_call, vega_put, rtol=0.01)
    
    def test_vega_restores_original_volatility(self):
        """Test que la volatilité originale est restaurée."""
        model = BlackScholesModel(volatility=0.25, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0)
        
        original_vol = model.parameters['volatility']
        pricer.vega(option, spot=100.0)
        
        # Volatilité devrait être restaurée
        assert model.parameters['volatility'] == original_vol


class TestOptionPricerTheta:
    """Tests pour le calcul du theta."""
    
    def test_theta_call_atm(self):
        """Test theta d'un call ATM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.CALL)
        
        theta = pricer.theta(option, spot=100.0)
        
        # Theta devrait être < 0 (décroissance temporelle)
        assert theta < 0
    
    def test_theta_put_atm(self):
        """Test theta d'un put ATM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.PUT)
        
        theta = pricer.theta(option, spot=100.0)
        
        assert theta < 0
    
    def test_theta_restores_original_maturity(self):
        """Test que la maturité originale est restaurée."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0)
        
        original_maturity = option.maturity
        pricer.theta(option, spot=100.0)
        
        # Maturité devrait être restaurée
        assert option.maturity == original_maturity
    
    def test_theta_with_custom_dt(self):
        """Test theta avec dt personnalisé."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0)
        
        theta_day = pricer.theta(option, spot=100.0, dt=1/365)
        theta_week = pricer.theta(option, spot=100.0, dt=7/365)
        
        # Les deux devraient être négatifs et comparables
        assert theta_day < 0
        assert theta_week < 0
        # Theta est approximativement linéaire en dt pour petites variations
        assert np.isclose(theta_week / theta_day, 1.0, rtol=0.2)


class TestOptionPricerRho:
    """Tests pour le calcul du rho."""
    
    def test_rho_call_atm(self):
        """Test rho d'un call ATM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.CALL)
        
        rho = pricer.rho(option, spot=100.0)
        
        # Rho call devrait être > 0
        assert rho > 0
        # Approximativement 0.5 pour ces paramètres
        assert 0.3 < rho < 0.7
    
    def test_rho_put_atm(self):
        """Test rho d'un put ATM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.PUT)
        
        rho = pricer.rho(option, spot=100.0)
        
        # Rho put devrait être < 0
        assert rho < 0
    
    def test_rho_restores_original_rate(self):
        """Test que le taux original est restauré."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0)
        
        original_rate = model.parameters['risk_free_rate']
        pricer.rho(option, spot=100.0)
        
        # Taux devrait être restauré
        assert model.parameters['risk_free_rate'] == original_rate


class TestOptionPricerGreeks:
    """Tests pour la méthode greeks (tous les Greeks ensemble)."""
    
    def test_greeks_returns_all_greeks(self):
        """Test que greeks() retourne tous les Greeks."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0)
        
        greeks = pricer.greeks(option, spot=100.0)
        
        # Vérifier que tous les Greeks sont présents
        assert 'delta' in greeks
        assert 'gamma' in greeks
        assert 'vega' in greeks
        assert 'theta' in greeks
        assert 'rho' in greeks
    
    def test_greeks_call_signs(self):
        """Test les signes des Greeks pour un call."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.CALL)
        
        greeks = pricer.greeks(option, spot=100.0)
        
        assert greeks['delta'] > 0
        assert greeks['gamma'] > 0
        assert greeks['vega'] > 0
        assert greeks['theta'] < 0
        assert greeks['rho'] > 0
    
    def test_greeks_put_signs(self):
        """Test les signes des Greeks pour un put."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.PUT)
        
        greeks = pricer.greeks(option, spot=100.0)
        
        assert greeks['delta'] < 0
        assert greeks['gamma'] > 0
        assert greeks['vega'] > 0
        assert greeks['theta'] < 0
        assert greeks['rho'] < 0


class TestOptionPricerEdgeCases:
    """Tests pour les cas limites."""
    
    def test_greeks_short_maturity(self):
        """Test Greeks avec maturité très courte."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=0.01)  # ~4 jours
        
        greeks = pricer.greeks(option, spot=100.0)
        
        # Devrait retourner des valeurs sans erreur
        assert all(isinstance(v, (int, float)) for v in greeks.values())
    
    def test_greeks_long_maturity(self):
        """Test Greeks avec maturité très longue."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=10.0)
        
        greeks = pricer.greeks(option, spot=100.0)
        
        assert all(isinstance(v, (int, float)) for v in greeks.values())
    
    def test_greeks_deep_itm_call(self):
        """Test Greeks pour call deep ITM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.CALL)
        
        greeks = pricer.greeks(option, spot=200.0)
        
        # Delta devrait être proche de 1
        assert greeks['delta'] > 0.95
        # Gamma devrait être petit
        assert greeks['gamma'] < 0.01
    
    def test_greeks_deep_otm_put(self):
        """Test Greeks pour put deep OTM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.PUT)
        
        greeks = pricer.greeks(option, spot=200.0)
        
        # Delta devrait être proche de 0
        assert abs(greeks['delta']) < 0.05


class TestOptionPricerIntegration:
    """Tests d'intégration."""
    
    def test_full_workflow(self):
        """Test un workflow complet."""
        # Créer le modèle
        model = BlackScholesModel(volatility=0.25, risk_free_rate=0.05, dividend_yield=0.02)
        
        # Créer le pricer
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        
        # Créer l'option
        option = Option(
            strike=100.0,
            maturity=1.0,
            option_type=OptionType.CALL,
            notional=100.0
        )
        
        # Calculer tous les Greeks
        greeks = pricer.greeks(option, spot=105.0)
        
        # Vérifier qu'on a tous les Greeks
        assert len(greeks) == 5
        assert all(k in greeks for k in ['delta', 'gamma', 'vega', 'theta', 'rho'])
        
        # Vérifier les valeurs
        assert greeks['delta'] > 0.5  # Call ITM
        assert greeks['gamma'] > 0
    
    def test_greeks_consistency_with_multiple_calls(self):
        """Test que les Greeks sont cohérents sur plusieurs appels."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0)
        
        greeks1 = pricer.greeks(option, spot=100.0)
        greeks2 = pricer.greeks(option, spot=100.0)
        
        # Devraient être identiques
        for key in greeks1:
            assert np.isclose(greeks1[key], greeks2[key])
    
    def test_different_spots_different_greeks(self):
        """Test que différents spots donnent différents Greeks."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = ConcreteOptionPricer(model, PricingMethod.ANALYTIC)
        option = Option(strike=100.0, maturity=1.0)
        
        greeks_90 = pricer.greeks(option, spot=90.0)
        greeks_110 = pricer.greeks(option, spot=110.0)
        
        # Delta devrait être différent
        assert abs(greeks_90['delta'] - greeks_110['delta']) > 0.1
