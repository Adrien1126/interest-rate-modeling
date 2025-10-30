"""
Tests pour les utilitaires stochastiques.

Teste :
- Simulation de lois de probabilité
- Génération de chemins browniens
- Corrélation et matrices
- Validation des paramètres
"""

import pytest
import numpy as np
from backend.core.utils.stochastic_utils import (
    # Lois de probabilité
    simulate_normal,
    simulate_uniform,
    simulate_correlated_normals,
    # Brownien
    brownian_path,
    geometric_brownian_path,
    brownian_bridge,
    # Temps
    time_grid,
    time_step,
    # Corrélation
    correlation_matrix,
    cholesky_decomposition,
    simulate_correlated_normal_vectors,
    # Réduction variance
    antithetic_variates,
    # Validation
    validate_positive,
    validate_non_negative,
    validate_probability,
    validate_correlation
)


# ============================================================================
# TESTS : LOIS DE PROBABILITÉ
# ============================================================================

class TestSimulateNormal:
    """Tests pour simulate_normal."""
    
    def test_shape_scalar(self):
        """Test que la forme est correcte (scalaire)."""
        z = simulate_normal(100, seed=42)
        assert z.shape == (100,)
    
    def test_shape_tuple(self):
        """Test que la forme est correcte (tuple)."""
        z = simulate_normal((10, 5), seed=42)
        assert z.shape == (10, 5)
    
    def test_mean_std(self):
        """Test que la moyenne et l'écart-type sont corrects."""
        z = simulate_normal(100000, mean=5.0, std=2.0, seed=42)
        
        assert abs(z.mean() - 5.0) < 0.05
        assert abs(z.std() - 2.0) < 0.05
    
    def test_reproducibility(self):
        """Test que la seed donne des résultats reproductibles."""
        z1 = simulate_normal(100, seed=42)
        z2 = simulate_normal(100, seed=42)
        
        np.testing.assert_array_equal(z1, z2)


class TestSimulateUniform:
    """Tests pour simulate_uniform."""
    
    def test_bounds(self):
        """Test que les valeurs sont dans les bornes."""
        u = simulate_uniform(1000, low=2.0, high=8.0, seed=42)
        
        assert np.all(u >= 2.0)
        assert np.all(u <= 8.0)
    
    def test_mean(self):
        """Test que la moyenne est correcte."""
        u = simulate_uniform(100000, low=0.0, high=10.0, seed=42)
        
        # Moyenne d'une uniforme [a,b] = (a+b)/2
        assert abs(u.mean() - 5.0) < 0.05


class TestSimulateCorrelatedNormals:
    """Tests pour simulate_correlated_normals."""
    
    def test_correlation_positive(self):
        """Test avec corrélation positive."""
        z1, z2 = simulate_correlated_normals(10000, correlation=0.7, seed=42)
        
        empirical_corr = np.corrcoef(z1, z2)[0, 1]
        assert abs(empirical_corr - 0.7) < 0.05
    
    def test_correlation_negative(self):
        """Test avec corrélation négative."""
        z1, z2 = simulate_correlated_normals(10000, correlation=-0.5, seed=42)
        
        empirical_corr = np.corrcoef(z1, z2)[0, 1]
        assert abs(empirical_corr - (-0.5)) < 0.05
    
    def test_correlation_zero(self):
        """Test avec corrélation nulle."""
        z1, z2 = simulate_correlated_normals(10000, correlation=0.0, seed=42)
        
        empirical_corr = np.corrcoef(z1, z2)[0, 1]
        assert abs(empirical_corr) < 0.05
    
    def test_invalid_correlation(self):
        """Test avec corrélation invalide."""
        with pytest.raises(ValueError, match="Corrélation doit être dans"):
            simulate_correlated_normals(100, correlation=1.5)


# ============================================================================
# TESTS : MOUVEMENT BROWNIEN
# ============================================================================

class TestBrownianPath:
    """Tests pour brownian_path."""
    
    def test_shape(self):
        """Test que la forme est correcte."""
        paths = brownian_path(100, 0.01, n_paths=5, seed=42)
        assert paths.shape == (5, 101)  # n_steps + 1
    
    def test_initial_value(self):
        """Test que W(0) = 0."""
        paths = brownian_path(100, 0.01, n_paths=10, seed=42)
        np.testing.assert_array_equal(paths[:, 0], 0)
    
    def test_variance_scaling(self):
        """Test que Var(W(t)) = t."""
        n_paths = 10000
        T = 1.0
        n_steps = 100
        dt = T / n_steps
        
        paths = brownian_path(n_steps, dt, n_paths, seed=42)
        
        # À t=1, Var(W(1)) = 1
        var_at_T = paths[:, -1].var()
        assert abs(var_at_T - T) < 0.1


