"""
Convertisseurs entre les schémas JSON/Pydantic et les objets core du backend.

Ce module permet de:
- Convertir un JSON de trade → objet Option/Swap/etc.
- Convertir un objet Option → JSON de trade
- Gérer la conversion des dates, enums, etc.
"""

from datetime import date, datetime
from typing import Dict, Any, Optional

from backend.core.products.option import Option
from backend.core.products.base_product import OptionType, ExerciseType
from backend.schemas.trade_schemas import (
    TradeContractSchema,
    TradeSchema,
    OptionSchema,
    PricingRequestSchema,
    PricingResponseSchema,
    GreeksSchema
)


class TradeConverter:
    """Convertisseur entre JSON et objets Python."""
    
    @staticmethod
    def calculate_maturity_years(
        expiration_date: date,
        valuation_date: Optional[date] = None
    ) -> float:
        """
        Calcule la maturité en années entre deux dates.
        
        Args:
            expiration_date: Date d'expiration
            valuation_date: Date de valorisation (par défaut aujourd'hui)
            
        Returns:
            Maturité en années (fraction)
        """
        if valuation_date is None:
            valuation_date = date.today()
        
        days = (expiration_date - valuation_date).days
        return days / 365.25  # Années calendaires
    
    @staticmethod
    def json_to_option(
        option_json: OptionSchema,
        valuation_date: Optional[date] = None
    ) -> Option:
        """
        Convertit un schéma JSON d'option en objet Option.
        
        Args:
            option_json: Schéma Pydantic de l'option
            valuation_date: Date de valorisation pour calculer la maturité
            
        Returns:
            Instance d'Option
        """
        # Calcul de la maturité
        maturity = TradeConverter.calculate_maturity_years(
            option_json.expiration_date,
            valuation_date
        )
        
        # Conversion du type d'option
        option_type = OptionType.CALL if option_json.option_type == "Call" else OptionType.PUT
        
        # Conversion du type d'exercice
        exercise_type_map = {
            "European": ExerciseType.EUROPEAN,
            "American": ExerciseType.AMERICAN,
            "Bermudan": ExerciseType.BERMUDAN
        }
        exercise_type = exercise_type_map[option_json.exercise_type]
        
        # Création de l'option
        return Option(
            strike=option_json.strike,
            maturity=maturity,
            option_type=option_type,
            exercise_type=exercise_type,
            notional=option_json.notional.amount
        )
    
    @staticmethod
    def option_to_json(
        option: Option,
        trade_id: str,
        underlying_description: str = "Underlying Asset",
        underlying_isin: Optional[str] = None,
        expiration_date: Optional[date] = None,
        premium_amount: Optional[float] = None,
        buyer_id: str = "buyer",
        seller_id: str = "seller",
        currency: str = "USD"
    ) -> TradeContractSchema:
        """
        Convertit un objet Option en schéma JSON de trade.
        
        Args:
            option: Instance d'Option
            trade_id: Identifiant du trade
            underlying_description: Description du sous-jacent
            underlying_isin: Code ISIN du sous-jacent
            expiration_date: Date d'expiration (calculée si None)
            premium_amount: Montant de la prime (optionnel)
            buyer_id: ID de l'acheteur
            seller_id: ID du vendeur
            currency: Devise
            
        Returns:
            Schéma TradeContractSchema
        """
        # Calcul de la date d'expiration si non fournie
        if expiration_date is None:
            today = date.today()
            days_to_expiry = int(option.maturity * 365.25)
            expiration_date = today.replace(year=today.year + int(option.maturity))
        
        # Construction du schéma
        option_type_str = "Call" if option.option_type == OptionType.CALL else "Put"
        exercise_type_str = option.exercise_type.value.capitalize()
        
        trade_dict = {
            "trade": {
                "trade_id": trade_id,
                "trade_date": date.today(),
                "product_type": "Option",
                "option": {
                    "option_type": option_type_str,
                    "exercise_type": exercise_type_str,
                    "underlying": {
                        "asset_type": "Equity",
                        "isin": underlying_isin,
                        "description": underlying_description
                    },
                    "strike": option.strike,
                    "expiration_date": expiration_date,
                    "notional": {
                        "amount": option.notional,
                        "currency": currency
                    },
                    "settlement": {
                        "settlement_type": "Cash"
                    }
                },
                "parties": {
                    "buyer": {
                        "id": buyer_id,
                        "name": buyer_id
                    },
                    "seller": {
                        "id": seller_id,
                        "name": seller_id
                    }
                }
            }
        }
        
        # Ajout de la prime si fournie
        if premium_amount is not None:
            trade_dict["trade"]["option"]["premium"] = {
                "amount": premium_amount,
                "currency": currency,
                "payment_date": date.today()
            }
        
        return TradeContractSchema(**trade_dict)
    
    @staticmethod
    def trade_to_option(
        trade_contract: TradeContractSchema,
        valuation_date: Optional[date] = None
    ) -> Option:
        """
        Extrait l'objet Option d'un trade contract.
        
        Args:
            trade_contract: Contrat de trade complet
            valuation_date: Date de valorisation
            
        Returns:
            Instance d'Option
            
        Raises:
            ValueError: Si le trade n'est pas une option
        """
        if trade_contract.trade.product_type != "Option":
            raise ValueError(
                f"Le trade n'est pas une option: {trade_contract.trade.product_type}"
            )
        
        if trade_contract.trade.option is None:
            raise ValueError("L'option est manquante dans le trade")
        
        return TradeConverter.json_to_option(
            trade_contract.trade.option,
            valuation_date
        )
    
    @staticmethod
    def extract_metadata(trade_contract: TradeContractSchema) -> Dict[str, Any]:
        """
        Extrait les métadonnées d'un trade contract.
        
        Args:
            trade_contract: Contrat de trade complet
            
        Returns:
            Dictionnaire des métadonnées
        """
        trade = trade_contract.trade
        option = trade.option
        
        metadata = {
            'trade_id': trade.trade_id,
            'trade_date': trade.trade_date,
            'product_type': trade.product_type,
            'buyer': trade.parties.buyer.model_dump(),
            'seller': trade.parties.seller.model_dump(),
        }
        
        if option:
            metadata.update({
                'underlying': option.underlying.model_dump(),
                'expiration_date': option.expiration_date,
                'currency': option.notional.currency,
                'settlement_type': option.settlement.settlement_type.value
            })
            
            if option.premium:
                metadata['premium'] = option.premium.model_dump()
        
        return metadata


