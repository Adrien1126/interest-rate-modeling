import pytest
from backend.core.products.option import Option
from backend.core.products.base_product import OptionType, ExerciseType, ProductType

# --- FIXTURES ---------------------------------------------------------------

@pytest.fixture
def call_option():
    """Option Call européenne avec paramètres standards."""
    return Option(
        strike=100,
        maturity=1.0,
        option_type=OptionType.CALL,
        exercise_type=ExerciseType.EUROPEAN,
        notional=1.0
    )

@pytest.fixture
def put_option():
    """Option Put européenne avec paramètres standards."""
    return Option(
        strike=100,
        maturity=1.0,
        option_type=OptionType.PUT,
        exercise_type=ExerciseType.EUROPEAN,
        notional=1.0
    )

# --- TESTS DE BASE ----------------------------------------------------------

def test_initialisation_valide(call_option):
    """Vérifie que l'option est correctement initialisée."""
    assert call_option.strike == 100
    assert call_option.maturity == 1.0
    assert call_option.option_type == OptionType.CALL
    assert call_option.exercise_type == ExerciseType.EUROPEAN
    assert call_option.product_type == ProductType.OPTION

def test_initialisation_invalide():
    """Vérifie qu'un strike <= 0 déclenche une erreur."""
    with pytest.raises(ValueError):
        Option(strike=0, maturity=1.0)

# --- PAYOFF -----------------------------------------------------------------

def test_call_payoff(call_option):
    """Payoff d'un call : max(S-K, 0)."""
    assert call_option.payoff(spot_price=120) == 20
    assert call_option.payoff(spot_price=80) == 0

def test_put_payoff(put_option):
    """Payoff d'un put : max(K-S, 0)."""
    assert put_option.payoff(spot_price=80) == 20
    assert put_option.payoff(spot_price=120) == 0

def test_payoff_type_invalide():
    """Erreur si option_type non reconnu."""
    opt = Option(strike=100, maturity=1.0)
    opt.option_type = "INVALID"
    with pytest.raises(ValueError):
        opt.payoff(spot_price=100)

# --- MONEYNESSES & ETAT -----------------------------------------------------

def test_is_in_the_money(call_option, put_option):
    assert call_option.is_in_the_money(120) is True
    assert call_option.is_in_the_money(80) is False
    assert put_option.is_in_the_money(80) is True
    assert put_option.is_in_the_money(120) is False

def test_is_out_of_the_money(call_option):
    assert call_option.is_out_of_the_money(80) is True
    assert call_option.is_out_of_the_money(120) is False

def test_is_at_the_money(call_option):
    assert call_option.is_at_the_money(spot_price=100.5, tolerance=0.01) is True
    assert call_option.is_at_the_money(spot_price=105, tolerance=0.01) is False

def test_moneyness(call_option, put_option):
    assert call_option.moneyness(120) == pytest.approx(1.2)
    assert put_option.moneyness(80) == pytest.approx(1.25)

# --- INFORMATIONS & REPRÉSENTATION -----------------------------------------

def test_get_characteristics(call_option):
    info = call_option.get_characteristics()
    assert info["product_type"] == "option"
    assert info["option_type"] == "call"
    assert info["exercise_type"] == "european"
    assert info["strike"] == 100
    assert info["maturity"] == 1.0

def test_repr_and_str(call_option):
    text = repr(call_option)
    assert "Option(" in text
    assert "type=call" in text
    assert str(call_option).startswith("CALL European")

# --- INTRINSIC VALUE --------------------------------------------------------

def test_intrinsic_value_call(call_option):
    """Vérifie que la valeur intrinsèque = payoff pour un call."""
    assert call_option.intrinsic_value(120) == 20
    assert call_option.intrinsic_value(80) == 0
    assert call_option.intrinsic_value(100) == 0

def test_intrinsic_value_put(put_option):
    """Vérifie que la valeur intrinsèque = payoff pour un put."""
    assert put_option.intrinsic_value(80) == 20
    assert put_option.intrinsic_value(120) == 0
    assert put_option.intrinsic_value(100) == 0

# --- TESTS ADDITIONNELS -----------------------------------------------------

def test_american_option():
    """Test création d'une option américaine."""
    opt = Option(
        strike=100,
        maturity=1.0,
        option_type=OptionType.PUT,
        exercise_type=ExerciseType.AMERICAN,
        notional=100.0
    )
    assert opt.exercise_type == ExerciseType.AMERICAN
    assert opt.notional == 100.0
    assert opt.payoff(90) == 1000.0  # (100-90) * 100

def test_bermudan_option():
    """Test création d'une option bermudienne."""
    opt = Option(
        strike=50,
        maturity=2.0,
        exercise_type=ExerciseType.BERMUDAN
    )
    assert opt.exercise_type == ExerciseType.BERMUDAN
    assert opt.strike == 50
    assert opt.maturity == 2.0