class TestGeometricBrownianPath:
    """Tests pour geometric_brownian_path."""
    
    def test_shape(self):
        """Test que la forme est correcte."""
        paths = geometric_brownian_path(100, 0.05, 0.2, 1.0, 252, n_paths=3, seed=42)
        assert paths.shape == (3, 253)
    
    def test_initial_value(self):
        """Test que S(0) = S0."""
        S0 = 100.0
        paths = geometric_brownian_path(S0, 0.05, 0.2, 1.0, 100, n_paths=5, seed=42)
        np.testing.assert_allclose(paths[:, 0], S0)
    
    def test_positivity(self):
        """Test que les chemins restent positifs."""
        paths = geometric_brownian_path(100, 0.05, 0.2, 1.0, 100, n_paths=10, seed=42)
        assert np.all(paths > 0)
    
    def test_mean_at_maturity(self):
        """Test que E[S(T)] ≈ S0 * exp(μT)."""
        S0 = 100.0
        mu = 0.1
        T = 1.0
        
        paths = geometric_brownian_path(S0, mu, 0.2, T, 252, n_paths=10000, seed=42)
        
        expected_mean = S0 * np.exp(mu * T)
        empirical_mean = paths[:, -1].mean()
        
        # Tolérance large car variance est élevée
        assert abs(empirical_mean - expected_mean) / expected_mean < 0.05


class TestBrownianBridge:
    """Tests pour brownian_bridge."""
    
    def test_endpoints(self):
        """Test que le pont commence et finit aux bonnes valeurs."""
        bridge = brownian_bridge(0, 1, 100, n_paths=10, seed=42)
        
        np.testing.assert_allclose(bridge[:, 0], 0, atol=1e-10)
        np.testing.assert_allclose(bridge[:, -1], 1, atol=1e-10)
    
    def test_shape(self):
        """Test que la forme est correcte."""
        bridge = brownian_bridge(0, 1, 50, n_paths=3, seed=42)
        assert bridge.shape == (3, 51)


# ============================================================================
# TESTS : TEMPS
# ============================================================================

class TestTimeGrid:
    """Tests pour time_grid."""
    
    def test_with_zero(self):
        """Test avec t=0 inclus."""
        grid = time_grid(1.0, 4, include_zero=True)
        expected = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
        np.testing.assert_allclose(grid, expected)
    
    def test_without_zero(self):
        """Test sans t=0."""
        grid = time_grid(1.0, 4, include_zero=False)
        expected = np.array([0.25, 0.5, 0.75, 1.0])
        np.testing.assert_allclose(grid, expected)


class TestTimeStep:
    """Tests pour time_step."""
    
    def test_basic(self):
        """Test du calcul du pas de temps."""
        dt = time_step(1.0, 100)
        assert dt == 0.01
        
        dt = time_step(2.0, 200)
        assert dt == 0.01


# ============================================================================
# TESTS : CORRÉLATION
# ============================================================================

class TestCorrelationMatrix:
    """Tests pour correlation_matrix."""
    
    def test_uniform_correlation(self):
        """Test avec corrélation uniforme."""
        C = correlation_matrix(0.5, 3)
        
        expected = np.array([
            [1.0, 0.5, 0.5],
            [0.5, 1.0, 0.5],
            [0.5, 0.5, 1.0]
        ])
        
        np.testing.assert_allclose(C, expected)
    
    def test_diagonal_ones(self):
        """Test que la diagonale est 1."""
        C = correlation_matrix(0.3, 5)
        np.testing.assert_allclose(np.diag(C), 1.0)
    
    def test_symmetric(self):
        """Test que la matrice est symétrique."""
        C = correlation_matrix(0.4, 4)
        np.testing.assert_allclose(C, C.T)
    
    def test_custom_matrix(self):
        """Test avec matrice personnalisée."""
        custom = np.array([
            [1.0, 0.5, 0.3],
            [0.5, 1.0, 0.6],
            [0.3, 0.6, 1.0]
        ])
        
        C = correlation_matrix(custom, 3)
        np.testing.assert_allclose(C, custom)
    
    def test_invalid_not_symmetric(self):
        """Test avec matrice non symétrique."""
        invalid = np.array([
            [1.0, 0.5],
            [0.3, 1.0]  # Différent de 0.5
        ])
        
        with pytest.raises(ValueError, match="symétrique"):
            correlation_matrix(invalid, 2)
    
    def test_invalid_diagonal(self):
        """Test avec diagonale différente de 1."""
        invalid = np.array([
            [1.0, 0.5],
            [0.5, 0.9]  # Devrait être 1.0
        ])
        
        with pytest.raises(ValueError, match="diagonale"):
            correlation_matrix(invalid, 2)


