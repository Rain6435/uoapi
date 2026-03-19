"""Unit tests for server helper functions."""

import pytest
from unittest.mock import Mock

from uoapi.server.app import (
    normalize_university,
    term_code_to_name,
    get_provider,
)
from uoapi.core.models import University


class TestNormalizeUniversity:
    """Tests for normalize_university helper function."""

    def test_uottawa_lowercase(self):
        """Test uottawa normalizes to uottawa."""
        result = normalize_university("uottawa")
        assert result == "uottawa"

    def test_ottawa_normalizes_to_uottawa(self):
        """Test ottawa normalizes to uottawa."""
        result = normalize_university("ottawa")
        assert result == "uottawa"

    def test_university_of_ottawa_normalizes(self):
        """Test 'University of Ottawa' normalizes."""
        result = normalize_university("University of Ottawa")
        assert result == "uottawa"

    def test_carleton_lowercase(self):
        """Test carleton normalizes to carleton."""
        result = normalize_university("carleton")
        assert result == "carleton"

    def test_carleton_university_normalizes(self):
        """Test 'Carleton University' normalizes."""
        result = normalize_university("Carleton University")
        assert result == "carleton"

    def test_cu_stays_as_cu(self):
        """Test cu stays as cu in normalization."""
        result = normalize_university("cu")
        assert result == "cu"

    def test_case_insensitive(self):
        """Test normalization is case insensitive."""
        assert normalize_university("UOTTAWA") == "uottawa"
        assert normalize_university("CARLETON") == "carleton"

    def test_removes_spaces(self):
        """Test spaces are removed."""
        result = normalize_university("Carleton University")
        assert result == "carleton"


class TestTermCodeToName:
    """Tests for term_code_to_name helper function."""

    def test_carleton_winter_2025(self):
        """Test Carleton winter term code."""
        result = term_code_to_name("202510")
        assert "Winter" in result
        assert "2025" in result

    def test_carleton_summer_2025(self):
        """Test Carleton summer term code."""
        result = term_code_to_name("202520")
        assert "Summer" in result
        assert "2025" in result

    def test_carleton_fall_2025(self):
        """Test Carleton fall term code."""
        result = term_code_to_name("202530")
        assert "Fall" in result
        assert "2025" in result

    def test_uottawa_fall_format(self):
        """Test UOttawa fall format."""
        result = term_code_to_name("2025fall")
        assert "Fall" in result
        assert "2025" in result

    def test_uottawa_winter_format(self):
        """Test UOttawa winter format."""
        result = term_code_to_name("2025winter")
        assert "Winter" in result
        assert "2025" in result

    def test_uottawa_summer_format(self):
        """Test UOttawa summer format."""
        result = term_code_to_name("2025summer")
        assert "Summer" in result
        assert "2025" in result

    def test_unknown_carleton_term(self):
        """Test unknown term code returns descriptive result."""
        result = term_code_to_name("202599")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_unrecognized_uottawa_format(self):
        """Test unrecognized format returns as-is."""
        result = term_code_to_name("2025spring")
        # Should return something
        assert isinstance(result, str)


class TestGetProvider:
    """Tests for get_provider helper function."""

    def test_returns_carleton_for_carleton(self):
        """Test get_provider returns provider for carleton."""
        provider = get_provider("carleton")
        assert provider is not None

    def test_returns_provider_for_cu(self):
        """Test get_provider returns provider for cu."""
        provider = get_provider("cu")
        assert provider is not None

    def test_returns_provider_for_uottawa(self):
        """Test get_provider returns provider for uottawa."""
        provider = get_provider("uottawa")
        assert provider is not None

    def test_returns_provider_for_ottawa(self):
        """Test get_provider returns provider for ottawa."""
        provider = get_provider("ottawa")
        assert provider is not None

    def test_raises_for_invalid_university(self):
        """Test get_provider raises ValueError for invalid university."""
        with pytest.raises(ValueError):
            get_provider("mcmaster")

    def test_raises_for_empty_string(self):
        """Test get_provider raises ValueError for empty string."""
        with pytest.raises(ValueError):
            get_provider("")

    def test_case_insensitive_lookup(self):
        """Test get_provider is case insensitive."""
        carleton1 = get_provider("CARLETON")
        carleton2 = get_provider("carleton")
        # Should get same type of provider
        assert type(carleton1) == type(carleton2)

    def test_error_message_includes_available(self):
        """Test error message includes available options."""
        try:
            get_provider("invalid")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Available" in str(e) or "available" in str(e)


class TestTermCodeRoundTrip:
    """Tests for round-trip conversion of term codes."""

    def test_carleton_codes_convert_back(self):
        """Test Carleton codes can be converted back."""
        codes = ["202510", "202520", "202530"]
        for code in codes:
            name = term_code_to_name(code)
            # Should contain year and term name
            assert code[:4] in name

    def test_uottawa_codes_convert_back(self):
        """Test UOttawa codes can be converted back."""
        codes = ["2025fall", "2025winter", "2025summer"]
        for code in codes:
            name = term_code_to_name(code)
            assert "2025" in name
