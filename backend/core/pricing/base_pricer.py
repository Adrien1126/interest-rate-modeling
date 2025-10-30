"""
Classe de base abstraite pour tous les pricers.

Cette classe définit l'interface commune pour tous les moteurs de pricing
(analytique, Monte Carlo, arbres binomiaux/trinomiaux, etc.).

Cette classe de base est GÉNÉRIQUE et ne fait aucune hypothèse sur le type de produit.
Les sensibilités (Greeks) sont gérées dans des classes spécialisées pour les options.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum

from backend.core.models.base_model import BaseModel
from backend.core.products.base_product import BaseProduct


class PricingMethod(Enum):
    """Méthodes de pricing disponibles."""
    ANALYTIC = "analytic"
    MONTE_CARLO = "monte_carlo"
    BINOMIAL_TREE = "binomial_tree"
    TRINOMIAL_TREE = "trinomial_tree"
    FINITE_DIFFERENCE = "finite_difference"
    FOURIER = "fourier"


class BasePricer(ABC):
    """
    Classe abstraite générique pour les pricers.
    
    Cette classe fournit uniquement la méthode price() qui est applicable
    à TOUS les produits dérivés (options, swaps, swaptions, bonds, etc.).
    
    Les sensibilités (Greeks) ne sont PAS dans cette classe car elles sont
    spécifiques aux options. Voir OptionPricer pour les Greeks.
    
    Attributes:
        model (BaseModel): Modèle stochastique utilisé
        method (PricingMethod): Méthode de pricing
    """
    
    def __init__(self, model: BaseModel, method: PricingMethod):
        """
        Initialise le pricer.
        
        Args:
            model: Modèle stochastique à utiliser
            method: Méthode de pricing
        """
        self.model = model
        self.method = method
    
    @abstractmethod
    def price(
        self,
        product: BaseProduct,
        spot: float,
        **kwargs
    ) -> float:
        """
        Calcule le prix du produit.
        
        Méthode abstraite à implémenter dans les classes concrètes.
        Cette méthode est GÉNÉRIQUE et s'applique à tous les produits.
        
        Args:
            product: Produit à pricer
            spot: Prix spot du sous-jacent
            **kwargs: Paramètres additionnels (date d'évaluation, etc.)
            
        Returns:
            Prix du produit
        """
        pass
    
    def get_pricing_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur le pricer.
        
        Returns:
            Dictionnaire avec les informations du pricer
        """
        return {
            'method': self.method.value,
            'model': self.model.name,
            'model_parameters': self.model.get_parameters()
        }
    
    def __repr__(self) -> str:
        """Représentation string du pricer."""
        return (
            f"{self.__class__.__name__}("
            f"model={self.model.name}, "
            f"method={self.method.value})"
        )
    
    def __str__(self) -> str:
        """String lisible du pricer."""
        return f"{self.method.value.capitalize()} pricer avec modèle {self.model.name}"
