"""
Tests pour la classe BasePricer et l'énumération PricingMethod.

Ces tests vérifient le comportement de la classe abstraite BasePricer
et de l'énumération PricingMethod.
"""

import pytest
from backend.core.pricing.base_pricer import BasePricer, PricingMethod
from backend.core.models.base_model import BaseModel
from backend.core.products.base_product import BaseProduct, ProductType
import numpy as np


# Classes concrètes pour les tests
class ConcreteModel(BaseModel):
    """Modèle concret pour les tests."""
    
    def _validate_parameters(self):
        pass
    
    def simulate(self, S0, T, n_steps, n_paths, random_seed=None):
        return np.zeros((n_paths, n_steps + 1))
    
    def characteristic_function(self, u, t, **kwargs):
        return complex(1.0, 0.0)


class ConcreteProduct(BaseProduct):
    """Produit concret pour les tests."""
    
    def payoff(self, spot_price, **kwargs):
        return spot_price * self.notional
    
    def get_characteristics(self):
        return {
            'product_type': self.product_type.value,
            'maturity': self.maturity
        }


class ConcretePricer(BasePricer):
    """Pricer concret pour les tests."""
    
    def price(self, product, spot, **kwargs):
        """Prix simple basé sur le payoff."""
        return product.payoff(spot)


class TestPricingMethod:
    """Tests pour l'énumération PricingMethod."""
    
    def test_all_pricing_methods_exist(self):
        """Vérifie que toutes les méthodes de pricing sont définies."""
        assert PricingMethod.ANALYTIC.value == "analytic"
        assert PricingMethod.MONTE_CARLO.value == "monte_carlo"
        assert PricingMethod.BINOMIAL_TREE.value == "binomial_tree"
        assert PricingMethod.TRINOMIAL_TREE.value == "trinomial_tree"
        assert PricingMethod.FINITE_DIFFERENCE.value == "finite_difference"
        assert PricingMethod.FOURIER.value == "fourier"
    
    def test_pricing_method_comparison(self):
        """Test la comparaison de méthodes de pricing."""
        assert PricingMethod.ANALYTIC == PricingMethod.ANALYTIC
        assert PricingMethod.ANALYTIC != PricingMethod.MONTE_CARLO
    
    def test_pricing_method_from_string(self):
        """Test la création depuis une string."""
        assert PricingMethod("analytic") == PricingMethod.ANALYTIC
        assert PricingMethod("monte_carlo") == PricingMethod.MONTE_CARLO
        assert PricingMethod("fourier") == PricingMethod.FOURIER
    
    def test_pricing_method_invalid_raises_error(self):
        """Test qu'une valeur invalide lève une erreur."""
        with pytest.raises(ValueError):
            PricingMethod("invalid_method")


class TestBasePricerInitialization:
    """Tests pour l'initialisation de BasePricer."""
    
    def test_init_with_valid_parameters(self):
        """Test l'initialisation avec des paramètres valides."""
        model = ConcreteModel("TestModel", {"param1": 1.0})
        pricer = ConcretePricer(model, PricingMethod.ANALYTIC)
        
        assert pricer.model == model
        assert pricer.method == PricingMethod.ANALYTIC
    
    def test_init_with_different_methods(self):
        """Test l'initialisation avec différentes méthodes."""
        model = ConcreteModel("TestModel")
        
        for method in PricingMethod:
            pricer = ConcretePricer(model, method)
            assert pricer.method == method
    
    def test_init_with_different_models(self):
        """Test l'initialisation avec différents modèles."""
        model1 = ConcreteModel("Model1", {"param1": 1.0})
        model2 = ConcreteModel("Model2", {"param1": 2.0})
        
        pricer1 = ConcretePricer(model1, PricingMethod.ANALYTIC)
        pricer2 = ConcretePricer(model2, PricingMethod.MONTE_CARLO)
        
        assert pricer1.model.name == "Model1"
        assert pricer2.model.name == "Model2"


class TestBasePricerPrice:
    """Tests pour la méthode price (implémentation concrète)."""
    
    def test_price_simple_product(self):
        """Test le pricing d'un produit simple."""
        model = ConcreteModel("TestModel")
        pricer = ConcretePricer(model, PricingMethod.ANALYTIC)
        product = ConcreteProduct(ProductType.OPTION, maturity=1.0, notional=10.0)
        
        price = pricer.price(product, spot=100.0)
        assert price == 1000.0  # 100 * 10
    
    def test_price_with_different_spots(self):
        """Test le pricing avec différents spots."""
        model = ConcreteModel("TestModel")
        pricer = ConcretePricer(model, PricingMethod.ANALYTIC)
        product = ConcreteProduct(ProductType.OPTION, maturity=1.0, notional=1.0)
        
        assert pricer.price(product, spot=50.0) == 50.0
        assert pricer.price(product, spot=100.0) == 100.0
        assert pricer.price(product, spot=200.0) == 200.0
    
    def test_price_with_kwargs(self):
        """Test le pricing avec des kwargs additionnels."""
        model = ConcreteModel("TestModel")
        pricer = ConcretePricer(model, PricingMethod.MONTE_CARLO)
        product = ConcreteProduct(ProductType.SWAP, maturity=5.0, notional=100.0)
        
        # Les kwargs sont acceptés mais pas utilisés dans notre implémentation simple
        price = pricer.price(product, spot=100.0, vol=0.2, rate=0.05)
        assert price == 10000.0


