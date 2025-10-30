"""
Tests pour les pricers analytiques (AnalyticPricer et AnalyticOptionPricer).

Ces tests vérifient le pricing analytique avec Black-Scholes,
le calcul des Greeks et la volatilité implicite.
"""

import pytest
import numpy as np
from backend.core.pricing.analytic_pricer import AnalyticPricer, AnalyticOptionPricer
from backend.core.models.black_scholes import BlackScholesModel
from backend.core.products.option import Option
from backend.core.products.base_product import OptionType, ExerciseType, ProductType
from backend.core.pricing.base_pricer import PricingMethod


class TestAnalyticPricerInitialization:
    """Tests pour l'initialisation de AnalyticPricer."""
    
    def test_init_with_black_scholes(self):
        """Test l'initialisation avec Black-Scholes."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = AnalyticPricer(model)
        
        assert pricer.model == model
        assert pricer.method == PricingMethod.ANALYTIC
    
    def test_init_sets_analytic_method(self):
        """Test que la méthode est toujours ANALYTIC."""
        model = BlackScholesModel(volatility=0.25, risk_free_rate=0.03)
        pricer = AnalyticPricer(model)
        
        assert pricer.method == PricingMethod.ANALYTIC


class TestAnalyticPricerPrice:
    """Tests pour le pricing avec AnalyticPricer."""
    
    def test_price_call_option(self):
        """Test pricing d'un call avec Black-Scholes."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = AnalyticPricer(model)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.CALL)
        
        price = pricer.price(option, spot=100.0)
        
        # Prix devrait être > 0
        assert price > 0
        # Approximativement 10.45 pour ces paramètres
        assert 9.0 < price < 12.0
    
    def test_price_put_option(self):
        """Test pricing d'un put avec Black-Scholes."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = AnalyticPricer(model)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.PUT)
        
        price = pricer.price(option, spot=100.0)
        
        assert price > 0
        assert 4.0 < price < 7.0
    
    def test_price_with_notional(self):
        """Test que le prix est multiplié par le notionnel."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = AnalyticPricer(model)
        
        option1 = Option(strike=100.0, maturity=1.0, notional=1.0)
        option2 = Option(strike=100.0, maturity=1.0, notional=100.0)
        
        price1 = pricer.price(option1, spot=100.0)
        price2 = pricer.price(option2, spot=100.0)
        
        assert np.isclose(price2, price1 * 100.0)
    
    def test_price_itm_call(self):
        """Test pricing d'un call ITM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = AnalyticPricer(model)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.CALL)
        
        price = pricer.price(option, spot=120.0)
        
        # Prix devrait être > valeur intrinsèque (20)
        assert price > 20.0
    
    def test_price_otm_put(self):
        """Test pricing d'un put OTM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = AnalyticPricer(model)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.PUT)
        
        price = pricer.price(option, spot=120.0)
        
        # Prix devrait être > 0 mais petit
        assert 0 < price < 5.0
    
    def test_price_non_option_raises_error(self):
        """Test qu'un produit non-option lève une erreur."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = AnalyticPricer(model)
        
        # Créer un produit factice qui n'est pas une Option
        from backend.core.products.base_product import BaseProduct
        
        class FakeProduct(BaseProduct):
            def payoff(self, spot_price, **kwargs):
                return spot_price
            
            def get_characteristics(self):
                return {}
        
        fake = FakeProduct(ProductType.SWAP, maturity=1.0)
        
        with pytest.raises(NotImplementedError, match="Pas de formule analytique"):
            pricer.price(fake, spot=100.0)


class TestAnalyticPricerRepr:
    """Tests pour __repr__."""
    
    def test_repr(self):
        """Test __repr__."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = AnalyticPricer(model)
        
        repr_str = repr(pricer)
        assert "AnalyticPricer" in repr_str
        assert "Black-Scholes" in repr_str


