"""
Tests pour le module date_utils avec QuantLib.

Ces tests vérifient:
- Les conversions de dates Python ↔ QuantLib
- Le calcul de fractions d'année avec différentes conventions
- L'ajustement de dates avec conventions de jours ouvrés
- Les calculs de jours ouvrés
- Le calcul de time to maturity avec toutes les conventions
"""

import pytest
from datetime import date
from backend.core.utils.date_utils import (
    DateUtils,
    calculate_time_to_maturity
)


class TestDateConversion:
    """Tests pour les conversions de dates."""
    
    def test_to_ql_date(self):
        """Test conversion Python date → QuantLib Date."""
        py_date = date(2025, 10, 30)
        ql_date = DateUtils.to_ql_date(py_date)
        
        # Vérifier que c'est bien la même date
        assert ql_date.dayOfMonth() == 30
        assert ql_date.month() == 10
        assert ql_date.year() == 2025
    
    def test_from_ql_date(self):
        """Test conversion QuantLib Date → Python date."""
        py_date = date(2025, 10, 30)
        ql_date = DateUtils.to_ql_date(py_date)
        converted_back = DateUtils.from_ql_date(ql_date)
        
        assert converted_back == py_date
    
    def test_round_trip_conversion(self):
        """Test conversion aller-retour."""
        original = date(2024, 1, 15)
        ql_date = DateUtils.to_ql_date(original)
        converted = DateUtils.from_ql_date(ql_date)
        
        assert converted == original


class TestYearFraction:
    """Tests pour le calcul de fractions d'année."""
    
    def test_year_fraction_act_365(self):
        """Test ACT/365 convention."""
        start = date(2025, 1, 1)
        end = date(2026, 1, 1)
        
        fraction = DateUtils.year_fraction(start, end, "ACT/365")
        
        # 365 jours / 365 = 1.0
        assert abs(fraction - 1.0) < 0.01
    
    def test_year_fraction_act_360(self):
        """Test ACT/360 convention."""
        start = date(2025, 1, 1)
        end = date(2025, 7, 1)  # ~181 jours
        
        fraction = DateUtils.year_fraction(start, end, "ACT/360")
        
        # Doit être > 0.5 (181/360 ≈ 0.5028)
        assert fraction > 0.5
        assert fraction < 0.51
    
    def test_year_fraction_30_360(self):
        """Test 30/360 convention."""
        start = date(2025, 1, 1)
        end = date(2025, 7, 1)
        
        fraction = DateUtils.year_fraction(start, end, "30/360")
        
        # 6 mois = 180 jours / 360 = 0.5
        assert abs(fraction - 0.5) < 0.01
    
    def test_year_fraction_act_act(self):
        """Test ACT/ACT convention."""
        start = date(2024, 1, 1)  # Année bissextile
        end = date(2025, 1, 1)
        
        fraction = DateUtils.year_fraction(start, end, "ACT/ACT")
        
        # 366 jours dans une année bissextile
        assert abs(fraction - 1.0) < 0.01
    
    def test_year_fraction_same_dates(self):
        """Test avec dates identiques."""
        start = date(2025, 1, 1)
        
        fraction = DateUtils.year_fraction(start, start, "ACT/365")
        
        assert fraction == 0.0


class TestBusinessDayAdjustment:
    """Tests pour l'ajustement de jours ouvrés."""
    
    def test_adjust_date_following(self):
        """Test Following convention."""
        # Samedi 1er novembre 2025
        saturday = date(2025, 11, 1)
        
        adjusted = DateUtils.adjust_date(saturday, "TARGET", "Following")
        
        # Doit être déplacé au lundi suivant
        assert adjusted.weekday() == 0  # Lundi
        assert adjusted > saturday
    
    def test_adjust_date_preceding(self):
        """Test Preceding convention."""
        # Samedi 1er novembre 2025
        saturday = date(2025, 11, 1)
        
        adjusted = DateUtils.adjust_date(saturday, "TARGET", "Preceding")
        
        # Doit être déplacé au vendredi précédent
        assert adjusted.weekday() == 4  # Vendredi
        assert adjusted < saturday
    
    def test_adjust_date_unadjusted(self):
        """Test Unadjusted convention."""
        # Samedi 1er novembre 2025
        saturday = date(2025, 11, 1)
        
        adjusted = DateUtils.adjust_date(saturday, "TARGET", "Unadjusted")
        
        # Ne doit pas changer
        assert adjusted == saturday
    
    def test_adjust_business_day_unchanged(self):
        """Test qu'un jour ouvré n'est pas modifié."""
        # Lundi 3 novembre 2025
        monday = date(2025, 11, 3)
        
        adjusted = DateUtils.adjust_date(monday, "TARGET", "Following")
        
        # Ne doit pas changer
        assert adjusted == monday


