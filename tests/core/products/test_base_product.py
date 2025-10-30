"""
Tests pour la classe BaseProduct et les énumérations associées.

Ces tests vérifient le comportement de la classe abstraite BaseProduct
et des énumérations ProductType, OptionType, ExerciseType.
"""

import pytest
from datetime import datetime
from backend.core.products.base_product import (
    BaseProduct,
    ProductType,
    OptionType,
    ExerciseType
)


# Classe concrète pour tester BaseProduct
class ConcreteProduct(BaseProduct):
    """
    Implémentation concrète minimale de BaseProduct pour les tests.
    """
    
    def payoff(self, spot_price: float, **kwargs) -> float:
        """
        Payoff simple basé sur le spot et le notionnel.
        """
        return self.notional * spot_price
    
    def get_characteristics(self):
        """
        Retourne les caractéristiques de base.
        """
        return {
            'product_type': self.product_type.value,
            'maturity': self.maturity,
            'notional': self.notional
        }


class TestProductType:
    """Tests pour l'énumération ProductType."""
    
    def test_all_product_types_exist(self):
        """Vérifie que tous les types de produits sont définis."""
        assert ProductType.OPTION.value == "option"
        assert ProductType.SWAP.value == "swap"
        assert ProductType.SWAPTION.value == "swaption"
        assert ProductType.FORWARD.value == "forward"
        assert ProductType.BOND.value == "bond"
        assert ProductType.CAP_FLOOR.value == "cap_floor"
    
    def test_product_type_comparison(self):
        """Test la comparaison de types de produits."""
        assert ProductType.OPTION == ProductType.OPTION
        assert ProductType.OPTION != ProductType.SWAP
    
    def test_product_type_from_string(self):
        """Test la création depuis une string."""
        assert ProductType("option") == ProductType.OPTION
        assert ProductType("swap") == ProductType.SWAP
    
    def test_product_type_invalid_raises_error(self):
        """Test qu'une valeur invalide lève une erreur."""
        with pytest.raises(ValueError):
            ProductType("invalid")


class TestOptionType:
    """Tests pour l'énumération OptionType."""
    
    def test_all_option_types_exist(self):
        """Vérifie que tous les types d'options sont définis."""
        assert OptionType.CALL.value == "call"
        assert OptionType.PUT.value == "put"
    
    def test_option_type_comparison(self):
        """Test la comparaison de types d'options."""
        assert OptionType.CALL == OptionType.CALL
        assert OptionType.CALL != OptionType.PUT
    
    def test_option_type_from_string(self):
        """Test la création depuis une string."""
        assert OptionType("call") == OptionType.CALL
        assert OptionType("put") == OptionType.PUT


class TestExerciseType:
    """Tests pour l'énumération ExerciseType."""
    
    def test_all_exercise_types_exist(self):
        """Vérifie que tous les types d'exercice sont définis."""
        assert ExerciseType.EUROPEAN.value == "european"
        assert ExerciseType.AMERICAN.value == "american"
        assert ExerciseType.BERMUDAN.value == "bermudan"
    
    def test_exercise_type_comparison(self):
        """Test la comparaison de types d'exercice."""
        assert ExerciseType.EUROPEAN == ExerciseType.EUROPEAN
        assert ExerciseType.EUROPEAN != ExerciseType.AMERICAN
    
    def test_exercise_type_from_string(self):
        """Test la création depuis une string."""
        assert ExerciseType("european") == ExerciseType.EUROPEAN
        assert ExerciseType("american") == ExerciseType.AMERICAN
        assert ExerciseType("bermudan") == ExerciseType.BERMUDAN