class TestAnalyticOptionPricerGreeks:
    """Tests pour le calcul des Greeks avec AnalyticOptionPricer."""
    
    def test_greeks_call_atm(self):
        """Test les Greeks d'un call ATM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = AnalyticOptionPricer(model)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.CALL)
        
        greeks = pricer.greeks(option, spot=100.0)
        
        # Vérifier que tous les Greeks sont présents
        assert 'delta' in greeks
        assert 'gamma' in greeks
        assert 'vega' in greeks
        assert 'theta' in greeks
        assert 'rho' in greeks
        
        # Vérifier les signes
        assert 0.4 < greeks['delta'] < 0.7  # Delta call ATM ~ 0.5
        assert greeks['gamma'] > 0
        assert greeks['vega'] > 0
        assert greeks['theta'] < 0
        assert greeks['rho'] > 0
    
    def test_greeks_put_atm(self):
        """Test les Greeks d'un put ATM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = AnalyticOptionPricer(model)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.PUT)
        
        greeks = pricer.greeks(option, spot=100.0)
        
        assert -0.7 < greeks['delta'] < -0.3
        assert greeks['gamma'] > 0
        assert greeks['vega'] > 0
        assert greeks['theta'] < 0
        assert greeks['rho'] < 0
    
    def test_greeks_with_notional(self):
        """Test que les Greeks sont multipliés par le notionnel."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = AnalyticOptionPricer(model)
        
        option1 = Option(strike=100.0, maturity=1.0, notional=1.0)
        option2 = Option(strike=100.0, maturity=1.0, notional=10.0)
        
        greeks1 = pricer.greeks(option1, spot=100.0)
        greeks2 = pricer.greeks(option2, spot=100.0)
        
        for key in greeks1:
            assert np.isclose(greeks2[key], greeks1[key] * 10.0)
    
    def test_greeks_call_itm(self):
        """Test Greeks d'un call deep ITM."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = AnalyticOptionPricer(model)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.CALL)
        
        greeks = pricer.greeks(option, spot=150.0)
        
        # Delta devrait être proche de 1
        assert greeks['delta'] > 0.9


class TestAnalyticOptionPricerImpliedVolatility:
    """Tests pour le calcul de la volatilité implicite."""
    
    def test_implied_vol_recovers_input_vol(self):
        """Test que la vol implicite retrouve la vol du modèle."""
        model = BlackScholesModel(volatility=0.25, risk_free_rate=0.05)
        pricer = AnalyticOptionPricer(model)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.CALL)
        
        # Calculer le prix avec vol=0.25
        market_price = pricer.price(option, spot=100.0)
        
        # Calculer la vol implicite
        implied_vol = pricer.implied_volatility(
            option, spot=100.0, market_price=market_price, initial_guess=0.2
        )
        
        # Devrait retrouver 0.25
        assert implied_vol is not None
        assert np.isclose(implied_vol, 0.25, atol=1e-4)
    
    def test_implied_vol_different_strikes(self):
        """Test la vol implicite pour différents strikes."""
        model = BlackScholesModel(volatility=0.3, risk_free_rate=0.05)
        pricer = AnalyticOptionPricer(model)
        
        for strike in [80.0, 100.0, 120.0]:
            option = Option(strike=strike, maturity=1.0, option_type=OptionType.CALL)
            market_price = pricer.price(option, spot=100.0)
            
            implied_vol = pricer.implied_volatility(
                option, spot=100.0, market_price=market_price
            )
            
            assert implied_vol is not None
            assert np.isclose(implied_vol, 0.3, atol=1e-4)
    
    def test_implied_vol_put(self):
        """Test la vol implicite pour un put."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = AnalyticOptionPricer(model)
        option = Option(strike=100.0, maturity=1.0, option_type=OptionType.PUT)
        
        market_price = pricer.price(option, spot=100.0)
        implied_vol = pricer.implied_volatility(option, spot=100.0, market_price=market_price)
        
        assert implied_vol is not None
        assert np.isclose(implied_vol, 0.2, atol=1e-4)
    
    def test_implied_vol_with_custom_tolerance(self):
        """Test avec une tolérance personnalisée."""
        model = BlackScholesModel(volatility=0.25, risk_free_rate=0.05)
        pricer = AnalyticOptionPricer(model)
        option = Option(strike=100.0, maturity=1.0)
        
        market_price = pricer.price(option, spot=100.0)
        implied_vol = pricer.implied_volatility(
            option, spot=100.0, market_price=market_price, tolerance=1e-8
        )
        
        assert implied_vol is not None
        assert np.isclose(implied_vol, 0.25, atol=1e-6)
    
    def test_implied_vol_restores_original_vol(self):
        """Test que la volatilité originale est restaurée."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = AnalyticOptionPricer(model)
        option = Option(strike=100.0, maturity=1.0)
        
        market_price = pricer.price(option, spot=100.0)
        
        # Volatilité avant
        vol_before = model.parameters['volatility']
        
        # Calculer la vol implicite
        pricer.implied_volatility(option, spot=100.0, market_price=market_price)
        
        # Volatilité après devrait être identique
        vol_after = model.parameters['volatility']
        assert vol_before == vol_after
    
    def test_implied_vol_no_convergence(self):
        """Test qu'aucune convergence retourne None."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = AnalyticOptionPricer(model)
        option = Option(strike=100.0, maturity=1.0)
        
        # Prix de marché irréaliste
        implied_vol = pricer.implied_volatility(
            option, spot=100.0, market_price=1000.0, max_iterations=5
        )
        
        # Pas de convergence avec 5 itérations et prix irréaliste
        assert implied_vol is None or implied_vol > 5.0
    
    def test_implied_vol_zero_vega_case(self):
        """Test le cas où vega est très petit."""
        model = BlackScholesModel(volatility=0.001, risk_free_rate=0.05)
        pricer = AnalyticOptionPricer(model)
        option = Option(strike=100.0, maturity=0.001)  # Très courte maturité
        
        market_price = pricer.price(option, spot=100.0)
        
        # Peut retourner None si vega trop petit
        implied_vol = pricer.implied_volatility(
            option, spot=100.0, market_price=market_price, initial_guess=0.001
        )
        # On vérifie juste qu'il n'y a pas d'erreur
        assert implied_vol is None or implied_vol > 0


class TestAnalyticOptionPricerRepr:
    """Tests pour __repr__."""
    
    def test_repr(self):
        """Test __repr__."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = AnalyticOptionPricer(model)
        
        repr_str = repr(pricer)
        assert "AnalyticOptionPricer" in repr_str
        assert "Black-Scholes" in repr_str


