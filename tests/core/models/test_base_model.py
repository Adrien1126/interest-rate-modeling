"""
Tests pour la classe BaseModel.

Ces tests vérifient le comportement de la classe abstraite BaseModel
en utilisant une implémentation concrète minimale.
"""

import pytest
import numpy as np
from backend.core.models.base_model import BaseModel


# Classe concrète pour tester BaseModel
class ConcreteModel(BaseModel):
    """
    Implémentation concrète minimale de BaseModel pour les tests.
    """
    
    def _validate_parameters(self) -> None:
        """
        Validation simple : vérifie que 'param1' existe et est positif.
        """
        if 'param1' in self.parameters:
            if self.parameters['param1'] <= 0:
                raise ValueError("param1 must be positive")
    
    def simulate(
        self, 
        S0: float, 
        T: float, 
        n_steps: int, 
        n_paths: int,
        random_seed: int = None
    ) -> np.ndarray:
        """
        Simulation simple qui retourne des chemins browniens.
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        
        dt = T / n_steps
        paths = np.zeros((n_paths, n_steps + 1))
        paths[:, 0] = S0
        
        for i in range(1, n_steps + 1):
            dW = np.random.randn(n_paths) * np.sqrt(dt)
            paths[:, i] = paths[:, i-1] + dW
        
        return paths
    
    def characteristic_function(self, u: complex, t: float, **kwargs) -> complex:
        """
        Fonction caractéristique simple (exponentielle).
        """
        return np.exp(1j * u * t)


class TestBaseModelInitialization:
    """Tests pour l'initialisation de BaseModel."""
    
    def test_init_with_name_only(self):
        """Test l'initialisation avec uniquement un nom."""
        model = ConcreteModel("TestModel")
        assert model.name == "TestModel"
        assert model.parameters == {}
    
    def test_init_with_parameters(self):
        """Test l'initialisation avec des paramètres."""
        params = {"param1": 1.5, "param2": 2.0}
        model = ConcreteModel("TestModel", params)
        assert model.name == "TestModel"
        assert model.parameters == params
    
    def test_init_with_empty_parameters(self):
        """Test l'initialisation avec un dictionnaire vide."""
        model = ConcreteModel("TestModel", {})
        assert model.parameters == {}
    
    def test_init_validates_parameters(self):
        """Test que l'initialisation valide les paramètres."""
        with pytest.raises(ValueError, match="param1 must be positive"):
            ConcreteModel("TestModel", {"param1": -1.0})
    
    def test_parameters_are_copied(self):
        """Test que les paramètres sont copiés et non référencés."""
        original_params = {"param1": 1.5}
        model = ConcreteModel("TestModel", original_params)
        original_params["param1"] = 99.0
        # Le modèle ne devrait pas être affecté
        assert model.parameters["param1"] == 1.5


class TestBaseModelGetParameters:
    """Tests pour la méthode get_parameters."""
    
    def test_get_parameters_returns_copy(self):
        """Test que get_parameters retourne une copie."""
        model = ConcreteModel("TestModel", {"param1": 1.5, "param2": 2.0})
        params = model.get_parameters()
        params["param1"] = 99.0
        # Le modèle ne devrait pas être affecté
        assert model.parameters["param1"] == 1.5
    
    def test_get_parameters_empty(self):
        """Test get_parameters avec un modèle sans paramètres."""
        model = ConcreteModel("TestModel")
        params = model.get_parameters()
        assert params == {}
    
    def test_get_parameters_returns_all_params(self):
        """Test que tous les paramètres sont retournés."""
        original_params = {"param1": 1.5, "param2": 2.0, "param3": 3.5}
        model = ConcreteModel("TestModel", original_params)
        params = model.get_parameters()
        assert params == original_params


class TestBaseModelSetParameters:
    """Tests pour la méthode set_parameters."""
    
    def test_set_parameters_updates_existing(self):
        """Test la mise à jour de paramètres existants."""
        model = ConcreteModel("TestModel", {"param1": 1.5, "param2": 2.0})
        model.set_parameters({"param1": 3.0})
        assert model.parameters["param1"] == 3.0
        assert model.parameters["param2"] == 2.0  # Inchangé
    
    def test_set_parameters_adds_new(self):
        """Test l'ajout de nouveaux paramètres."""
        model = ConcreteModel("TestModel", {"param1": 1.5})
        model.set_parameters({"param3": 3.0})
        assert model.parameters["param1"] == 1.5
        assert model.parameters["param3"] == 3.0
    
    def test_set_parameters_validates(self):
        """Test que set_parameters valide les paramètres."""
        model = ConcreteModel("TestModel", {"param1": 1.5})
        with pytest.raises(ValueError, match="param1 must be positive"):
            model.set_parameters({"param1": -1.0})
    
    def test_set_parameters_empty_dict(self):
        """Test set_parameters avec un dictionnaire vide."""
        model = ConcreteModel("TestModel", {"param1": 1.5})
        model.set_parameters({})
        assert model.parameters == {"param1": 1.5}
    
    def test_set_parameters_multiple(self):
        """Test la mise à jour de plusieurs paramètres à la fois."""
        model = ConcreteModel("TestModel", {"param1": 1.5, "param2": 2.0})
        model.set_parameters({"param1": 3.0, "param2": 4.0, "param3": 5.0})
        assert model.parameters == {"param1": 3.0, "param2": 4.0, "param3": 5.0}