class TestBasePricerGetPricingInfo:
    """Tests pour la méthode get_pricing_info."""
    
    def test_get_pricing_info_returns_dict(self):
        """Test que get_pricing_info retourne un dictionnaire."""
        model = ConcreteModel("BlackScholes", {"sigma": 0.2, "r": 0.05})
        pricer = ConcretePricer(model, PricingMethod.ANALYTIC)
        
        info = pricer.get_pricing_info()
        
        assert isinstance(info, dict)
        assert info['method'] == 'analytic'
        assert info['model'] == 'BlackScholes'
        assert info['model_parameters'] == {'sigma': 0.2, 'r': 0.05}
    
    def test_get_pricing_info_different_methods(self):
        """Test get_pricing_info avec différentes méthodes."""
        model = ConcreteModel("TestModel")
        
        for method in [PricingMethod.ANALYTIC, PricingMethod.MONTE_CARLO, PricingMethod.FOURIER]:
            pricer = ConcretePricer(model, method)
            info = pricer.get_pricing_info()
            assert info['method'] == method.value
    
    def test_get_pricing_info_includes_model_params(self):
        """Test que get_pricing_info inclut les paramètres du modèle."""
        params = {"vol": 0.25, "rate": 0.03, "dividend": 0.01}
        model = ConcreteModel("Heston", params)
        pricer = ConcretePricer(model, PricingMethod.FOURIER)
        
        info = pricer.get_pricing_info()
        assert info['model_parameters'] == params
    
    def test_get_pricing_info_empty_parameters(self):
        """Test get_pricing_info avec un modèle sans paramètres."""
        model = ConcreteModel("SimpleModel")
        pricer = ConcretePricer(model, PricingMethod.ANALYTIC)
        
        info = pricer.get_pricing_info()
        assert info['model_parameters'] == {}


class TestBasePricerStringRepresentations:
    """Tests pour __repr__ et __str__."""
    
    def test_repr_contains_class_info(self):
        """Test que __repr__ contient les informations de la classe."""
        model = ConcreteModel("BlackScholes")
        pricer = ConcretePricer(model, PricingMethod.ANALYTIC)
        
        repr_str = repr(pricer)
        assert "ConcretePricer" in repr_str
        assert "model=BlackScholes" in repr_str
        assert "method=analytic" in repr_str
    
    def test_repr_different_methods(self):
        """Test __repr__ avec différentes méthodes."""
        model = ConcreteModel("TestModel")
        
        pricer_mc = ConcretePricer(model, PricingMethod.MONTE_CARLO)
        repr_mc = repr(pricer_mc)
        assert "method=monte_carlo" in repr_mc
        
        pricer_tree = ConcretePricer(model, PricingMethod.BINOMIAL_TREE)
        repr_tree = repr(pricer_tree)
        assert "method=binomial_tree" in repr_tree
    
    def test_str_readable_format(self):
        """Test que __str__ produit un format lisible."""
        model = ConcreteModel("Heston")
        pricer = ConcretePricer(model, PricingMethod.FOURIER)
        
        str_repr = str(pricer)
        assert "Fourier" in str_repr
        assert "Heston" in str_repr
    
    def test_str_different_combinations(self):
        """Test __str__ avec différentes combinaisons."""
        model1 = ConcreteModel("BlackScholes")
        pricer1 = ConcretePricer(model1, PricingMethod.ANALYTIC)
        assert "Analytic" in str(pricer1)
        assert "BlackScholes" in str(pricer1)
        
        model2 = ConcreteModel("HullWhite")
        pricer2 = ConcretePricer(model2, PricingMethod.MONTE_CARLO)
        assert "Monte_carlo" in str(pricer2)
        assert "HullWhite" in str(pricer2)


class TestBasePricerAbstractMethods:
    """Tests pour vérifier que les méthodes abstraites doivent être implémentées."""
    
    def test_cannot_instantiate_base_pricer(self):
        """Test qu'on ne peut pas instancier BasePricer directement."""
        model = ConcreteModel("TestModel")
        
        with pytest.raises(TypeError):
            BasePricer(model, PricingMethod.ANALYTIC)
    
    def test_concrete_pricer_must_implement_price(self):
        """Test qu'une classe concrète doit implémenter price."""
        
        # Classe incomplète (manque price)
        class IncompletePricer(BasePricer):
            pass
        
        model = ConcreteModel("TestModel")
        with pytest.raises(TypeError):
            IncompletePricer(model, PricingMethod.ANALYTIC)