class TestCholeskyDecomposition:
    """Tests pour cholesky_decomposition."""
    
    def test_basic(self):
        """Test basique de décomposition."""
        C = correlation_matrix(0.5, 2)
        L = cholesky_decomposition(C)
        
        # Vérifier L @ L.T = C
        np.testing.assert_allclose(L @ L.T, C, atol=1e-10)
    
    def test_triangular(self):
        """Test que L est triangulaire inférieure."""
        C = correlation_matrix(0.3, 3)
        L = cholesky_decomposition(C)
        
        # Partie supérieure doit être nulle
        assert np.allclose(np.triu(L, k=1), 0)


class TestSimulateCorrelatedNormalVectors:
    """Tests pour simulate_correlated_normal_vectors."""
    
    def test_shape(self):
        """Test que la forme est correcte."""
        C = correlation_matrix(0.5, 3)
        samples = simulate_correlated_normal_vectors(100, C, seed=42)
        
        assert samples.shape == (100, 3)
    
    def test_correlation_empirical(self):
        """Test que la corrélation empirique est proche de la théorique."""
        C = correlation_matrix(0.6, 3)
        samples = simulate_correlated_normal_vectors(10000, C, seed=42)
        
        empirical_corr = np.corrcoef(samples.T)
        np.testing.assert_allclose(empirical_corr, C, atol=0.05)


# ============================================================================
# TESTS : ANTITHETIC VARIATES
# ============================================================================

class TestAntitheticVariates:
    """Tests pour antithetic_variates."""
    
    def test_opposite(self):
        """Test que z et -z sont opposés."""
        z, z_anti = antithetic_variates(100, seed=42)
        np.testing.assert_allclose(z, -z_anti)
    
    def test_zero_mean(self):
        """Test que la moyenne de (z + (-z))/2 est nulle."""
        z, z_anti = antithetic_variates(1000, seed=42)
        combined_mean = (z.mean() + z_anti.mean()) / 2
        
        assert abs(combined_mean) < 1e-10


# ============================================================================
# TESTS : VALIDATION
# ============================================================================

class TestValidation:
    """Tests pour les fonctions de validation."""
    
    def test_validate_positive(self):
        """Test de validate_positive."""
        validate_positive(1.0, "test")  # OK
        validate_positive(0.001, "test")  # OK
        
        with pytest.raises(ValueError, match="strictement positif"):
            validate_positive(0.0, "test")
        
        with pytest.raises(ValueError, match="strictement positif"):
            validate_positive(-1.0, "test")
    
    def test_validate_non_negative(self):
        """Test de validate_non_negative."""
        validate_non_negative(0.0, "test")  # OK
        validate_non_negative(1.0, "test")  # OK
        
        with pytest.raises(ValueError, match="non-négatif"):
            validate_non_negative(-0.01, "test")
    
    def test_validate_probability(self):
        """Test de validate_probability."""
        validate_probability(0.0, "test")  # OK
        validate_probability(0.5, "test")  # OK
        validate_probability(1.0, "test")  # OK
        
        with pytest.raises(ValueError, match="dans \\[0, 1\\]"):
            validate_probability(-0.1, "test")
        
        with pytest.raises(ValueError, match="dans \\[0, 1\\]"):
            validate_probability(1.1, "test")
    
    def test_validate_correlation(self):
        """Test de validate_correlation."""
        validate_correlation(-1.0, "test")  # OK
        validate_correlation(0.0, "test")  # OK
        validate_correlation(1.0, "test")  # OK
        
        with pytest.raises(ValueError, match="dans \\[-1, 1\\]"):
            validate_correlation(-1.1, "test")
        
        with pytest.raises(ValueError, match="dans \\[-1, 1\\]"):
            validate_correlation(1.5, "test")


# ============================================================================
# TESTS D'INTÉGRATION
# ============================================================================

class TestIntegration:
    """Tests d'intégration combinant plusieurs fonctions."""
    
    def test_correlated_gbm_paths(self):
        """Test de simulation de GBM corrélés."""
        # Matrice de corrélation
        C = correlation_matrix(0.5, 2)
        
        # Paramètres
        S0 = 100.0
        mu = 0.05
        sigma = 0.2
        T = 1.0
        n_steps = 252
        n_paths = 1000
        
        # Génération de chemins corrélés
        dt = T / n_steps
        L = cholesky_decomposition(C)
        
        # Browniens corrélés
        Z = simulate_correlated_normal_vectors(n_paths * n_steps, C, seed=42)
        Z = Z.reshape(n_paths, n_steps, 2)
        
        # Vérifier que la forme est correcte
        assert Z.shape == (n_paths, n_steps, 2)
        
        # Vérifier la corrélation
        corr_empirical = np.corrcoef(Z[:, :, 0].flatten(), Z[:, :, 1].flatten())[0, 1]
        assert abs(corr_empirical - 0.5) < 0.05
