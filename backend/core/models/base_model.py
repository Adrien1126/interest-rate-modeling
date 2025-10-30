"""
Classe de base abstraite pour tous les modèles stochastiques.

Cette classe définit l'interface commune que doivent implémenter tous les modèles
de pricing (Black-Scholes, Heston, SABR, Hull-White, CIR, etc.).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np


class BaseModel(ABC):
    """
    Classe abstraite pour les modèles stochastiques.
    
    Attributes:
        name (str): Nom du modèle
        parameters (Dict[str, float]): Paramètres du modèle
    """
    
    def __init__(self, name: str, parameters: Optional[Dict[str, float]] = None):
        """
        Initialise le modèle.
        
        Args:
            name: Nom du modèle
            parameters: Dictionnaire des paramètres du modèle
        """
        self.name = name
        self.parameters = parameters.copy() if parameters is not None else {}
        self._validate_parameters()
    
    @abstractmethod
    def _validate_parameters(self) -> None:
        """
        Valide les paramètres du modèle.
        
        Raises:
            ValueError: Si les paramètres sont invalides
        """
        pass
    
    @abstractmethod
    def simulate(
        self, 
        S0: float, 
        T: float, 
        n_steps: int, 
        n_paths: int,
        random_seed: Optional[int] = None
    ) -> np.ndarray:
        """
        Simule des trajectoires selon le modèle.
        
        Args:
            S0: Valeur initiale du sous-jacent
            T: Maturité (en années)
            n_steps: Nombre de pas de temps
            n_paths: Nombre de trajectoires à simuler
            random_seed: Graine aléatoire pour reproductibilité
            
        Returns:
            Array de shape (n_paths, n_steps + 1) contenant les trajectoires simulées
        """
        pass
    
    @abstractmethod
    def characteristic_function(self, u: complex, t: float, **kwargs) -> complex:
        """
        Fonction caractéristique du modèle (pour méthodes de Fourier).
        
        Args:
            u: Argument complexe
            t: Temps
            **kwargs: Paramètres additionnels
            
        Returns:
            Valeur de la fonction caractéristique
        """
        pass
    
    def get_parameters(self) -> Dict[str, float]:
        """
        Retourne les paramètres du modèle.
        
        Returns:
            Dictionnaire des paramètres
        """
        return self.parameters.copy()
    
    def set_parameters(self, parameters: Dict[str, float]) -> None:
        """
        Met à jour les paramètres du modèle.
        
        Args:
            parameters: Nouveaux paramètres
            
        Raises:
            ValueError: Si les paramètres sont invalides
        """
        self.parameters.update(parameters)
        self._validate_parameters()
    
    def __repr__(self) -> str:
        """Représentation string du modèle."""
        params_str = ", ".join(f"{k}={v:.4f}" for k, v in self.parameters.items())
        return f"{self.__class__.__name__}({params_str})"
    
    def __str__(self) -> str:
        """String lisible du modèle."""
        return f"{self.name} avec paramètres: {self.parameters}"
