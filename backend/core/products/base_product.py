"""
Classe de base abstraite pour tous les produits dérivés.

Cette classe définit l'interface commune pour tous les produits financiers
(options, swaps, swaptions, forwards, etc.).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ProductType(Enum):
    """Types de produits dérivés."""
    OPTION = "option"
    SWAP = "swap"
    SWAPTION = "swaption"
    FORWARD = "forward"
    BOND = "bond"
    CAP_FLOOR = "cap_floor"


class OptionType(Enum):
    """Types d'options."""
    CALL = "call"
    PUT = "put"


class ExerciseType(Enum):
    """Types d'exercice."""
    EUROPEAN = "european"
    AMERICAN = "american"
    BERMUDAN = "bermudan"


class BaseProduct(ABC):
    """
    Classe abstraite pour les produits dérivés.
    
    Attributes:
        product_type (ProductType): Type de produit
        maturity (float): Maturité en années
        notional (float): Notionnel du contrat
    """
    
    def __init__(
        self,
        product_type: ProductType,
        maturity: float,
        notional: float = 1.0
    ):
        """
        Initialise le produit.
        
        Args:
            product_type: Type de produit
            maturity: Maturité en années
            notional: Notionnel du contrat
            
        Raises:
            ValueError: Si les paramètres sont invalides
        """
        if maturity <= 0:
            raise ValueError("La maturité doit être strictement positive")
        if notional <= 0:
            raise ValueError("Le notionnel doit être strictement positif")
            
        self.product_type = product_type
        self.maturity = maturity
        self.notional = notional
    
    @abstractmethod
    def payoff(self, spot_price: float, **kwargs) -> float:
        """
        Calcule le payoff du produit.
        
        Args:
            spot_price: Prix du sous-jacent à maturité
            **kwargs: Paramètres additionnels spécifiques au produit
            
        Returns:
            Valeur du payoff
        """
        pass
    
    @abstractmethod
    def get_characteristics(self) -> Dict[str, Any]:
        """
        Retourne les caractéristiques du produit.
        
        Returns:
            Dictionnaire contenant les caractéristiques du produit
        """
        pass
    
    def get_time_to_maturity(self, current_date: Optional[datetime] = None) -> float:
        """
        Calcule le temps jusqu'à maturité.
        
        Args:
            current_date: Date actuelle (par défaut: aujourd'hui)
            
        Returns:
            Temps jusqu'à maturité en années
        """
        # Pour l'instant, on retourne simplement la maturité
        # Dans une implémentation complète, on calculerait la différence avec current_date
        return self.maturity
    
    def validate(self) -> bool:
        """
        Valide les paramètres du produit.
        
        Returns:
            True si le produit est valide
            
        Raises:
            ValueError: Si le produit est invalide
        """
        if self.maturity <= 0:
            raise ValueError("La maturité doit être strictement positive")
        if self.notional <= 0:
            raise ValueError("Le notionnel doit être strictement positif")
        return True
    
    def __repr__(self) -> str:
        """Représentation string du produit."""
        return (
            f"{self.__class__.__name__}("
            f"type={self.product_type.value}, "
            f"maturity={self.maturity}, "
            f"notional={self.notional})"
        )
    
    def __str__(self) -> str:
        """String lisible du produit."""
        return (
            f"{self.product_type.value.capitalize()} "
            f"(Maturité: {self.maturity} ans, Notionnel: {self.notional:,.0f})"
        )
