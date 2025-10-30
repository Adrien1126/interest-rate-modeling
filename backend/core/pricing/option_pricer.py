"""
Pricer spécialisé pour les options avec calcul des Greeks.

Cette classe hérite de BasePricer et ajoute les fonctionnalités spécifiques
aux options : calcul des sensibilités (Greeks).
"""

from typing import Dict
import numpy as np

from backend.core.pricing.base_pricer import BasePricer
from backend.core.products.option import Option


class OptionPricer(BasePricer):
    """
    Classe abstraite spécialisée pour le pricing d'options.
    
    Ajoute les méthodes de calcul des Greeks (delta, gamma, vega, theta, rho)
    par différences finies.
    
    Les classes concrètes (AnalyticOptionPricer, MonteCarloOptionPricer, etc.)
    doivent hériter de cette classe.
    """
    
    def greeks(
        self,
        option: Option,
        spot: float,
        **kwargs
    ) -> Dict[str, float]:
        """
        Calcule tous les Greeks par différences finies.
        
        Args:
            option: Option à analyser
            spot: Prix spot du sous-jacent
            **kwargs: Paramètres additionnels
            
        Returns:
            Dictionnaire contenant les Greeks (delta, gamma, vega, theta, rho)
        """
        return {
            'delta': self.delta(option, spot, **kwargs),
            'gamma': self.gamma(option, spot, **kwargs),
            'vega': self.vega(option, spot, **kwargs),
            'theta': self.theta(option, spot, **kwargs),
            'rho': self.rho(option, spot, **kwargs)
        }
    
    def delta(
        self,
        option: Option,
        spot: float,
        epsilon: float = 0.01,
        **kwargs
    ) -> float:
        """
        Calcule le delta par différences finies.
        
        Delta = ∂V/∂S (sensibilité au prix du sous-jacent)
        
        Args:
            option: Option à analyser
            spot: Prix spot
            epsilon: Perturbation relative pour le calcul numérique
            **kwargs: Paramètres additionnels
            
        Returns:
            Delta
        """
        h = spot * epsilon
        price_up = self.price(option, spot + h, **kwargs)
        price_down = self.price(option, spot - h, **kwargs)
        return (price_up - price_down) / (2 * h)
    
    def gamma(
        self,
        option: Option,
        spot: float,
        epsilon: float = 0.01,
        **kwargs
    ) -> float:
        """
        Calcule le gamma par différences finies.
        
        Gamma = ∂²V/∂S² (convexité par rapport au prix spot)
        
        Args:
            option: Option à analyser
            spot: Prix spot
            epsilon: Perturbation relative
            **kwargs: Paramètres additionnels
            
        Returns:
            Gamma
        """
        h = spot * epsilon
        price_up = self.price(option, spot + h, **kwargs)
        price_down = self.price(option, spot - h, **kwargs)
        price_mid = self.price(option, spot, **kwargs)
        return (price_up - 2 * price_mid + price_down) / (h ** 2)
    
    def vega(
        self,
        option: Option,
        spot: float,
        epsilon: float = 0.01,
        **kwargs
    ) -> float:
        """
        Calcule le vega par différences finies.
        
        Vega = ∂V/∂σ (sensibilité à la volatilité)
        
        Args:
            option: Option à analyser
            spot: Prix spot
            epsilon: Perturbation absolue sur la volatilité
            **kwargs: Paramètres additionnels
            
        Returns:
            Vega (pour 1% de volatilité)
        """
        # Sauvegarder la volatilité originale
        original_vol = self.model.parameters.get('volatility', 0.2)
        
        # Calcul avec vol + epsilon
        self.model.set_parameters({'volatility': original_vol + epsilon})
        price_up = self.price(option, spot, **kwargs)
        
        # Calcul avec vol - epsilon
        self.model.set_parameters({'volatility': original_vol - epsilon})
        price_down = self.price(option, spot, **kwargs)
        
        # Restaurer la volatilité originale
        self.model.set_parameters({'volatility': original_vol})
        
        # Vega pour 1% de volatilité
        return (price_up - price_down) / (2 * epsilon) / 100
    
    def theta(
        self,
        option: Option,
        spot: float,
        dt: float = 1/365,
        **kwargs
    ) -> float:
        """
        Calcule le theta (sensibilité au temps).
        
        Theta = -∂V/∂t (décroissance temporelle de l'option)
        
        Args:
            option: Option à analyser
            spot: Prix spot
            dt: Variation de temps (en années, par défaut 1 jour)
            **kwargs: Paramètres additionnels
            
        Returns:
            Theta (par jour)
        """
        # Prix actuel
        price_now = self.price(option, spot, **kwargs)
        
        # Réduire la maturité
        original_maturity = option.maturity
        option.maturity = max(0, original_maturity - dt)
        price_later = self.price(option, spot, **kwargs)
        
        # Restaurer la maturité
        option.maturity = original_maturity
        
        # Theta est négatif (décroissance de valeur)
        return (price_later - price_now) / dt
    
    def rho(
        self,
        option: Option,
        spot: float,
        epsilon: float = 0.0001,
        **kwargs
    ) -> float:
        """
        Calcule le rho par différences finies.
        
        Rho = ∂V/∂r (sensibilité au taux sans risque)
        
        Args:
            option: Option à analyser
            spot: Prix spot
            epsilon: Perturbation absolue sur le taux (0.01% par défaut)
            **kwargs: Paramètres additionnels
            
        Returns:
            Rho (pour 1% de taux)
        """
        # Sauvegarder le taux original
        original_rate = self.model.parameters.get('risk_free_rate', 0.05)
        
        # Calcul avec taux + epsilon
        self.model.set_parameters({'risk_free_rate': original_rate + epsilon})
        price_up = self.price(option, spot, **kwargs)
        
        # Calcul avec taux - epsilon
        self.model.set_parameters({'risk_free_rate': original_rate - epsilon})
        price_down = self.price(option, spot, **kwargs)
        
        # Restaurer le taux original
        self.model.set_parameters({'risk_free_rate': original_rate})
        
        # Rho pour 1% de taux
        return (price_up - price_down) / (2 * epsilon) / 100