class PricingConverter:
    """Convertisseur pour les requêtes et réponses de pricing."""
    
    @staticmethod
    def create_pricing_response(
        trade_id: str,
        price: float,
        currency: str,
        valuation_date: date,
        model_type: str,
        model_parameters: Dict[str, Any],
        pricing_method: str,
        greeks: Optional[Dict[str, float]] = None,
        implied_volatility: Optional[float] = None,
        confidence_interval: Optional[Dict[str, float]] = None,
        computation_time_ms: Optional[float] = None
    ) -> PricingResponseSchema:
        """
        Crée une réponse de pricing formatée.
        
        Args:
            trade_id: ID du trade
            price: Prix calculé
            currency: Devise
            valuation_date: Date de valorisation
            model_type: Type de modèle utilisé
            model_parameters: Paramètres du modèle
            pricing_method: Méthode de pricing
            greeks: Greeks (optionnel)
            implied_volatility: Volatilité implicite (optionnel)
            confidence_interval: Intervalle de confiance (optionnel)
            computation_time_ms: Temps de calcul (optionnel)
            
        Returns:
            PricingResponseSchema
        """
        response_dict = {
            'trade_id': trade_id,
            'price': price,
            'currency': currency,
            'valuation_date': valuation_date,
            'model_type': model_type,
            'model_parameters': model_parameters,
            'pricing_method': pricing_method
        }
        
        if greeks is not None:
            response_dict['greeks'] = GreeksSchema(**greeks)
        
        if implied_volatility is not None:
            response_dict['implied_volatility'] = implied_volatility
        
        if confidence_interval is not None:
            response_dict['confidence_interval'] = confidence_interval
        
        if computation_time_ms is not None:
            response_dict['computation_time_ms'] = computation_time_ms
        
        return PricingResponseSchema(**response_dict)


def example_usage():
    """Exemple d'utilisation des convertisseurs."""
    import json
    
    # JSON d'exemple
    json_str = '''
    {
      "trade": {
        "trade_id": "OPT-001",
        "trade_date": "2025-10-29",
        "product_type": "Option",
        "option": {
          "option_type": "Call",
          "exercise_type": "European",
          "underlying": {
            "asset_type": "Equity",
            "isin": "US0378331005",
            "description": "Apple Inc."
          },
          "strike": 150.0,
          "expiration_date": "2026-10-29",
          "notional": {
            "amount": 100.0,
            "currency": "USD"
          },
          "settlement": {
            "settlement_type": "Cash"
          }
        },
        "parties": {
          "buyer": {
            "id": "Bank_A",
            "name": "Bank A"
          },
          "seller": {
            "id": "Client_B",
            "name": "Client B"
          }
        }
      }
    }
    '''
    
    # Parsing JSON → Pydantic (Pydantic V2)
    trade_contract = TradeContractSchema.model_validate_json(json_str)
    print("✅ JSON parsé avec succès")
    print(f"Trade ID: {trade_contract.trade.trade_id}")
    
    # Pydantic → Objet Option
    option = TradeConverter.trade_to_option(trade_contract)
    print(f"\n✅ Option créée: {option}")
    print(f"Strike: {option.strike}, Maturité: {option.maturity:.4f} ans")
    
    # Objet Option → JSON
    new_trade = TradeConverter.option_to_json(
        option=option,
        trade_id="OPT-002",
        underlying_description="Apple Inc.",
        underlying_isin="US0378331005"
    )
    print(f"\n✅ Trade contract créé: {new_trade.trade.trade_id}")
    
    # Sérialisation JSON (Pydantic V2)
    json_output = new_trade.model_dump_json(indent=2)
    print(f"\n✅ JSON exporté:\n{json_output}")


if __name__ == "__main__":
    example_usage()