class TestBaseModelStringRepresentations:
    """Tests pour __repr__ et __str__."""
    
    def test_repr_with_parameters(self):
        """Test __repr__ avec des paramètres."""
        model = ConcreteModel("TestModel", {"param1": 1.5, "param2": 2.0})
        repr_str = repr(model)
        assert "ConcreteModel" in repr_str
        assert "param1=1.5000" in repr_str
        assert "param2=2.0000" in repr_str
    
    def test_repr_without_parameters(self):
        """Test __repr__ sans paramètres."""
        model = ConcreteModel("TestModel")
        repr_str = repr(model)
        assert repr_str == "ConcreteModel()"
    
    def test_str_with_parameters(self):
        """Test __str__ avec des paramètres."""
        model = ConcreteModel("TestModel", {"param1": 1.5, "param2": 2.0})
        str_repr = str(model)
        assert "TestModel" in str_repr
        assert "param1" in str_repr
        assert "param2" in str_repr
        assert str_repr == "TestModel avec paramètres: {'param1': 1.5, 'param2': 2.0}"
    
    def test_str_without_parameters(self):
        """Test __str__ sans paramètres."""
        model = ConcreteModel("TestModel")
        str_repr = str(model)
        assert str_repr == "TestModel avec paramètres: {}"


class TestBaseModelSimulate:
    """Tests pour la méthode simulate (implémentation concrète)."""
    
    def test_simulate_output_shape(self):
        """Test que simulate retourne la bonne forme de array."""
        model = ConcreteModel("TestModel")
        paths = model.simulate(S0=100.0, T=1.0, n_steps=252, n_paths=1000)
        assert paths.shape == (1000, 253)  # n_paths x (n_steps + 1)
    
    def test_simulate_initial_value(self):
        """Test que toutes les trajectoires commencent à S0."""
        model = ConcreteModel("TestModel")
        S0 = 100.0
        paths = model.simulate(S0=S0, T=1.0, n_steps=252, n_paths=1000)
        assert np.allclose(paths[:, 0], S0)
    
    def test_simulate_reproducibility_with_seed(self):
        """Test que simulate est reproductible avec une graine."""
        model = ConcreteModel("TestModel")
        paths1 = model.simulate(S0=100.0, T=1.0, n_steps=100, n_paths=10, random_seed=42)
        paths2 = model.simulate(S0=100.0, T=1.0, n_steps=100, n_paths=10, random_seed=42)
        assert np.allclose(paths1, paths2)
    
    def test_simulate_different_seeds_different_results(self):
        """Test que différentes graines donnent des résultats différents."""
        model = ConcreteModel("TestModel")
        paths1 = model.simulate(S0=100.0, T=1.0, n_steps=100, n_paths=10, random_seed=42)
        paths2 = model.simulate(S0=100.0, T=1.0, n_steps=100, n_paths=10, random_seed=123)
        assert not np.allclose(paths1, paths2)
    
    def test_simulate_different_n_steps(self):
        """Test simulate avec différents nombres de pas."""
        model = ConcreteModel("TestModel")
        paths_10 = model.simulate(S0=100.0, T=1.0, n_steps=10, n_paths=100, random_seed=42)
        paths_100 = model.simulate(S0=100.0, T=1.0, n_steps=100, n_paths=100, random_seed=42)
        assert paths_10.shape == (100, 11)
        assert paths_100.shape == (100, 101)


