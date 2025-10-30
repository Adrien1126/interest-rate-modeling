"""
Implémentation de la classe Option (européenne et américaine).
"""

from typing import Dict, Any
import numpy as np

from backend.core.products.base_product import (
    BaseProduct,
    ProductType,
    OptionType,
    ExerciseType
)


class Option(BaseProduct):
    """
    Classe représentant une option (call ou put).
    
    Attributes:
        strike (float): Prix d'exercice (strike)
        option_type (OptionType): Type d'option (CALL ou PUT)
        exercise_type (ExerciseType): Type d'exercice (EUROPEAN, AMERICAN, etc.)
    """
    
    def __init__(
        self,
        strike: float,
        maturity: float,
        option_type: OptionType = OptionType.CALL,
        exercise_type: ExerciseType = ExerciseType.EUROPEAN,
        notional: float = 1.0
    ):
        """
        Initialise une option.
        
        Args:
            strike: Prix d'exercice
            maturity: Maturité en années
            option_type: CALL ou PUT
            exercise_type: EUROPEAN, AMERICAN ou BERMUDAN
            notional: Notionnel du contrat
            
        Raises:
            ValueError: Si les paramètres sont invalides
        """
        super().__init__(
            product_type=ProductType.OPTION,
            maturity=maturity,
            notional=notional
        )
        
        if strike <= 0:
            raise ValueError("Le strike doit être strictement positif")
        
        self.strike = strike
        self.option_type = option_type
        self.exercise_type = exercise_type
    
    def payoff(self, spot_price: float, **kwargs) -> float:
        """
        Calcule le payoff de l'option à maturité.
        
        Args:
            spot_price: Prix du sous-jacent à maturité
            **kwargs: Paramètres additionnels (non utilisés pour une option européenne)
            
        Returns:
            Valeur du payoff
        """
        if self.option_type == OptionType.CALL:
            intrinsic_value = max(spot_price - self.strike, 0)
        elif self.option_type == OptionType.PUT:
            intrinsic_value = max(self.strike - spot_price, 0)
        else:
            raise ValueError(f"Type d'option invalide: {self.option_type}")
        
        return self.notional * intrinsic_value
    
    def intrinsic_value(self, spot_price: float) -> float:
        """
        Calcule la valeur intrinsèque de l'option.
        
        Args:
            spot_price: Prix actuel du sous-jacent
            
        Returns:
            Valeur intrinsèque
        """
        return self.payoff(spot_price)
    
    def is_in_the_money(self, spot_price: float) -> bool:
        """
        Vérifie si l'option est dans la monnaie (ITM).
        
        Args:
            spot_price: Prix actuel du sous-jacent
            
        Returns:
            True si ITM, False sinon
        """
        if self.option_type == OptionType.CALL:
            return spot_price > self.strike
        else:  # PUT
            return spot_price < self.strike
    
    def is_at_the_money(self, spot_price: float, tolerance: float = 0.01) -> bool:
        """
        Vérifie si l'option est à la monnaie (ATM).
        
        Args:
            spot_price: Prix actuel du sous-jacent
            tolerance: Tolérance relative pour considérer ATM
            
        Returns:
            True si ATM, False sinon
        """
        return abs(spot_price - self.strike) / self.strike < tolerance
    
    def is_out_of_the_money(self, spot_price: float) -> bool:
        """
        Vérifie si l'option est hors de la monnaie (OTM).
        
        Args:
            spot_price: Prix actuel du sous-jacent
            
        Returns:
            True si OTM, False sinon
        """
        return not self.is_in_the_money(spot_price)
    
    def moneyness(self, spot_price: float) -> float:
        """
        Calcule le moneyness (S/K pour call, K/S pour put).
        
        Args:
            spot_price: Prix actuel du sous-jacent
            
        Returns:
            Valeur du moneyness
        """
        if self.option_type == OptionType.CALL:
            return spot_price / self.strike
        else:  # PUT
            return self.strike / spot_price
    
    def get_characteristics(self) -> Dict[str, Any]:
        """
        Retourne les caractéristiques de l'option.
        
        Returns:
            Dictionnaire des caractéristiques
        """
        return {
            'product_type': self.product_type.value,
            'option_type': self.option_type.value,
            'exercise_type': self.exercise_type.value,
            'strike': self.strike,
            'maturity': self.maturity,
            'notional': self.notional
        }
    
    def __repr__(self) -> str:
        """Représentation string de l'option."""
        return (
            f"Option("
            f"type={self.option_type.value}, "
            f"strike={self.strike}, "
            f"maturity={self.maturity}, "
            f"exercise={self.exercise_type.value})"
        )
    
    def __str__(self) -> str:
        """String lisible de l'option."""
        return (
            f"{self.option_type.value.upper()} {self.exercise_type.value.capitalize()} "
            f"(Strike: {self.strike}, Maturité: {self.maturity} ans)"
        )
