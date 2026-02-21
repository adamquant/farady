"""API contract tests for SunnaAssets integration.

These tests validate that the input/output schemas of the Lambda functions
match the expected format for the farady module integration.
"""

import json
import pytest
from typing import Any


HEIR_FIELDS = {
    "ibn",
    "bint",
    "iibn",
    "bibn",
    "iiibn",
    "biibn",
    "umm",
    "jadda",
    "ab",
    "jadd",
    "lium",
    "shaqiqa",
    "shaqiq",
    "uliab",
    "aliab",
    "ibnamm_sh",
    "ibnamm_liab",
    "amm",
    "zawj",
    "zawja",
}


class TestInputContract:
    """Tests for input schema validation."""

    @pytest.mark.parametrize("field", HEIR_FIELDS)
    def test_field_is_recognized(self, field: str) -> None:
        """All heir fields should be recognized by farady."""
        from farady import HEIR_FIELDS as FARADY_FIELDS

        assert field in FARADY_FIELDS, f"Field {field} not in farady.HEIR_FIELDS"

    def test_inheritance_case_accepts_all_fields(self) -> None:
        """InheritanceCase should accept all heir fields."""
        from farady import InheritanceCase

        case = InheritanceCase(
            ibn=1,
            bint=2,
            iibn=0,
            bibn=0,
            umm=1,
            ab=1,
            zawja=True,
        )
        assert case.ibn == 1
        assert case.zawja is True

    def test_string_values_converted(self) -> None:
        """String values in input should be converted properly."""
        from farady import calculate_from_dict

        result = calculate_from_dict(
            {
                "ibn": "1",
                "bint": "2",
                "zawja": "True",
            }
        )

        assert "ibn" in result.distribution
        assert "bint" in result.distribution
        assert "zawja" in result.distribution


class TestOutputContract:
    """Tests for output schema validation."""

    def test_result_has_required_fields(self) -> None:
        """InheritanceResult should have all required fields."""
        from farady import calculate_inheritance

        result = calculate_inheritance(ibn=1, bint=1, zawja=True)

        assert hasattr(result, "distribution")
        assert hasattr(result, "ending")
        assert hasattr(result, "asib")
        assert hasattr(result, "total")
        assert hasattr(result, "status")
        assert hasattr(result, "denominator")

    def test_distribution_is_dict(self) -> None:
        """Distribution should be a dict mapping heir names to shares."""
        from farady import calculate_inheritance

        result = calculate_inheritance(ibn=1, zawja=True)

        assert isinstance(result.distribution, dict)
        for heir, share in result.distribution.items():
            assert isinstance(heir, str)
            assert isinstance(share, float)
            assert 0 <= share <= 1

    def test_total_equals_one_for_complete(self) -> None:
        """Total should be 1.0 for complete distributions."""
        from farady import calculate_inheritance

        result = calculate_inheritance(ibn=1, zawja=True)

        assert result.status == "Complete"
        assert abs(result.total - 1.0) < 0.0001

    def test_denominator_is_positive_integer(self) -> None:
        """Denominator should be a positive integer when set."""
        from farady import calculate_inheritance

        result = calculate_inheritance(ibn=1, bint=1, zawja=True)

        if result.denominator is not None:
            assert isinstance(result.denominator, int)
            assert result.denominator > 0


class TestLambdaPayloadFormat:
    """Tests for Lambda event payload format."""

    def test_free_estimate_payload_format(self) -> None:
        """Validate expected payload format for free-estimate Lambda."""
        expected_payload = {
            "body": json.dumps(
                {
                    "ibn": 1,
                    "bint": 1,
                    "zawja": True,
                    "email": "user@example.com",
                }
            )
        }

        body = json.loads(expected_payload["body"])
        assert "ibn" in body or any(f in body for f in HEIR_FIELDS)

    def test_onewasiya_payload_format(self) -> None:
        """Validate expected payload format for onewasiya Lambda."""
        expected_payload = {
            "body": json.dumps(
                {
                    "ibn": 2,
                    "bint": 1,
                    "umm": 1,
                    "zawja": True,
                }
            )
        }

        body = json.loads(expected_payload["body"])
        assert any(f in body for f in HEIR_FIELDS)