class TestBaseProductInitialization:
    """Tests pour l'initialisation de BaseProduct."""
    
    def test_init_with_valid_parameters(self):
        """Test l'initialisation avec des paramètres valides."""
        product = ConcreteProduct(
            product_type=ProductType.OPTION,
            maturity=1.0,
            notional=100.0
        )
        assert product.product_type == ProductType.OPTION
        assert product.maturity == 1.0
        assert product.notional == 100.0
    
    def test_init_with_default_notional(self):
        """Test l'initialisation avec le notionnel par défaut."""
        product = ConcreteProduct(
            product_type=ProductType.SWAP,
            maturity=5.0
        )
        assert product.notional == 1.0
    
    def test_init_with_zero_maturity_raises_error(self):
        """Test qu'une maturité nulle lève une erreur."""
        with pytest.raises(ValueError, match="maturité doit être strictement positive"):
            ConcreteProduct(
                product_type=ProductType.OPTION,
                maturity=0,
                notional=100.0
            )
    
    def test_init_with_negative_maturity_raises_error(self):
        """Test qu'une maturité négative lève une erreur."""
        with pytest.raises(ValueError, match="maturité doit être strictement positive"):
            ConcreteProduct(
                product_type=ProductType.OPTION,
                maturity=-1.0,
                notional=100.0
            )
    
    def test_init_with_zero_notional_raises_error(self):
        """Test qu'un notionnel nul lève une erreur."""
        with pytest.raises(ValueError, match="notionnel doit être strictement positif"):
            ConcreteProduct(
                product_type=ProductType.OPTION,
                maturity=1.0,
                notional=0
            )
    
    def test_init_with_negative_notional_raises_error(self):
        """Test qu'un notionnel négatif lève une erreur."""
        with pytest.raises(ValueError, match="notionnel doit être strictement positif"):
            ConcreteProduct(
                product_type=ProductType.OPTION,
                maturity=1.0,
                notional=-100.0
            )
    
    def test_init_with_different_product_types(self):
        """Test l'initialisation avec différents types de produits."""
        for ptype in ProductType:
            product = ConcreteProduct(
                product_type=ptype,
                maturity=1.0,
                notional=100.0
            )
            assert product.product_type == ptype


class TestBaseProductPayoff:
    """Tests pour la méthode payoff (implémentation concrète)."""
    
    def test_payoff_simple(self):
        """Test le payoff simple."""
        product = ConcreteProduct(
            product_type=ProductType.OPTION,
            maturity=1.0,
            notional=10.0
        )
        assert product.payoff(100.0) == 1000.0  # 10 * 100
    
    def test_payoff_with_different_notionals(self):
        """Test le payoff avec différents notionnels."""
        product1 = ConcreteProduct(ProductType.OPTION, 1.0, notional=1.0)
        product2 = ConcreteProduct(ProductType.OPTION, 1.0, notional=100.0)
        
        assert product1.payoff(50.0) == 50.0
        assert product2.payoff(50.0) == 5000.0


class TestBaseProductGetCharacteristics:
    """Tests pour la méthode get_characteristics."""
    
    def test_get_characteristics_returns_dict(self):
        """Test que get_characteristics retourne un dictionnaire."""
        product = ConcreteProduct(
            product_type=ProductType.SWAP,
            maturity=2.5,
            notional=1000000.0
        )
        chars = product.get_characteristics()
        assert isinstance(chars, dict)
        assert chars['product_type'] == 'swap'
        assert chars['maturity'] == 2.5
        assert chars['notional'] == 1000000.0


class TestBaseProductGetTimeToMaturity:
    """Tests pour la méthode get_time_to_maturity."""
    
    def test_get_time_to_maturity_without_date(self):
        """Test get_time_to_maturity sans date (retourne maturity)."""
        product = ConcreteProduct(
            product_type=ProductType.OPTION,
            maturity=1.5
        )
        assert product.get_time_to_maturity() == 1.5
    
    def test_get_time_to_maturity_with_date(self):
        """Test get_time_to_maturity avec une date."""
        product = ConcreteProduct(
            product_type=ProductType.OPTION,
            maturity=2.0
        )
        # Pour l'instant, l'implémentation retourne toujours maturity
        assert product.get_time_to_maturity(datetime.now()) == 2.0
    
    def test_get_time_to_maturity_different_maturities(self):
        """Test avec différentes maturités."""
        for maturity in [0.5, 1.0, 5.0, 10.0]:
            product = ConcreteProduct(
                product_type=ProductType.BOND,
                maturity=maturity
            )
            assert product.get_time_to_maturity() == maturity


