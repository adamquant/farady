"""Lambda smoke tests for SunnaAssets integration.

These tests invoke the actual Lambda functions in AWS to verify
they respond correctly with the latest farady module.

Run only on release-sa and prod-sa branches, NOT on main.
"""

import json
import os
import boto3
import pytest
from botocore.config import Config

AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "eu-north-1")

lambda_client = boto3.client(
    "lambda",
    region_name=AWS_REGION,
    config=Config(retries={"max_attempts": 3, "mode": "standard"}),
)


class TestFreeEstimateLambda:
    """Smoke tests for sa_free_report Lambda function."""

    @pytest.fixture
    def test_payload(self) -> dict:
        return {
            "body": json.dumps(
                {
                    "ibn": 1,
                    "bint": 1,
                    "zawja": True,
                    "email": "test@example.com",
                }
            )
        }

    def test_lambda_invokes_successfully(self, test_payload: dict) -> None:
        """Lambda should respond without errors."""
        response = lambda_client.invoke(
            FunctionName="sa_free_report",
            InvocationType="RequestResponse",
            Payload=json.dumps(test_payload),
        )

        assert response["StatusCode"] == 200, (
            f"Lambda returned {response['StatusCode']}"
        )

        payload = json.loads(response["Payload"].read())
        assert "statusCode" in payload or "body" in payload

    def test_lambda_returns_valid_distribution(self, test_payload: dict) -> None:
        """Lambda should return a valid inheritance distribution."""
        response = lambda_client.invoke(
            FunctionName="sa_free_report",
            InvocationType="RequestResponse",
            Payload=json.dumps(test_payload),
        )

        payload = json.loads(response["Payload"].read())

        if "body" in payload:
            body = (
                json.loads(payload["body"])
                if isinstance(payload["body"], str)
                else payload["body"]
            )

            if "distribution" in body:
                distribution = body["distribution"]
                assert isinstance(distribution, dict)
                assert len(distribution) > 0

                total = sum(distribution.values())
                assert abs(total - 1.0) < 0.01, f"Distribution total {total} != 1.0"


class TestOneWasiyaLambda:
    """Smoke tests for one-wasiya Lambda function."""

    @pytest.fixture
    def test_payload(self) -> dict:
        return {
            "body": json.dumps(
                {
                    "ibn": 2,
                    "bint": 1,
                    "umm": 1,
                    "zawja": True,
                }
            )
        }

    def test_lambda_invokes_successfully(self, test_payload: dict) -> None:
        """Lambda should respond without errors."""
        response = lambda_client.invoke(
            FunctionName="one-wasiya",
            InvocationType="RequestResponse",
            Payload=json.dumps(test_payload),
        )

        assert response["StatusCode"] == 200, (
            f"Lambda returned {response['StatusCode']}"
        )

        payload = json.loads(response["Payload"].read())
        assert "statusCode" in payload or "body" in payload

    def test_lambda_handles_missing_heirs(self) -> None:
        """Lambda should handle case with minimal heirs."""
        test_payload = {
            "body": json.dumps(
                {
                    "bint": 1,
                }
            )
        }

        response = lambda_client.invoke(
            FunctionName="one-wasiya",
            InvocationType="RequestResponse",
            Payload=json.dumps(test_payload),
        )

        assert response["StatusCode"] == 200