def test_option_with_custom_notional():
    """Test option avec notionnel personnalisé."""
    opt = Option(
        strike=100,
        maturity=1.0,
        option_type=OptionType.CALL,
        notional=1000.0
    )
    assert opt.notional == 1000.0
    # Payoff multiplié par le notionnel
    assert opt.payoff(110) == 10000.0  # (110-100) * 1000

def test_negative_strike_raises_error():
    """Test qu'un strike négatif lève une erreur."""
    with pytest.raises(ValueError, match="strike doit être strictement positif"):
        Option(strike=-100, maturity=1.0)

def test_strike_at_boundary():
    """Test option avec strike très petit mais positif."""
    opt = Option(strike=0.01, maturity=1.0)
    assert opt.strike == 0.01

def test_moneyness_put():
    """Test moneyness spécifique pour un put."""
    opt = Option(
        strike=100,
        maturity=1.0,
        option_type=OptionType.PUT
    )
    # Pour un put: moneyness = K/S
    assert opt.moneyness(50) == pytest.approx(2.0)
    assert opt.moneyness(100) == pytest.approx(1.0)
    assert opt.moneyness(200) == pytest.approx(0.5)

def test_moneyness_call():
    """Test moneyness spécifique pour un call."""
    opt = Option(
        strike=100,
        maturity=1.0,
        option_type=OptionType.CALL
    )
    # Pour un call: moneyness = S/K
    assert opt.moneyness(50) == pytest.approx(0.5)
    assert opt.moneyness(100) == pytest.approx(1.0)
    assert opt.moneyness(200) == pytest.approx(2.0)

def test_is_at_the_money_exact():
    """Test ATM avec prix spot exactement égal au strike."""
    opt = Option(strike=100, maturity=1.0)
    assert opt.is_at_the_money(100.0, tolerance=0.01) is True
    # Avec tolérance 0, même 100.0 exact donne False car 0 < 0 est False
    # C'est le comportement correct de l'opérateur strict <
    assert opt.is_at_the_money(100.0, tolerance=0.0) is False
    # Mais avec une tolérance très petite, ça marche
    assert opt.is_at_the_money(100.0, tolerance=1e-10) is True

def test_is_at_the_money_with_tolerance():
    """Test ATM avec différentes tolérances."""
    opt = Option(strike=100, maturity=1.0)
    # 99.5 est à 0.5% de 100
    assert opt.is_at_the_money(99.5, tolerance=0.01) is True
    assert opt.is_at_the_money(99.5, tolerance=0.001) is False
    # 102 est à 2% de 100
    assert opt.is_at_the_money(102, tolerance=0.025) is True
    assert opt.is_at_the_money(102, tolerance=0.01) is False

def test_is_in_the_money_at_strike():
    """Test qu'au strike, l'option n'est pas ITM."""
    call = Option(strike=100, maturity=1.0, option_type=OptionType.CALL)
    put = Option(strike=100, maturity=1.0, option_type=OptionType.PUT)
    assert call.is_in_the_money(100) is False
    assert put.is_in_the_money(100) is False

def test_is_out_of_the_money_at_strike():
    """Test qu'au strike, l'option est OTM."""
    opt = Option(strike=100, maturity=1.0)
    assert opt.is_out_of_the_money(100) is True

def test_payoff_at_strike():
    """Test que le payoff au strike est 0."""
    call = Option(strike=100, maturity=1.0, option_type=OptionType.CALL)
    put = Option(strike=100, maturity=1.0, option_type=OptionType.PUT)
    assert call.payoff(100) == 0
    assert put.payoff(100) == 0

def test_get_characteristics_put():
    """Test get_characteristics pour un put."""
    opt = Option(
        strike=150,
        maturity=2.5,
        option_type=OptionType.PUT,
        exercise_type=ExerciseType.AMERICAN,
        notional=500.0
    )
    chars = opt.get_characteristics()
    assert chars["product_type"] == "option"
    assert chars["option_type"] == "put"
    assert chars["exercise_type"] == "american"
    assert chars["strike"] == 150
    assert chars["maturity"] == 2.5
    assert chars["notional"] == 500.0

def test_repr_put():
    """Test __repr__ pour un put."""
    opt = Option(
        strike=75,
        maturity=0.5,
        option_type=OptionType.PUT,
        exercise_type=ExerciseType.BERMUDAN
    )
    repr_str = repr(opt)
    assert "Option(" in repr_str
    assert "type=put" in repr_str
    assert "strike=75" in repr_str
    assert "maturity=0.5" in repr_str
    assert "exercise=bermudan" in repr_str

def test_str_put():
    """Test __str__ pour un put."""
    opt = Option(
        strike=120,
        maturity=3.0,
        option_type=OptionType.PUT,
        exercise_type=ExerciseType.AMERICAN
    )
    str_repr = str(opt)
    assert "PUT" in str_repr
    assert "American" in str_repr
    assert "120" in str_repr
    assert "3.0" in str_repr

def test_str_bermudan():
    """Test __str__ pour une option bermudienne."""
    opt = Option(
        strike=90,
        maturity=1.5,
        exercise_type=ExerciseType.BERMUDAN
    )
    str_repr = str(opt)
    assert "Bermudan" in str_repr