class TestAnalyticPricerIntegration:
    """Tests d'intégration."""
    
    def test_full_workflow_call(self):
        """Test un workflow complet pour un call."""
        # Créer le modèle
        model = BlackScholesModel(volatility=0.25, risk_free_rate=0.05, dividend_yield=0.02)
        
        # Créer le pricer
        pricer = AnalyticOptionPricer(model)
        
        # Créer l'option
        option = Option(
            strike=100.0,
            maturity=1.0,
            option_type=OptionType.CALL,
            notional=100.0
        )
        
        # Pricer
        price = pricer.price(option, spot=105.0)
        assert price > 0
        
        # Greeks
        greeks = pricer.greeks(option, spot=105.0)
        assert greeks['delta'] > 0.5  # Call ITM
        
        # Vol implicite
        impl_vol = pricer.implied_volatility(option, spot=105.0, market_price=price)
        assert np.isclose(impl_vol, 0.25, atol=1e-4)
    
    def test_full_workflow_put(self):
        """Test un workflow complet pour un put."""
        model = BlackScholesModel(volatility=0.3, risk_free_rate=0.04)
        pricer = AnalyticOptionPricer(model)
        option = Option(strike=100.0, maturity=2.0, option_type=OptionType.PUT, notional=50.0)
        
        price = pricer.price(option, spot=95.0)
        greeks = pricer.greeks(option, spot=95.0)
        impl_vol = pricer.implied_volatility(option, spot=95.0, market_price=price)
        
        assert price > 0
        assert greeks['delta'] < 0  # Put a delta négatif
        assert np.isclose(impl_vol, 0.3, atol=1e-4)
    
    def test_pricing_info(self):
        """Test get_pricing_info."""
        model = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        pricer = AnalyticPricer(model)
        
        info = pricer.get_pricing_info()
        assert info['method'] == 'analytic'
        assert info['model'] == 'Black-Scholes'
        assert info['model_parameters']['volatility'] == 0.2
    
    def test_different_models_same_option(self):
        """Test le même option avec différents modèles."""
        model1 = BlackScholesModel(volatility=0.2, risk_free_rate=0.05)
        model2 = BlackScholesModel(volatility=0.3, risk_free_rate=0.05)
        
        pricer1 = AnalyticPricer(model1)
        pricer2 = AnalyticPricer(model2)
        
        option = Option(strike=100.0, maturity=1.0)
        
        price1 = pricer1.price(option, spot=100.0)
        price2 = pricer2.price(option, spot=100.0)
        
        # Plus de volatilité = prix plus élevé
        assert price2 > price1