class TestBasePricerEdgeCases:
    """Tests pour les cas limites."""
    
    def test_pricer_with_model_no_parameters(self):
        """Test pricer avec un modèle sans paramètres."""
        model = ConcreteModel("SimpleModel")
        pricer = ConcretePricer(model, PricingMethod.ANALYTIC)
        
        assert pricer.model.get_parameters() == {}
        info = pricer.get_pricing_info()
        assert info['model_parameters'] == {}
    
    def test_pricer_with_model_many_parameters(self):
        """Test pricer avec un modèle ayant beaucoup de paramètres."""
        params = {f"param{i}": float(i) for i in range(10)}
        model = ConcreteModel("ComplexModel", params)
        pricer = ConcretePricer(model, PricingMethod.FINITE_DIFFERENCE)
        
        info = pricer.get_pricing_info()
        assert len(info['model_parameters']) == 10
    
    def test_price_with_zero_spot(self):
        """Test pricing avec spot = 0."""
        model = ConcreteModel("TestModel")
        pricer = ConcretePricer(model, PricingMethod.ANALYTIC)
        product = ConcreteProduct(ProductType.OPTION, maturity=1.0, notional=100.0)
        
        price = pricer.price(product, spot=0.0)
        assert price == 0.0
    
    def test_price_with_very_large_spot(self):
        """Test pricing avec un spot très grand."""
        model = ConcreteModel("TestModel")
        pricer = ConcretePricer(model, PricingMethod.ANALYTIC)
        product = ConcreteProduct(ProductType.OPTION, maturity=1.0, notional=1.0)
        
        large_spot = 1e10
        price = pricer.price(product, spot=large_spot)
        assert price == large_spot


class TestBasePricerIntegration:
    """Tests d'intégration pour vérifier le comportement global."""
    
    def test_full_workflow(self):
        """Test un workflow complet de pricing."""
        # Créer un modèle
        model = ConcreteModel("BlackScholes", {"vol": 0.2, "rate": 0.05})
        
        # Créer un pricer
        pricer = ConcretePricer(model, PricingMethod.ANALYTIC)
        
        # Créer un produit
        product = ConcreteProduct(ProductType.OPTION, maturity=1.0, notional=100.0)
        
        # Pricer le produit
        price = pricer.price(product, spot=105.0)
        assert price == 10500.0
        
        # Obtenir les infos
        info = pricer.get_pricing_info()
        assert info['method'] == 'analytic'
        assert info['model'] == 'BlackScholes'
    
    def test_multiple_pricers_independence(self):
        """Test que plusieurs pricers sont indépendants."""
        model1 = ConcreteModel("Model1", {"param": 1.0})
        model2 = ConcreteModel("Model2", {"param": 2.0})
        
        pricer1 = ConcretePricer(model1, PricingMethod.ANALYTIC)
        pricer2 = ConcretePricer(model2, PricingMethod.MONTE_CARLO)
        
        # Modifier model1 ne devrait pas affecter pricer2
        model1.set_parameters({"param": 10.0})
        
        assert pricer1.model.get_parameters()["param"] == 10.0
        assert pricer2.model.get_parameters()["param"] == 2.0
    
    def test_all_pricing_methods_can_be_used(self):
        """Test que toutes les méthodes de pricing peuvent être utilisées."""
        model = ConcreteModel("TestModel")
        product = ConcreteProduct(ProductType.OPTION, 1.0, 1.0)
        
        for method in PricingMethod:
            pricer = ConcretePricer(model, method)
            price = pricer.price(product, spot=100.0)
            assert price == 100.0  # Notre implémentation simple
            
            info = pricer.get_pricing_info()
            assert info['method'] == method.value
    
    def test_pricer_with_different_products(self):
        """Test le même pricer avec différents produits."""
        model = ConcreteModel("TestModel")
        pricer = ConcretePricer(model, PricingMethod.ANALYTIC)
        
        products = [
            ConcreteProduct(ProductType.OPTION, 1.0, 100.0),
            ConcreteProduct(ProductType.SWAP, 5.0, 1000.0),
            ConcreteProduct(ProductType.FORWARD, 0.5, 50.0)
        ]
        
        for product in products:
            price = pricer.price(product, spot=100.0)
            assert price == product.notional * 100.0
    
    def test_same_model_different_pricers(self):
        """Test le même modèle avec différents pricers."""
        model = ConcreteModel("SharedModel", {"vol": 0.25})
        
        pricer_analytic = ConcretePricer(model, PricingMethod.ANALYTIC)
        pricer_mc = ConcretePricer(model, PricingMethod.MONTE_CARLO)
        
        # Les deux pricers partagent le même modèle
        assert pricer_analytic.model == pricer_mc.model
        assert pricer_analytic.model.name == "SharedModel"
        assert pricer_mc.model.name == "SharedModel"
        
        # Mais ont des méthodes différentes
        assert pricer_analytic.method != pricer_mc.method