class TestBaseModelCharacteristicFunction:
    """Tests pour la méthode characteristic_function."""
    
    def test_characteristic_function_returns_complex(self):
        """Test que la fonction caractéristique retourne un complexe."""
        model = ConcreteModel("TestModel")
        result = model.characteristic_function(u=1+2j, t=1.0)
        assert isinstance(result, (complex, np.complexfloating))
    
    def test_characteristic_function_simple_values(self):
        """Test la fonction caractéristique avec des valeurs simples."""
        model = ConcreteModel("TestModel")
        # Pour notre implémentation simple: exp(i*u*t)
        u = 1.0
        t = 2.0
        result = model.characteristic_function(u=u, t=t)
        expected = np.exp(1j * u * t)
        assert np.isclose(result, expected)
    
    def test_characteristic_function_with_complex_argument(self):
        """Test avec un argument complexe."""
        model = ConcreteModel("TestModel")
        u = 1.0 + 2.0j
        t = 1.5
        result = model.characteristic_function(u=u, t=t)
        expected = np.exp(1j * u * t)
        assert np.isclose(result, expected)
    
    def test_characteristic_function_at_zero(self):
        """Test la fonction caractéristique en u=0."""
        model = ConcreteModel("TestModel")
        result = model.characteristic_function(u=0, t=1.0)
        # exp(i*0*t) = exp(0) = 1
        assert np.isclose(result, 1.0)


class TestBaseModelAbstractMethods:
    """Tests pour vérifier que les méthodes abstraites doivent être implémentées."""
    
    def test_cannot_instantiate_base_model(self):
        """Test qu'on ne peut pas instancier BaseModel directement."""
        with pytest.raises(TypeError):
            BaseModel("TestModel")
    
    def test_concrete_model_must_implement_all_methods(self):
        """Test qu'une classe concrète doit implémenter toutes les méthodes abstraites."""
        
        # Classe incomplète (manque characteristic_function)
        class IncompleteModel(BaseModel):
            def _validate_parameters(self):
                pass
            
            def simulate(self, S0, T, n_steps, n_paths, random_seed=None):
                return np.zeros((n_paths, n_steps + 1))
        
        with pytest.raises(TypeError):
            IncompleteModel("Incomplete")


class TestBaseModelEdgeCases:
    """Tests pour les cas limites."""
    
    def test_model_with_numeric_parameters(self):
        """Test avec différents types numériques."""
        model = ConcreteModel("TestModel", {
            "param1": 1,      # int
            "param2": 1.5,    # float
            "param3": np.float64(2.0)  # numpy float
        })
        assert len(model.parameters) == 3
    
    def test_model_name_with_special_characters(self):
        """Test avec des caractères spéciaux dans le nom."""
        model = ConcreteModel("Test-Model_v1.0")
        assert model.name == "Test-Model_v1.0"
    
    def test_parameters_with_zero_values(self):
        """Test avec des paramètres à zéro."""
        model = ConcreteModel("TestModel", {"param2": 0.0})
        assert model.parameters["param2"] == 0.0
    
    def test_parameters_with_large_values(self):
        """Test avec de grandes valeurs."""
        model = ConcreteModel("TestModel", {"param1": 1e10, "param2": 1e-10})
        assert model.parameters["param1"] == 1e10
        assert model.parameters["param2"] == 1e-10
    
    def test_get_parameters_immutability(self):
        """Test que la modification des paramètres retournés n'affecte pas le modèle."""
        model = ConcreteModel("TestModel", {"param1": 1.5})
        params = model.get_parameters()
        params["param1"] = 999.0
        params["new_param"] = 100.0
        # Le modèle ne devrait pas être affecté
        assert model.parameters["param1"] == 1.5
        assert "new_param" not in model.parameters


class TestBaseModelIntegration:
    """Tests d'intégration pour vérifier le comportement global."""
    
    def test_full_workflow(self):
        """Test un workflow complet : création, modification, simulation."""
        # Créer un modèle
        model = ConcreteModel("TestModel", {"param1": 1.5})
        
        # Vérifier l'état initial
        assert model.name == "TestModel"
        assert model.parameters["param1"] == 1.5
        
        # Modifier les paramètres
        model.set_parameters({"param1": 2.0, "param2": 3.0})
        assert model.parameters["param1"] == 2.0
        assert model.parameters["param2"] == 3.0
        
        # Simuler
        paths = model.simulate(S0=100.0, T=1.0, n_steps=10, n_paths=5, random_seed=42)
        assert paths.shape == (5, 11)
        
        # Fonction caractéristique
        cf = model.characteristic_function(u=1.0, t=1.0)
        assert isinstance(cf, (complex, np.complexfloating))
    
    def test_multiple_models_independence(self):
        """Test que plusieurs instances de modèle sont indépendantes."""
        model1 = ConcreteModel("Model1", {"param1": 1.0})
        model2 = ConcreteModel("Model2", {"param1": 2.0})
        
        model1.set_parameters({"param1": 10.0})
        
        # model2 ne devrait pas être affecté
        assert model2.parameters["param1"] == 2.0
        assert model1.parameters["param1"] == 10.0