class TestBusinessDayCalculations:
    """Tests pour les calculs de jours ouvrés."""
    
    def test_is_business_day_weekday(self):
        """Test qu'un jour de semaine est un jour ouvré."""
        # Lundi 3 novembre 2025
        monday = date(2025, 11, 3)
        
        is_business = DateUtils.is_business_day(monday, "TARGET")
        
        assert is_business is True
    
    def test_is_business_day_weekend(self):
        """Test qu'un weekend n'est pas un jour ouvré."""
        # Samedi 1er novembre 2025
        saturday = date(2025, 11, 1)
        
        is_business = DateUtils.is_business_day(saturday, "TARGET")
        
        assert is_business is False
    
    def test_add_business_days(self):
        """Test ajout de jours ouvrés."""
        # Vendredi 31 octobre 2025
        friday = date(2025, 10, 31)
        
        # Ajouter 1 jour ouvré doit donner lundi
        next_day = DateUtils.add_business_days(friday, 1, "TARGET")
        
        assert next_day.weekday() == 0  # Lundi
        assert next_day == date(2025, 11, 3)
    
    def test_business_days_between(self):
        """Test calcul de jours ouvrés entre deux dates."""
        # Vendredi 31 octobre au lundi 3 novembre
        friday = date(2025, 10, 31)
        monday = date(2025, 11, 3)
        
        days = DateUtils.business_days_between(friday, monday, "TARGET")
        
        # Vendredi → Lundi = 1 jour ouvré (pas de comptage du premier jour)
        assert days == 1


class TestCalculateTimeToMaturity:
    """Tests pour la fonction principale calculate_time_to_maturity."""
    
    def test_calculate_maturity_one_year_act_365(self):
        """Test calcul d'1 an avec ACT/365."""
        start = date(2025, 10, 30)
        end = date(2026, 10, 30)
        
        maturity = calculate_time_to_maturity(
            trade_date=start,
            maturity_date=end,
            day_count="ACT/365",
            business_day_convention="Unadjusted",
            calendar="NullCalendar"
        )
        
        # Environ 1 an
        assert abs(maturity - 1.0) < 0.01
    
    def test_calculate_maturity_six_months_30_360(self):
        """Test calcul de 6 mois avec 30/360."""
        start = date(2025, 1, 1)
        end = date(2025, 7, 1)
        
        maturity = calculate_time_to_maturity(
            trade_date=start,
            maturity_date=end,
            day_count="30/360",
            business_day_convention="Unadjusted",
            calendar="NullCalendar"
        )
        
        # 6 mois = 0.5 an avec 30/360
        assert abs(maturity - 0.5) < 0.01
    
    def test_calculate_maturity_with_adjustment(self):
        """Test calcul avec ajustement de jours ouvrés."""
        # Expiration un samedi
        start = date(2025, 10, 30)
        end = date(2025, 11, 1)  # Samedi
        
        maturity = calculate_time_to_maturity(
            trade_date=start,
            maturity_date=end,
            day_count="ACT/365",
            business_day_convention="Following",
            calendar="TARGET"
        )
        
        # L'expiration devrait être ajustée au lundi suivant
        # Donc la maturité devrait être légèrement plus longue
        maturity_unadjusted = calculate_time_to_maturity(
            trade_date=start,
            maturity_date=end,
            day_count="ACT/365",
            business_day_convention="Unadjusted",
            calendar="NullCalendar"
        )
        
        assert maturity > maturity_unadjusted
    
    def test_calculate_maturity_different_conventions(self):
        """Test que différentes conventions donnent des résultats différents."""
        start = date(2025, 1, 1)
        end = date(2025, 7, 1)
        
        maturity_365 = calculate_time_to_maturity(
            trade_date=start,
            maturity_date=end,
            day_count="ACT/365",
            business_day_convention="Unadjusted",
            calendar="NullCalendar"
        )
        
        maturity_360 = calculate_time_to_maturity(
            trade_date=start,
            maturity_date=end,
            day_count="ACT/360",
            business_day_convention="Unadjusted",
            calendar="NullCalendar"
        )
        
        # ACT/360 devrait donner un résultat légèrement plus grand
        assert maturity_360 > maturity_365


class TestEdgeCases:
    """Tests pour les cas limites."""
    
    def test_leap_year_act_act(self):
        """Test année bissextile avec ACT/ACT."""
        start = date(2024, 2, 28)
        end = date(2024, 3, 1)  # 2024 est bissextile
        
        fraction = DateUtils.year_fraction(start, end, "ACT/ACT")
        
        # 2 jours dans une année de 366 jours
        expected = 2 / 366
        assert abs(fraction - expected) < 0.001
    
    def test_different_calendars(self):
        """Test que différents calendriers donnent des résultats différents."""
        # Date qui pourrait être un jour férié aux US mais pas au UK
        some_date = date(2025, 7, 4)  # Independence Day US
        
        is_business_us = DateUtils.is_business_day(some_date, "UnitedStates")
        is_business_uk = DateUtils.is_business_day(some_date, "UnitedKingdom")
        
        # Le 4 juillet devrait être férié aux US
        assert is_business_us is False
        # Mais pas au UK (c'est un vendredi normal)
        assert is_business_uk is True
    
    def test_null_calendar_no_holidays(self):
        """Test que NullCalendar n'a pas de jours fériés."""
        # Un dimanche
        sunday = date(2025, 11, 2)
        
        is_business = DateUtils.is_business_day(sunday, "NullCalendar")
        
        # NullCalendar considère tous les jours (même les weekends) comme ouvrés
        assert is_business is True
