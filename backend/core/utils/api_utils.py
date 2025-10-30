"""
Utilitaires communs pour les routes API.

Fonctions réutilisables pour la gestion d'erreurs, validation, etc.
"""

from fastapi import HTTPException, status
from typing import Optional, Callable, TypeVar, Any
from functools import wraps
import time

T = TypeVar('T')


def validate_required_param(
    value: Optional[Any],
    param_name: str,
    context: str = ""
) -> None:
    """
    Valide qu'un paramètre requis n'est pas None.
    
    Args:
        value: Valeur à valider
        param_name: Nom du paramètre
        context: Contexte supplémentaire (ex: "pour le modèle Black-Scholes")
        
    Raises:
        HTTPException: Si la valeur est None
    """
    if value is None:
        detail = f"{param_name} est requis"
        if context:
            detail += f" {context}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


def validate_product_type(
    actual_type: str,
    expected_type: str,
    detail: Optional[str] = None
) -> None:
    """
    Valide que le type de produit correspond à celui attendu.
    
    Args:
        actual_type: Type reçu
        expected_type: Type attendu
        detail: Message d'erreur personnalisé
        
    Raises:
        HTTPException: Si les types ne correspondent pas
    """
    if actual_type != expected_type:
        error_detail = detail or f"Le produit doit être de type '{expected_type}', reçu: '{actual_type}'"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail
        )


def handle_api_error(error: Exception, context: str = "opération") -> HTTPException:
    """
    Convertit une exception en HTTPException appropriée.
    
    Args:
        error: Exception à traiter
        context: Contexte de l'erreur (ex: "pricing", "validation")
        
    Returns:
        HTTPException appropriée
    """
    if isinstance(error, HTTPException):
        return error
    elif isinstance(error, ValueError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur de validation lors de {context}: {str(error)}"
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne lors de {context}: {str(error)}"
        )


def time_execution(func: Callable[..., T]) -> Callable[..., tuple[T, float]]:
    """
    Décorateur pour mesurer le temps d'exécution d'une fonction.
    
    Args:
        func: Fonction à mesurer
        
    Returns:
        Tuple (résultat, temps_ms)
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> tuple[T, float]:
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time_ms = (time.time() - start_time) * 1000
        return result, execution_time_ms
    
    return wrapper


class ModelFactory:
    """Factory pour créer des modèles stochastiques."""
    
    @staticmethod
    def create_black_scholes(
        volatility: Optional[float],
        risk_free_rate: Optional[float],
        dividend_yield: Optional[float] = 0.0
    ):
        """
        Crée un modèle Black-Scholes avec validation.
        
        Args:
            volatility: Volatilité
            risk_free_rate: Taux sans risque
            dividend_yield: Taux de dividende
            
        Returns:
            Instance de BlackScholesModel
            
        Raises:
            HTTPException: Si les paramètres sont invalides
        """
        from backend.core.models.black_scholes import BlackScholesModel
        
        validate_required_param(
            volatility,
            "La volatilité",
            "pour le modèle Black-Scholes"
        )
        validate_required_param(
            risk_free_rate,
            "Le taux sans risque",
            "pour le modèle Black-Scholes"
        )
        
        return BlackScholesModel(
            volatility=volatility,
            risk_free_rate=risk_free_rate,
            dividend_yield=dividend_yield or 0.0
        )
    
    @staticmethod
    def create_model(
        model_type: str,
        **params
    ):
        """
        Factory method pour créer n'importe quel modèle.
        
        Args:
            model_type: Type de modèle ("BlackScholes", "Heston", etc.)
            **params: Paramètres du modèle
            
        Returns:
            Instance du modèle
            
        Raises:
            HTTPException: Si le modèle n'est pas supporté
        """
        if model_type == "BlackScholes":
            return ModelFactory.create_black_scholes(
                volatility=params.get('volatility'),
                risk_free_rate=params.get('risk_free_rate'),
                dividend_yield=params.get('dividend_yield')
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Modèle non implémenté: {model_type}"
            )


def create_error_response(
    trade_id: str,
    error_message: str,
    currency: str = "USD"
) -> dict:
    """
    Crée une réponse d'erreur standardisée pour le pricing.
    
    Args:
        trade_id: ID du trade
        error_message: Message d'erreur
        currency: Devise
        
    Returns:
        Dictionnaire de réponse d'erreur
    """
    from datetime import date
    
    return {
        "trade_id": trade_id,
        "price": 0.0,
        "currency": currency,
        "valuation_date": date.today().isoformat(),
        "model_type": "Error",
        "model_parameters": {"error": error_message},
        "pricing_method": "error"
    }
