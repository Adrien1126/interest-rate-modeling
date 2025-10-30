"""
Routes FastAPI pour le pricing de produits dérivés.

Ce module expose les endpoints API pour:
- Pricer des trades à partir de JSON
- Calculer les Greeks
- Calculer la volatilité implicite
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional
import time
from datetime import date

from backend.schemas.trade_schemas import (
    PricingRequestSchema,
    PricingResponseSchema,
    TradeContractSchema
)
from backend.core.utils.trade_converter import TradeConverter, PricingConverter
from backend.core.utils.pricing_converter import PricingRequestConverter
from backend.core.models.black_scholes import BlackScholesModel
from backend.core.pricing.analytic_pricer import AnalyticOptionPricer
from backend.core.pricing.montecarlo_pricer import MonteCarloOptionPricer
from backend.core.utils.api_utils import (
    validate_required_param,
    validate_product_type,
    handle_api_error,
    create_error_response
)


router = APIRouter(
    prefix="/api/pricing",
    tags=["pricing"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/option",
    response_model=PricingResponseSchema,
    summary="Price une option",
    description="Calcule le prix et les Greeks d'une option à partir d'un trade JSON"
)
async def price_option(request: PricingRequestSchema) -> PricingResponseSchema:
    """
    Price une option en utilisant le modèle spécifié.
    
    Args:
        request: Requête de pricing avec le trade et les paramètres de marché
        
    Returns:
        Réponse avec le prix et les Greeks
        
    Raises:
        HTTPException: Si le trade n'est pas une option ou si les paramètres sont invalides
    """
    start_time = time.time()
    
    try:
        # Validation du type de produit
        validate_product_type(
            request.trade.product_type,
            "Option",
            "Le produit doit être une option"
        )
        
        # Validation des données option
        validate_required_param(
            request.trade.option,
            "Les données de l'option"
        )
        
        # NOUVEAU: Conversion avec conventions de marché
        converter = PricingRequestConverter()
        option, model, time_to_maturity = converter.convert(request)
        
        # Extract dates for response
        valuation_date, expiration_date = converter.extract_dates(request)
        
        # Création du pricer selon la méthode
        if request.pricing_method == "analytic":
            pricer = AnalyticOptionPricer(model)
            pricing_method_name = "analytic"
        else:  # monte_carlo
            pricer = MonteCarloOptionPricer(
                model=model,
                n_simulations=10000,
                n_steps=100,
                use_antithetic=True
            )
            pricing_method_name = "monte_carlo"
        
        # Calcul du prix
        price = pricer.price(option, spot=request.spot_price)
        
        # Calcul des Greeks si demandé
        greeks_dict = None
        if request.compute_greeks:
            greeks_dict = pricer.greeks(option, spot=request.spot_price)
        
        # Pas d'intervalle de confiance pour le pricing analytique
        confidence_interval = None
        
        # Calcul de la volatilité implicite si demandé (analytique uniquement)
        impl_vol = None
        if (request.compute_implied_vol and 
            request.pricing_method == "analytic" and 
            isinstance(pricer, AnalyticOptionPricer) and
            request.trade.option and 
            request.trade.option.premium):
            market_price = request.trade.option.premium.amount
            impl_vol = pricer.implied_volatility(
                option,
                spot=request.spot_price,
                market_price=market_price
            )
        
        # Temps de calcul
        computation_time = (time.time() - start_time) * 1000  # en ms
        
        # Récupérer la devise depuis l'option
        currency = "USD"  # Valeur par défaut
        if request.trade.option and request.trade.option.notional:
            currency = request.trade.option.notional.currency
        
        # Construction de la réponse
        response = PricingConverter.create_pricing_response(
            trade_id=request.trade.trade_id,
            price=price,
            currency=currency,
            valuation_date=valuation_date,
            model_type=request.model_type,
            model_parameters=model.get_parameters(),
            pricing_method=pricing_method_name,
            greeks=greeks_dict,
            implied_volatility=impl_vol,
            confidence_interval=confidence_interval,
            computation_time_ms=round(computation_time, 2)
        )
        
        return response
        
    except HTTPException:
        raise
    except ValueError as e:
        raise handle_api_error(e, "pricing (validation)")
    except Exception as e:
        raise handle_api_error(e, "pricing")


@router.post(
    "/validate-trade",
    response_model=dict,
    summary="Valide un trade",
    description="Vérifie qu'un trade JSON est valide"
)
async def validate_trade(trade: TradeContractSchema) -> dict:
    """
    Valide un trade sans le pricer.
    
    Args:
        trade: Trade à valider
        
    Returns:
        Dictionnaire avec le statut de validation
    """
    try:
        # Extraction des métadonnées
        metadata = TradeConverter.extract_metadata(trade)
        
        # Conversion en objet (teste la validité)
        if trade.trade.product_type == "Option":
            option = TradeConverter.trade_to_option(trade)
            
            return {
                "status": "valid",
                "message": "Trade valide",
                "metadata": metadata,
                "product_info": {
                    "strike": option.strike,
                    "maturity_years": round(option.maturity, 4),
                    "option_type": option.option_type.value,
                    "exercise_type": option.exercise_type.value
                }
            }
        else:
            return {
                "status": "valid",
                "message": "Trade valide (produit non implémenté pour validation complète)",
                "metadata": metadata
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trade invalide: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health check",
    description="Vérifie que le service de pricing est disponible"
)
async def health_check() -> dict:
    """Health check du service de pricing."""
    return {
        "status": "healthy",
        "service": "pricing",
        "supported_models": ["BlackScholes"],
        "supported_products": ["Option"],
        "supported_methods": ["analytic", "monte_carlo"]
    }


@router.post(
    "/batch",
    response_model=list[PricingResponseSchema],
    summary="Price plusieurs options",
    description="Calcule le prix de plusieurs options en batch"
)
async def price_batch(requests: list[PricingRequestSchema]) -> list[PricingResponseSchema]:
    """
    Price plusieurs options en une seule requête.
    
    Args:
        requests: Liste de requêtes de pricing
        
    Returns:
        Liste de réponses de pricing
    """
    responses = []
    
    for request in requests:
        try:
            response = await price_option(request)
            responses.append(response)
        except HTTPException as e:
            # En cas d'erreur, utiliser la factory de réponse d'erreur
            error_resp = create_error_response(
                trade_id=request.trade.trade_id,
                error_message=str(e.detail)
            )
            responses.append(
                PricingResponseSchema(
                    **error_resp,
                    computation_time_ms=0.0
                )
            )
    
    return responses


@router.post(
    "/price",
    summary="Price un produit générique",
    description="Endpoint unifié pour pricer différents types de produits"
)
async def price_generic(request: dict):
    """
    Endpoint générique pour le pricing.
    
    Format attendu:
    {
        "product_type": "option",
        "product_params": {
            "option_type": "call" | "put",
            "strike": float,
            "trade_date": "YYYY-MM-DD",
            "expiration_date": "YYYY-MM-DD",
            "day_count_convention": "ACT/365" | ...,
            "business_day_convention": "ModifiedFollowing" | ...,
            "calendar": "TARGET" | ...
        },
        "pricing_method": "analytic" | "montecarlo",
        "pricing_params": {
            "n_simulations": int,
            "n_steps": int,
            "use_antithetic": bool,
            "random_seed": int,
            "compute_confidence_interval": bool,
            "confidence_level": float
        },
        "market_data": {
            "spot": float,
            "rate": float,
            "dividend_yield": float,
            "volatility": float
        },
        "model": "black-scholes"
    }
    """
    start_time = time.time()
    
    try:
        from backend.core.products.option import Option
        from backend.core.products.base_product import OptionType
        from backend.core.utils.date_utils import DateUtils
        
        # Extraction des paramètres
        product_type = request.get("product_type", "option")
        product_params = request.get("product_params", {})
        pricing_method = request.get("pricing_method", "analytic")
        pricing_params = request.get("pricing_params", {})
        market_data = request.get("market_data", {})
        model_type = request.get("model", "black-scholes")
        
        # Validation
        if product_type != "option":
            raise HTTPException(
                status_code=400,
                detail=f"Type de produit non supporté: {product_type}"
            )
        
        # Création de l'option
        option_type_str = product_params.get("option_type", "call").upper()
        option_type = OptionType.CALL if option_type_str == "CALL" else OptionType.PUT
        strike = float(product_params.get("strike", 100))
        trade_date_str = product_params.get("trade_date")
        expiration_date_str = product_params.get("expiration_date")
        
        # Calcul du temps jusqu'à maturité avec conventions de marché
        day_count = product_params.get("day_count_convention", "ACT/365")
        business_day = product_params.get("business_day_convention", "ModifiedFollowing")
        calendar_name = product_params.get("calendar", "TARGET")
        
        # Convertir les dates string en objets date
        from datetime import datetime
        trade_date = datetime.strptime(trade_date_str, "%Y-%m-%d").date()
        expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d").date()
        
        time_to_maturity = DateUtils.year_fraction(
            trade_date,
            expiration_date,
            day_count=day_count
        )
        
        # Création du produit
        option = Option(
            option_type=option_type,
            strike=strike,
            maturity=time_to_maturity
        )
        
        # Extraction des données de marché
        spot = float(market_data.get("spot", 100))
        volatility = float(market_data.get("volatility", 0.2))
        risk_free_rate = float(market_data.get("rate", 0.05))
        dividend_yield = float(market_data.get("dividend_yield", 0.0))
        
        # Création du modèle
        model = BlackScholesModel(
            volatility=volatility,
            risk_free_rate=risk_free_rate,
            dividend_yield=dividend_yield
        )
        
        # Création du pricer
        if pricing_method == "analytic":
            pricer = AnalyticOptionPricer(model)
            pricing_method_name = "analytic"
            confidence_interval = None
        else:  # montecarlo
            n_simulations = int(pricing_params.get("n_simulations", 10000))
            n_steps = int(pricing_params.get("n_steps", 100))
            use_antithetic = pricing_params.get("use_antithetic", True)
            random_seed = pricing_params.get("random_seed", None)
            
            pricer = MonteCarloOptionPricer(
                model=model,
                n_simulations=n_simulations,
                n_steps=n_steps,
                use_antithetic=use_antithetic,
                random_seed=random_seed if random_seed else None
            )
            pricing_method_name = "monte_carlo"
            
            # Calcul de l'intervalle de confiance si demandé
            if pricing_params.get("compute_confidence_interval", True):
                confidence_level = float(pricing_params.get("confidence_level", 0.95))
                confidence_interval = pricer.confidence_interval(
                    option,
                    spot=spot,
                    confidence_level=confidence_level
                )
            else:
                confidence_interval = None
        
        # Calcul du prix
        price = pricer.price(option, spot=spot)
        
        # Calcul des Greeks
        greeks_dict = pricer.greeks(option, spot=spot)
        
        # Temps de calcul
        computation_time = (time.time() - start_time) * 1000  # en ms
        
        # Construction de la réponse
        response = {
            "price": float(price),
            "greeks": {
                "delta": float(greeks_dict.get("delta", 0)),
                "gamma": float(greeks_dict.get("gamma", 0)),
                "vega": float(greeks_dict.get("vega", 0)),
                "theta": float(greeks_dict.get("theta", 0)),
                "rho": float(greeks_dict.get("rho", 0))
            },
            "model_type": model_type,
            "pricing_method": pricing_method_name,
            "computation_time_ms": round(computation_time, 2),
            "market_data": market_data,
            "product_params": product_params
        }
        
        # Ajouter l'intervalle de confiance si disponible
        if confidence_interval:
            response["confidence_interval"] = {
                "price": float(confidence_interval.get("price", price)),
                "lower_bound": float(confidence_interval.get("lower_bound", 0)),
                "upper_bound": float(confidence_interval.get("upper_bound", 0)),
                "std_error": float(confidence_interval.get("std_error", 0)),
                "confidence_level": float(confidence_interval.get("confidence_level", 0.95))
            }
        
        return response
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erreur de validation: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du pricing: {str(e)}"
        )
