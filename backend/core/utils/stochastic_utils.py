"""
Utilitaires pour les processus stochastiques.

Ce module fournit des fonctions de base réutilisables pour :
- Simulation de lois de probabilité
- Génération de chemins browniens
- Génération de variables aléatoires corrélées
- Discrétisation temporelle

Principe DRY : ces fonctions sont utilisées par tous les modèles et simulateurs
pour éviter la duplication de code.
"""

import numpy as np
from typing import Optional, Tuple, Union
from numpy.typing import NDArray


# ============================================================================
# SIMULATION DE LOIS DE PROBABILITÉ
# ============================================================================

def simulate_normal(
    size: Union[int, Tuple[int, ...]],
    mean: float = 0.0,
    std: float = 1.0,
    seed: Optional[int] = None
) -> NDArray[np.float64]:
    """
    Simule une loi normale.
    
    Args:
        size: Dimension des échantillons (int ou tuple)
        mean: Moyenne de la loi normale
        std: Écart-type de la loi normale
        seed: Graine pour la reproductibilité (optionnel)
        
    Returns:
        Array de variables aléatoires normales
        
    Example:
        >>> z = simulate_normal(1000, mean=0, std=1)
        >>> z.shape
        (1000,)
        >>> abs(z.mean()) < 0.1  # Proche de 0
        True
    """
    if seed is not None:
        np.random.seed(seed)
    
    return np.random.normal(loc=mean, scale=std, size=size)


def simulate_uniform(
    size: Union[int, Tuple[int, ...]],
    low: float = 0.0,
    high: float = 1.0,
    seed: Optional[int] = None
) -> NDArray[np.float64]:
    """
    Simule une loi uniforme.
    
    Args:
        size: Dimension des échantillons
        low: Borne inférieure
        high: Borne supérieure
        seed: Graine pour la reproductibilité
        
    Returns:
        Array de variables aléatoires uniformes
    """
    if seed is not None:
        np.random.seed(seed)
    
    return np.random.uniform(low=low, high=high, size=size)