class TestBaseProductValidate:
    """Tests pour la méthode validate."""
    
    def test_validate_with_valid_parameters(self):
        """Test validate avec des paramètres valides."""
        product = ConcreteProduct(
            product_type=ProductType.OPTION,
            maturity=1.0,
            notional=100.0
        )
        assert product.validate() is True
    
    def test_validate_after_modifying_maturity_to_zero(self):
        """Test validate après modification de la maturité à 0."""
        product = ConcreteProduct(
            product_type=ProductType.OPTION,
            maturity=1.0,
            notional=100.0
        )
        product.maturity = 0
        with pytest.raises(ValueError, match="maturité doit être strictement positive"):
            product.validate()
    
    def test_validate_after_modifying_maturity_to_negative(self):
        """Test validate après modification de la maturité en négatif."""
        product = ConcreteProduct(
            product_type=ProductType.OPTION,
            maturity=1.0,
            notional=100.0
        )
        product.maturity = -1.0
        with pytest.raises(ValueError, match="maturité doit être strictement positive"):
            product.validate()
    
    def test_validate_after_modifying_notional_to_zero(self):
        """Test validate après modification du notionnel à 0."""
        product = ConcreteProduct(
            product_type=ProductType.OPTION,
            maturity=1.0,
            notional=100.0
        )
        product.notional = 0
        with pytest.raises(ValueError, match="notionnel doit être strictement positif"):
            product.validate()
    
    def test_validate_after_modifying_notional_to_negative(self):
        """Test validate après modification du notionnel en négatif."""
        product = ConcreteProduct(
            product_type=ProductType.OPTION,
            maturity=1.0,
            notional=100.0
        )
        product.notional = -100.0
        with pytest.raises(ValueError, match="notionnel doit être strictement positif"):
            product.validate()


class TestBaseProductStringRepresentations:
    """Tests pour __repr__ et __str__."""
    
    def test_repr_contains_class_name(self):
        """Test que __repr__ contient le nom de la classe."""
        product = ConcreteProduct(
            product_type=ProductType.OPTION,
            maturity=1.0,
            notional=100.0
        )
        repr_str = repr(product)
        assert "ConcreteProduct" in repr_str
        assert "type=option" in repr_str
        assert "maturity=1.0" in repr_str
        assert "notional=100.0" in repr_str
    
    def test_repr_different_product_types(self):
        """Test __repr__ avec différents types de produits."""
        product = ConcreteProduct(
            product_type=ProductType.SWAP,
            maturity=5.0,
            notional=1000000.0
        )
        repr_str = repr(product)
        assert "type=swap" in repr_str
        assert "maturity=5.0" in repr_str
    
    def test_str_readable_format(self):
        """Test que __str__ produit un format lisible."""
        product = ConcreteProduct(
            product_type=ProductType.BOND,
            maturity=10.0,
            notional=1000000.0
        )
        str_repr = str(product)
        assert "Bond" in str_repr
        assert "10.0" in str_repr
        assert "1,000,000" in str_repr  # Format avec virgules
    
    def test_str_different_product_types(self):
        """Test __str__ avec différents types de produits."""
        product = ConcreteProduct(
            product_type=ProductType.SWAPTION,
            maturity=2.0,
            notional=500000.0
        )
        str_repr = str(product)
        assert "Swaption" in str_repr
        assert "2.0" in str_repr


