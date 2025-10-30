"""
Configuration pytest pour tous les tests.

Ce fichier configure pytest pour permettre l'import des modules
depuis le répertoire racine du projet et définit des fixtures globales.
"""

import sys
from pathlib import Path
import pytest

# Ajouter le répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))


# ========== Fixtures globales pour les modèles ==========

@pytest.fixture
def bs_model_standard():
    """Modèle Black-Scholes standard (vol=0.2, r=0.05)."""
    from backend.core.models.black_scholes import BlackScholesModel
    return BlackScholesModel(volatility=0.2, risk_free_rate=0.05)


@pytest.fixture
def bs_model_with_dividend():
    """Modèle Black-Scholes avec dividende (vol=0.25, r=0.05, q=0.02)."""
    from backend.core.models.black_scholes import BlackScholesModel
    return BlackScholesModel(volatility=0.25, risk_free_rate=0.05, dividend_yield=0.02)


# ========== Fixtures globales pour les options ==========

@pytest.fixture
def option_call_atm():
    """Option call ATM standard (K=100, T=1)."""
    from backend.core.products.option import Option
    from backend.core.products.base_product import OptionType
    return Option(strike=100.0, maturity=1.0, option_type=OptionType.CALL)


@pytest.fixture
def option_put_atm():
    """Option put ATM standard (K=100, T=1)."""
    from backend.core.products.option import Option
    from backend.core.products.base_product import OptionType
    return Option(strike=100.0, maturity=1.0, option_type=OptionType.PUT)