def simulate_correlated_normals(
    size: int,
    correlation: float,
    seed: Optional[int] = None
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Simule deux lois normales corrélées.
    
    Utilise la décomposition de Cholesky pour générer deux variables
    normales avec une corrélation donnée.
    
    Args:
        size: Nombre d'échantillons
        correlation: Coefficient de corrélation entre -1 et 1
        seed: Graine pour la reproductibilité
        
    Returns:
        Tuple (Z1, Z2) de deux arrays corrélés
        
    Raises:
        ValueError: Si correlation n'est pas dans [-1, 1]
        
    Example:
        >>> z1, z2 = simulate_correlated_normals(10000, correlation=0.5)
        >>> np.corrcoef(z1, z2)[0, 1]  # doctest: +SKIP
        0.498  # Proche de 0.5
    """
    if not -1 <= correlation <= 1:
        raise ValueError(f"Corrélation doit être dans [-1, 1], reçu: {correlation}")
    
    if seed is not None:
        np.random.seed(seed)
    
    # Deux normales indépendantes
    z1 = np.random.normal(0, 1, size)
    z2_indep = np.random.normal(0, 1, size)
    
    # Décomposition de Cholesky
    z2 = correlation * z1 + np.sqrt(1 - correlation**2) * z2_indep
    
    return z1, z2


# ============================================================================
# MOUVEMENT BROWNIEN
# ============================================================================

def brownian_path(
    n_steps: int,
    dt: float,
    n_paths: int = 1,
    seed: Optional[int] = None
) -> NDArray[np.float64]:
    """
    Génère des chemins de mouvement brownien standard.
    
    Simule W(t) où dW(t) = sqrt(dt) * Z avec Z ~ N(0,1).
    
    Args:
        n_steps: Nombre de pas de temps
        dt: Pas de temps
        n_paths: Nombre de chemins à simuler
        seed: Graine pour la reproductibilité
        
    Returns:
        Array de forme (n_paths, n_steps+1) avec W(0) = 0
        
    Example:
        >>> paths = brownian_path(100, 0.01, n_paths=3)
        >>> paths.shape
        (3, 101)
        >>> np.allclose(paths[:, 0], 0)  # W(0) = 0
        True
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Incréments browniens
    dW = np.random.normal(0, np.sqrt(dt), size=(n_paths, n_steps))
    
    # Cumul pour obtenir le chemin
    W = np.zeros((n_paths, n_steps + 1))
    W[:, 1:] = np.cumsum(dW, axis=1)
    
    return W


def geometric_brownian_path(
    S0: float,
    mu: float,
    sigma: float,
    T: float,
    n_steps: int,
    n_paths: int = 1,
    seed: Optional[int] = None
) -> NDArray[np.float64]:
    """
    Génère des chemins de mouvement brownien géométrique.
    
    Simule S(t) solution de dS(t) = μ S(t) dt + σ S(t) dW(t).
    Utilise la solution exacte : S(t) = S0 * exp((μ - σ²/2)t + σ W(t)).
    
    Args:
        S0: Valeur initiale
        mu: Drift
        sigma: Volatilité
        T: Maturité
        n_steps: Nombre de pas de temps
        n_paths: Nombre de chemins
        seed: Graine pour la reproductibilité
        
    Returns:
        Array de forme (n_paths, n_steps+1) des chemins de prix
        
    Example:
        >>> paths = geometric_brownian_path(100, 0.05, 0.2, 1.0, 252, n_paths=5)
        >>> paths.shape
        (5, 253)
        >>> np.allclose(paths[:, 0], 100)  # S(0) = S0
        True
    """
    dt = T / n_steps
    
    # Génération du brownien
    W = brownian_path(n_steps, dt, n_paths, seed)
    
    # Grille temporelle
    t = np.linspace(0, T, n_steps + 1)
    
    # Solution exacte du GBM
    S = S0 * np.exp((mu - 0.5 * sigma**2) * t + sigma * W)
    
    return S


def brownian_bridge(
    start: float,
    end: float,
    n_steps: int,
    n_paths: int = 1,
    seed: Optional[int] = None
) -> NDArray[np.float64]:
    """
    Génère un pont brownien entre deux valeurs.
    
    Un pont brownien est un mouvement brownien conditionné à W(0) = start
    et W(T) = end.
    
    Args:
        start: Valeur initiale
        end: Valeur finale
        n_steps: Nombre de pas de temps
        n_paths: Nombre de chemins
        seed: Graine pour la reproductibilité
        
    Returns:
        Array de forme (n_paths, n_steps+1)
        
    Example:
        >>> bridge = brownian_bridge(0, 1, 100, n_paths=10)
        >>> np.allclose(bridge[:, 0], 0)  # Start = 0
        True
        >>> np.allclose(bridge[:, -1], 1)  # End = 1
        True
    """
    if seed is not None:
        np.random.seed(seed)
    
    dt = 1.0 / n_steps
    
    # Brownien standard
    W = brownian_path(n_steps, dt, n_paths, seed)
    
    # Grille temporelle
    t = np.linspace(0, 1, n_steps + 1)
    
    # Transformation en pont brownien
    # B(t) = W(t) - t * W(1) + start + t * (end - start)
    bridge = W - t * W[:, -1:] + start + t * (end - start)
    
    return bridge


# ============================================================================
# DISCRÉTISATION TEMPORELLE
# ============================================================================

def time_grid(
    T: float,
    n_steps: int,
    include_zero: bool = True
) -> NDArray[np.float64]:
    """
    Crée une grille temporelle uniforme.
    
    Args:
        T: Maturité finale
        n_steps: Nombre de pas de temps
        include_zero: Inclure t=0 dans la grille
        
    Returns:
        Array des temps
        
    Example:
        >>> grid = time_grid(1.0, 4, include_zero=True)
        >>> grid
        array([0.  , 0.25, 0.5 , 0.75, 1.  ])
    """
    if include_zero:
        return np.linspace(0, T, n_steps + 1)
    else:
        return np.linspace(T / n_steps, T, n_steps)


def time_step(T: float, n_steps: int) -> float:
    """
    Calcule le pas de temps.
    
    Args:
        T: Maturité
        n_steps: Nombre de pas
        
    Returns:
        Pas de temps dt
        
    Example:
        >>> time_step(1.0, 100)
        0.01
    """
    return T / n_steps


# ============================================================================
# MATRICE DE CORRÉLATION
# ============================================================================

def correlation_matrix(rho: Union[float, NDArray[np.float64]], n: int) -> NDArray[np.float64]:
    """
    Crée une matrice de corrélation.
    
    Args:
        rho: Corrélation uniforme (float) ou matrice de corrélation complète
        n: Dimension de la matrice (si rho est un float)
        
    Returns:
        Matrice de corrélation n x n
        
    Raises:
        ValueError: Si la matrice n'est pas symétrique définie positive
        
    Example:
        >>> corr = correlation_matrix(0.5, 3)
        >>> corr
        array([[1. , 0.5, 0.5],
               [0.5, 1. , 0.5],
               [0.5, 0.5, 1. ]])
    """
    if isinstance(rho, (int, float)):
        # Corrélation uniforme
        C = np.full((n, n), rho)
        np.fill_diagonal(C, 1.0)
    else:
        C = np.array(rho)
        
        # Vérifications
        if C.shape[0] != C.shape[1]:
            raise ValueError("La matrice de corrélation doit être carrée")
        
        if not np.allclose(C, C.T):
            raise ValueError("La matrice de corrélation doit être symétrique")
        
        if not np.allclose(np.diag(C), 1.0):
            raise ValueError("La diagonale doit être égale à 1")
    
    # Vérifier que la matrice est définie positive
    eigenvalues = np.linalg.eigvalsh(C)
    if np.any(eigenvalues < -1e-10):
        raise ValueError("La matrice de corrélation doit être définie positive")
    
    return C


def cholesky_decomposition(correlation_matrix: NDArray[np.float64]) -> NDArray[np.float64]:
    """
    Décomposition de Cholesky d'une matrice de corrélation.
    
    Utilisée pour générer des variables aléatoires corrélées.
    
    Args:
        correlation_matrix: Matrice de corrélation n x n
        
    Returns:
        Matrice triangulaire inférieure L telle que L @ L.T = correlation_matrix
        
    Example:
        >>> C = correlation_matrix(0.5, 2)
        >>> L = cholesky_decomposition(C)
        >>> np.allclose(L @ L.T, C)
        True
    """
    try:
        return np.linalg.cholesky(correlation_matrix)
    except np.linalg.LinAlgError:
        raise ValueError(
            "Impossible de calculer la décomposition de Cholesky. "
            "La matrice n'est pas définie positive."
        )


def simulate_correlated_normal_vectors(
    n_samples: int,
    correlation_matrix: NDArray[np.float64],
    seed: Optional[int] = None
) -> NDArray[np.float64]:
    """
    Simule des vecteurs de lois normales corrélées.
    
    Args:
        n_samples: Nombre d'échantillons
        correlation_matrix: Matrice de corrélation n x n
        seed: Graine pour la reproductibilité
        
    Returns:
        Array de forme (n_samples, n) de vecteurs corrélés
        
    Example:
        >>> C = correlation_matrix(0.5, 3)
        >>> samples = simulate_correlated_normal_vectors(1000, C, seed=42)
        >>> samples.shape
        (1000, 3)
        >>> empirical_corr = np.corrcoef(samples.T)
        >>> np.allclose(empirical_corr, C, atol=0.1)  # doctest: +SKIP
        True
    """
    if seed is not None:
        np.random.seed(seed)
    
    n = correlation_matrix.shape[0]
    
    # Décomposition de Cholesky
    L = cholesky_decomposition(correlation_matrix)
    
    # Normales indépendantes
    Z = np.random.normal(0, 1, size=(n_samples, n))
    
    # Application de la corrélation
    return Z @ L.T


# ============================================================================
# ANTITHETIC VARIATES
# ============================================================================

def antithetic_variates(
    size: Union[int, Tuple[int, ...]],
    seed: Optional[int] = None
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Génère des variables antithétiques pour la réduction de variance.
    
    Simule Z et -Z où Z ~ N(0,1) pour réduire la variance des estimateurs
    Monte Carlo.
    
    Args:
        size: Dimension des échantillons
        seed: Graine pour la reproductibilité
        
    Returns:
        Tuple (Z, -Z) de variables antithétiques
        
    Example:
        >>> z, z_anti = antithetic_variates(1000, seed=42)
        >>> np.allclose(z, -z_anti)
        True
        >>> (z.mean() + z_anti.mean()) / 2  # Moyenne proche de 0
        0.0
    """
    z = simulate_normal(size, seed=seed)
    return z, -z


# ============================================================================
# VALIDATION
# ============================================================================

def validate_positive(value: float, name: str) -> None:
    """Valide qu'une valeur est strictement positive."""
    if value <= 0:
        raise ValueError(f"{name} doit être strictement positif, reçu: {value}")


def validate_non_negative(value: float, name: str) -> None:
    """Valide qu'une valeur est non-négative."""
    if value < 0:
        raise ValueError(f"{name} doit être non-négatif, reçu: {value}")


def validate_probability(value: float, name: str) -> None:
    """Valide qu'une valeur est une probabilité (dans [0, 1])."""
    if not 0 <= value <= 1:
        raise ValueError(f"{name} doit être dans [0, 1], reçu: {value}")


def validate_correlation(value: float, name: str) -> None:
    """Valide qu'une valeur est une corrélation (dans [-1, 1])."""
    if not -1 <= value <= 1:
        raise ValueError(f"{name} doit être dans [-1, 1], reçu: {value}")