class TestBaseProductAbstractMethods:
    """Tests pour vérifier que les méthodes abstraites doivent être implémentées."""
    
    def test_cannot_instantiate_base_product(self):
        """Test qu'on ne peut pas instancier BaseProduct directement."""
        with pytest.raises(TypeError):
            BaseProduct(
                product_type=ProductType.OPTION,
                maturity=1.0,
                notional=100.0
            )
    
    def test_concrete_class_must_implement_payoff(self):
        """Test qu'une classe concrète doit implémenter payoff."""
        
        # Classe incomplète (manque payoff)
        class IncompleteProduct1(BaseProduct):
            def get_characteristics(self):
                return {}
        
        with pytest.raises(TypeError):
            IncompleteProduct1(ProductType.OPTION, 1.0)
    
    def test_concrete_class_must_implement_get_characteristics(self):
        """Test qu'une classe concrète doit implémenter get_characteristics."""
        
        # Classe incomplète (manque get_characteristics)
        class IncompleteProduct2(BaseProduct):
            def payoff(self, spot_price, **kwargs):
                return 0.0
        
        with pytest.raises(TypeError):
            IncompleteProduct2(ProductType.OPTION, 1.0)


class TestBaseProductEdgeCases:
    """Tests pour les cas limites."""
    
    def test_very_small_maturity(self):
        """Test avec une maturité très petite mais positive."""
        product = ConcreteProduct(
            product_type=ProductType.OPTION,
            maturity=0.001,  # ~9 heures
            notional=100.0
        )
        assert product.maturity == 0.001
        assert product.validate() is True
    
    def test_very_large_maturity(self):
        """Test avec une maturité très grande."""
        product = ConcreteProduct(
            product_type=ProductType.BOND,
            maturity=100.0,  # 100 ans
            notional=100.0
        )
        assert product.maturity == 100.0
        assert product.validate() is True
    
    def test_very_small_notional(self):
        """Test avec un notionnel très petit."""
        product = ConcreteProduct(
            product_type=ProductType.OPTION,
            maturity=1.0,
            notional=0.01
        )
        assert product.notional == 0.01
        assert product.validate() is True
    
    def test_very_large_notional(self):
        """Test avec un notionnel très grand."""
        product = ConcreteProduct(
            product_type=ProductType.SWAP,
            maturity=5.0,
            notional=1e12  # 1 trillion
        )
        assert product.notional == 1e12
        assert product.validate() is True
    
    def test_fractional_maturity(self):
        """Test avec une maturité fractionnaire."""
        product = ConcreteProduct(
            product_type=ProductType.OPTION,
            maturity=0.25,  # 3 mois
            notional=100.0
        )
        assert product.maturity == 0.25


class TestBaseProductIntegration:
    """Tests d'intégration pour vérifier le comportement global."""
    
    def test_full_workflow(self):
        """Test un workflow complet."""
        # Créer un produit
        product = ConcreteProduct(
            product_type=ProductType.FORWARD,
            maturity=2.0,
            notional=1000.0
        )
        
        # Valider
        assert product.validate() is True
        
        # Calculer le payoff
        payoff = product.payoff(spot_price=105.0)
        assert payoff == 105000.0  # 1000 * 105
        
        # Obtenir les caractéristiques
        chars = product.get_characteristics()
        assert chars['product_type'] == 'forward'
        assert chars['maturity'] == 2.0
        
        # Temps jusqu'à maturité
        ttm = product.get_time_to_maturity()
        assert ttm == 2.0
    
    def test_multiple_products_independence(self):
        """Test que plusieurs instances sont indépendantes."""
        product1 = ConcreteProduct(ProductType.OPTION, 1.0, 100.0)
        product2 = ConcreteProduct(ProductType.SWAP, 5.0, 1000.0)
        
        # Modifier product1 ne devrait pas affecter product2
        product1.maturity = 2.0
        assert product2.maturity == 5.0
        
        product1.notional = 200.0
        assert product2.notional == 1000.0
    
    def test_all_product_types_can_be_instantiated(self):
        """Test que tous les types de produits peuvent être instanciés."""
        for ptype in ProductType:
            product = ConcreteProduct(
                product_type=ptype,
                maturity=1.0,
                notional=100.0
            )
            assert product.product_type == ptype
            assert product.validate() is True
