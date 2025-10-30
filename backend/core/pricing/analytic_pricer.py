"""
Pricer analytique GÉNÉRIQUE pour les produits dérivés.

Utilise des formules fermées (closed-form) quand elles sont disponibles.
Cette classe est générique et peut pricer tous types de produits.

Pour les Greeks des options, voir OptionPricer et ses implémentations.
"""

from typing import Dict, Optional
import numpy as np

from backend.core.pricing.base_pricer import BasePricer, PricingMethod
from backend.core.models.base_model import BaseModel
from backend.core.models.black_scholes import BlackScholesModel
from backend.core.products.base_product import BaseProduct
from backend.core.products.option import Option


class AnalyticPricer(BasePricer):
    """
    Pricer générique utilisant des formules analytiques.
    
    Supporte:
    - Options européennes avec Black-Scholes
    - Swaps (à implémenter)
    - Bonds (à implémenter)
    - Extensions futures pour d'autres modèles
    
    Note: Cette classe ne fournit QUE la méthode price().
    Pour les Greeks, utilisez AnalyticOptionPricer.
    """
    
    def __init__(self, model: BaseModel):
        """
        Initialise le pricer analytique.
        
        Args:
            model: Modèle stochastique à utiliser
        """
        super().__init__(model=model, method=PricingMethod.ANALYTIC)
    
    def price(
        self,
        product: BaseProduct,
        spot: float,
        **kwargs
    ) -> float:
        """
        Calcule le prix du produit de manière analytique.
        
        Args:
            product: Produit à pricer
            spot: Prix spot du sous-jacent
            **kwargs: Paramètres additionnels
            
        Returns:
            Prix du produit
            
        Raises:
            NotImplementedError: Si aucune formule analytique n'existe
        """
        # Pricing d'une option avec Black-Scholes
        if isinstance(product, Option) and isinstance(self.model, BlackScholesModel):
            return self._price_option_black_scholes(product, spot, **kwargs)
        
        raise NotImplementedError(
            f"Pas de formule analytique pour {product.__class__.__name__} "
            f"avec le modèle {self.model.__class__.__name__}"
        )
    
    def _price_option_black_scholes(
        self,
        option: Option,
        spot: float,
        **kwargs
    ) -> float:
        """
        Price une option avec la formule de Black-Scholes.
        
        Args:
            option: Option à pricer
            spot: Prix spot
            **kwargs: Paramètres additionnels
            
        Returns:
            Prix de l'option
        """
        return self.model.black_scholes_price(
            S=spot,
            K=option.strike,
            T=option.maturity,
            option_type=option.option_type.value
        ) * option.notional
    
    def __repr__(self) -> str:
        """Représentation string du pricer."""
        return f"AnalyticPricer(model={self.model.name})"


class AnalyticOptionPricer(AnalyticPricer):
    """
    Pricer analytique spécialisé pour les options avec calcul des Greeks.
    
    Hérite de AnalyticPricer pour le pricing et ajoute les Greeks analytiques.
    """
    
    def greeks(
        self,
        option: Option,
        spot: float,
        **kwargs
    ) -> Dict[str, float]:
        """
        Calcule les Greeks analytiquement avec Black-Scholes.
        
        Args:
            option: Option à analyser
            spot: Prix spot
            **kwargs: Paramètres additionnels
            
        Returns:
            Dictionnaire des Greeks
            
        Raises:
            NotImplementedError: Si le modèle n'est pas Black-Scholes
        """
        if isinstance(self.model, BlackScholesModel):
            greeks = self.model.black_scholes_greeks(
                S=spot,
                K=option.strike,
                T=option.maturity,
                option_type=option.option_type.value
            )
            
            # Ajuster par le notionnel
            for key in greeks:
                greeks[key] *= option.notional
            
            return greeks
        
        raise NotImplementedError(
            f"Greeks analytiques non implémentés pour {self.model.__class__.__name__}"
        )
    
    def implied_volatility(
        self,
        option: Option,
        spot: float,
        market_price: float,
        initial_guess: float = 0.2,
        max_iterations: int = 100,
        tolerance: float = 1e-6
    ) -> Optional[float]:
        """
        Calcule la volatilité implicite par méthode de Newton-Raphson.
        
        La volatilité implicite est la volatilité qui, lorsqu'elle est utilisée
        dans le modèle de pricing, reproduit le prix de marché observé.
        
        Args:
            option: Option à analyser
            spot: Prix spot
            market_price: Prix de marché observé
            initial_guess: Estimation initiale de la volatilité
            max_iterations: Nombre maximum d'itérations
            tolerance: Tolérance pour la convergence
            
        Returns:
            Volatilité implicite, ou None si pas de convergence
            
        Raises:
            NotImplementedError: Si le modèle n'est pas Black-Scholes
        """
        if not isinstance(self.model, BlackScholesModel):
            raise NotImplementedError(
                "Volatilité implicite uniquement implémentée pour Black-Scholes"
            )
        
        # Sauvegarder la volatilité originale
        original_vol = self.model.parameters['volatility']
        
        vol = initial_guess
        
        for _ in range(max_iterations):
            # Calculer le prix avec la volatilité courante
            self.model.set_parameters({'volatility': vol})
            price = self.price(option, spot)
            
            # Vérifier la convergence
            if abs(price - market_price) < tolerance:
                self.model.set_parameters({'volatility': original_vol})
                return vol
            
            # Calculer le vega pour Newton-Raphson
            greeks = self.greeks(option, spot)
            vega = greeks['vega'] * 100  # Ramener à la variation pour 1 (pas 1%)
            
            if abs(vega) < 1e-10:
                # Vega trop petit, risque de division par zéro
                break
            
            # Mise à jour de Newton-Raphson
            vol = vol - (price - market_price) / vega
            
            # S'assurer que vol reste positif
            vol = max(vol, 0.001)
        
        # Pas de convergence
        self.model.set_parameters({'volatility': original_vol})
        return None
    
    def __repr__(self) -> str:
        """Représentation string du pricer."""
        return f"AnalyticOptionPricer(model={self.model.name})"
