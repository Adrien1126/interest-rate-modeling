"""
Pricer Monte Carlo pour options.

Implémentation du pricing par simulation Monte Carlo avec:
- Simulation de trajectoires du sous-jacent
- Réduction de variance par variables antithétiques
- Calcul d'intervalles de confiance
- Calcul numérique des Greeks par différences finies
"""

from typing import Optional, Dict, Any
import numpy as np
from scipy import stats

from backend.core.pricing.base_pricer import BasePricer, PricingMethod
from backend.core.models.base_model import BaseModel
from backend.core.products.base_product import BaseProduct
from backend.core.products.option import Option
from backend.core.products.base_product import ExerciseType


class MonteCarloPricer(BasePricer):
    """Pricer Monte Carlo pour produits dérivés."""
    
    def __init__(
        self,
        model: BaseModel,
        n_simulations: int = 10000,
        n_steps: int = 100,
        use_antithetic: bool = True,
        random_seed: Optional[int] = None
    ):
        super().__init__(model, PricingMethod.MONTE_CARLO)
        
        if n_simulations <= 0:
            raise ValueError("n_simulations doit être > 0")
        if n_steps <= 0:
            raise ValueError("n_steps doit être > 0")
        
        self.n_simulations = n_simulations
        self.n_steps = n_steps
        self.use_antithetic = use_antithetic
        self.random_seed = random_seed
        
        self._last_paths: Optional[np.ndarray] = None
        self._last_payoffs: Optional[np.ndarray] = None
        self._last_maturity: Optional[float] = None
    
    def _simulate_paths(self, spot: float, maturity: float) -> np.ndarray:
        """Simule les trajectoires du sous-jacent."""
        if self.use_antithetic:
            n_sims = self.n_simulations // 2
        else:
            n_sims = self.n_simulations
        
        paths = self.model.simulate(
            S0=spot,
            T=maturity,
            n_steps=self.n_steps,
            n_paths=n_sims,
            random_seed=self.random_seed
        )
        
        if self.use_antithetic:
            params = self.model.get_parameters()
            sigma = params['volatility']
            r = params['risk_free_rate']
            q = params.get('dividend_yield', 0.0)
            mu = r - q
            
            t = np.linspace(0, maturity, self.n_steps + 1)
            drift_term = (mu - 0.5 * sigma**2) * t
            
            log_returns = np.log(paths / spot)
            brownian = (log_returns - drift_term) / sigma
            
            log_returns_anti = drift_term - sigma * brownian
            paths_anti = spot * np.exp(log_returns_anti)
            
            paths = np.vstack([paths, paths_anti])
        
        self._last_paths = paths
        return paths
    
    def _compute_payoff(self, product: BaseProduct, final_prices: np.ndarray) -> np.ndarray:
        """Calcule le payoff du produit pour chaque simulation."""
        payoffs = np.array([product.payoff(price) for price in final_prices])
        self._last_payoffs = payoffs
        return payoffs
    
    def price(self, product: BaseProduct, spot: float, **kwargs) -> float:
        """Calcule le prix d'un produit par Monte Carlo."""
        if isinstance(product, Option):
            if product.exercise_type != ExerciseType.EUROPEAN:
                raise NotImplementedError(
                    f"Monte Carlo non implémenté pour {product.exercise_type.name}"
                )
        
        self._last_maturity = product.maturity
        paths = self._simulate_paths(spot, product.maturity)
        final_prices = paths[:, -1]
        payoffs = self._compute_payoff(product, final_prices)
        
        params = self.model.get_parameters()
        r = params.get('risk_free_rate', 0.0)
        discount_factor = np.exp(-r * product.maturity)
        
        price = np.mean(payoffs) * discount_factor
        return price
    
    def standard_error(self) -> Optional[float]:
        """Calcule l'erreur standard de la dernière estimation."""
        if self._last_payoffs is None or self._last_maturity is None:
            return None
        
        params = self.model.get_parameters()
        r = params.get('risk_free_rate', 0.0)
        
        discount_factor = np.exp(-r * self._last_maturity)
        discounted_payoffs = self._last_payoffs * discount_factor
        
        return np.std(discounted_payoffs, ddof=1) / np.sqrt(len(discounted_payoffs))
    
    def confidence_interval(
        self,
        product: BaseProduct,
        spot: float,
        confidence_level: float = 0.95
    ) -> Dict[str, float]:
        """Calcule l'intervalle de confiance du prix."""
        price = self.price(product, spot)
        std_error = self.standard_error()
        
        if std_error is None:
            std_error = 0.0
        
        z_score = stats.norm.ppf((1 + confidence_level) / 2)
        margin = z_score * std_error
        
        return {
            'price': float(price),
            'lower_bound': float(price - margin),
            'upper_bound': float(price + margin),
            'std_error': float(std_error),
            'confidence_level': confidence_level
        }
    
    def get_pricing_info(self) -> Dict[str, Any]:
        """Retourne les informations de configuration du pricer."""
        info = {
            'method': 'monte_carlo',
            'model': self.model.name,
            'n_simulations': self.n_simulations,
            'n_steps': self.n_steps,
            'use_antithetic': self.use_antithetic
        }
        if self.random_seed is not None:
            info['random_seed'] = self.random_seed
        return info
    
    def __repr__(self) -> str:
        return (
            f"MonteCarloPricer("
            f"model={self.model.name}, "
            f"n_simulations={self.n_simulations}, "
            f"n_steps={self.n_steps}, "
            f"antithetic={self.use_antithetic})"
        )


class MonteCarloOptionPricer(MonteCarloPricer):
    """Pricer Monte Carlo spécialisé pour les options."""
    
    def greeks(
        self,
        option: Option,
        spot: float,
        epsilon_spot: float = 0.01,
        epsilon_vol: float = 0.01,
        epsilon_time: float = 1/365
    ) -> Dict[str, float]:
        """Calcule les Greeks par différences finies numériques."""
        price = self.price(option, spot)
        
        # Delta
        dS = spot * epsilon_spot
        price_up = self.price(option, spot + dS)
        price_down = self.price(option, spot - dS)
        delta = (price_up - price_down) / (2 * dS)
        
        # Gamma
        gamma = (price_up - 2 * price + price_down) / (dS ** 2)
        
        # Vega
        params = self.model.get_parameters()
        original_vol = params['volatility']
        
        self.model.set_parameters({'volatility': original_vol + epsilon_vol})
        price_vol_up = self.price(option, spot)
        self.model.set_parameters({'volatility': original_vol})
        vega = (price_vol_up - price) / epsilon_vol / 100.0
        
        # Theta
        option_later = Option(
            strike=option.strike,
            maturity=max(option.maturity - epsilon_time, epsilon_time),
            option_type=option.option_type,
            exercise_type=option.exercise_type,
            notional=option.notional
        )
        price_later = self.price(option_later, spot)
        theta = (price_later - price) / epsilon_time
        
        # Rho
        original_r = params['risk_free_rate']
        epsilon_r = 0.01
        
        self.model.set_parameters({'risk_free_rate': original_r + epsilon_r})
        price_r_up = self.price(option, spot)
        self.model.set_parameters({'risk_free_rate': original_r})
        rho = (price_r_up - price) / epsilon_r / 100.0
        
        return {
            'delta': delta,
            'gamma': gamma,
            'vega': vega,
            'theta': theta,
            'rho': rho
        }
    
    def __repr__(self) -> str:
        return (
            f"MonteCarloOptionPricer("
            f"model={self.model.name}, "
            f"n_simulations={self.n_simulations}, "
            f"n_steps={self.n_steps}, "
            f"antithetic={self.use_antithetic})"
        )
