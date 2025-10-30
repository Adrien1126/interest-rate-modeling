"""
Implémentation du modèle Black-Scholes.

Modèle classique pour le pricing d'options sur actions/indices.
"""

import numpy as np
from typing import Dict, Optional
from scipy.stats import norm
from backend.core.utils.stochastic_utils import geometric_brownian_path

from backend.core.models.base_model import BaseModel


class BlackScholesModel(BaseModel):
    """
    Modèle Black-Scholes pour le pricing d'options.
    
    Le modèle suppose que le prix du sous-jacent suit:
    dS(t) = r * S(t) * dt + σ * S(t) * dW(t)
    
    Paramètres requis:
        - volatility (σ): Volatilité constante
        - risk_free_rate (r): Taux sans risque
        - dividend_yield (q): Taux de dividende (optionnel, défaut: 0)
    """
    
    def __init__(
        self,
        volatility: float,
        risk_free_rate: float,
        dividend_yield: float = 0.0
    ):
        """
        Initialise le modèle Black-Scholes.
        
        Args:
            volatility: Volatilité (σ > 0)
            risk_free_rate: Taux sans risque
            dividend_yield: Taux de dividende (défaut: 0)
        """
        parameters = {
            'volatility': volatility,
            'risk_free_rate': risk_free_rate,
            'dividend_yield': dividend_yield
        }
        super().__init__(name="Black-Scholes", parameters=parameters)
    
    def _validate_parameters(self) -> None:
        """Valide les paramètres du modèle."""
        vol = self.parameters.get('volatility')
        if vol is None or vol <= 0:
            raise ValueError("La volatilité doit être strictement positive")
        
        # Les taux peuvent être négatifs (taux négatifs possibles en réalité)
        if 'risk_free_rate' not in self.parameters:
            raise ValueError("Le taux sans risque est requis")
    
    def simulate(
        self,
        S0: float,
        T: float,
        n_steps: int,
        n_paths: int = 1,
        random_seed: Optional[int] = None
    ) -> np.ndarray:
        """
        Simule des trajectoires de prix selon le modèle Black-Scholes.
        
        Utilise la solution exacte du mouvement brownien géométrique via
        stochastic_utils.geometric_brownian_path().
        
        Args:
            S0: Prix initial
            T: Maturité
            n_steps: Nombre de pas de temps
            n_paths: Nombre de trajectoires
            random_seed: Graine aléatoire
            
        Returns:
            Array (n_paths, n_steps + 1) de trajectoires
        """
        sigma = self.parameters['volatility']
        r = self.parameters['risk_free_rate']
        q = self.parameters.get('dividend_yield', 0.0)
        
        # Drift effectif (r - q)
        mu = r - q
        
        # Utilisation de la fonction réutilisable
        return geometric_brownian_path(
            S0=S0,
            mu=mu,
            sigma=sigma,
            T=T,
            n_steps=n_steps,
            n_paths=n_paths,
            seed=random_seed
        )
    
    def characteristic_function(self, u: complex, t: float, **kwargs) -> complex:
        """
        Fonction caractéristique du log-prix sous Black-Scholes.
        
        Args:
            u: Argument complexe
            t: Temps
            **kwargs: Paramètres additionnels (S0, r, q)
            
        Returns:
            Valeur de la fonction caractéristique
        """
        S0 = kwargs.get('S0', 100.0)
        r = self.parameters['risk_free_rate']
        q = self.parameters.get('dividend_yield', 0.0)
        sigma = self.parameters['volatility']
        
        # ln(S_t) ~ N(ln(S0) + (r-q-σ²/2)t, σ²t)
        mu = np.log(S0) + (r - q - 0.5 * sigma**2) * t
        var = sigma**2 * t
        
        # CF de loi normale: exp(iuμ - u²σ²/2)
        return np.exp(1j * u * mu - 0.5 * u**2 * var)
    
    def _compute_d1_d2(
        self,
        S: float,
        K: float,
        T: float
    ) -> tuple[float, float]:
        """
        Calcule d1 et d2 pour les formules de Black-Scholes.
        
        Méthode privée utilisée par black_scholes_price() et black_scholes_greeks()
        pour éviter la duplication de code.
        
        Args:
            S: Prix spot
            K: Strike
            T: Maturité
            
        Returns:
            Tuple (d1, d2)
        """
        r = self.parameters['risk_free_rate']
        q = self.parameters.get('dividend_yield', 0.0)
        sigma = self.parameters['volatility']
        
        d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        return d1, d2
    
    def black_scholes_price(
        self,
        S: float,
        K: float,
        T: float,
        option_type: str = 'call'
    ) -> float:
        """
        Formule analytique de Black-Scholes.
        
        Args:
            S: Prix spot
            K: Strike
            T: Maturité
            option_type: 'call' ou 'put'
            
        Returns:
            Prix de l'option
        """
        r = self.parameters['risk_free_rate']
        q = self.parameters.get('dividend_yield', 0.0)
        sigma = self.parameters['volatility']
        
        if T <= 0:
            # Payoff intrinsèque
            if option_type.lower() == 'call':
                return max(S - K, 0)
            else:
                return max(K - S, 0)
        
        # Calcul de d1 et d2 (factorisation)
        d1, d2 = self._compute_d1_d2(S, K, T)
        
        if option_type.lower() == 'call':
            price = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        elif option_type.lower() == 'put':
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)
        else:
            raise ValueError(f"Type d'option invalide: {option_type}")
        
        return price
    
    def black_scholes_greeks(
        self,
        S: float,
        K: float,
        T: float,
        option_type: str = 'call'
    ) -> Dict[str, float]:
        """
        Calcule les Greeks analytiquement.
        
        Args:
            S: Prix spot
            K: Strike
            T: Maturité
            option_type: 'call' ou 'put'
            
        Returns:
            Dictionnaire des Greeks
        """
        r = self.parameters['risk_free_rate']
        q = self.parameters.get('dividend_yield', 0.0)
        sigma = self.parameters['volatility']
        
        if T <= 0:
            return {
                'delta': 0.0,
                'gamma': 0.0,
                'vega': 0.0,
                'theta': 0.0,
                'rho': 0.0
            }
        
        # Calcul de d1 et d2 (factorisation)
        d1, d2 = self._compute_d1_d2(S, K, T)
        
        # Densité normale
        phi_d1 = norm.pdf(d1)
        
        # Greeks communs
        gamma = phi_d1 * np.exp(-q * T) / (S * sigma * np.sqrt(T))
        vega = S * np.exp(-q * T) * phi_d1 * np.sqrt(T) / 100  # Divisé par 100 pour 1% de vol
        
        if option_type.lower() == 'call':
            delta = np.exp(-q * T) * norm.cdf(d1)
            theta = (
                -S * phi_d1 * sigma * np.exp(-q * T) / (2 * np.sqrt(T))
                - r * K * np.exp(-r * T) * norm.cdf(d2)
                + q * S * np.exp(-q * T) * norm.cdf(d1)
            ) / 365  # Par jour
            rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100  # Pour 1% de taux
        else:  # put
            delta = -np.exp(-q * T) * norm.cdf(-d1)
            theta = (
                -S * phi_d1 * sigma * np.exp(-q * T) / (2 * np.sqrt(T))
                + r * K * np.exp(-r * T) * norm.cdf(-d2)
                - q * S * np.exp(-q * T) * norm.cdf(-d1)
            ) / 365
            rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100
        
        return {
            'delta': delta,
            'gamma': gamma,
            'vega': vega,
            'theta': theta,
            'rho': rho
        }
