#!/usr/bin/env python3
"""End-to-end smoke test against running infrastructure."""

import sys
import time

import httpx

API_BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "demo-key-12345"
HEALTH_URL = "http://localhost:8000/healthz"

TIMEOUT_SECONDS = 60


class SmokeTest:
    """End-to-end smoke test suite."""

    def __init__(self):
        """Initialize the test."""
        self.passed = 0
        self.failed = 0
        self.client = httpx.Client(
            headers={"X-API-Key": API_KEY},
            timeout=10.0,
        )

    def log(self, message: str) -> None:
        """Log a message."""
        print(f"[TEST] {message}")

    def passed_test(self, name: str) -> None:
        """Mark a test as passed."""
        self.passed += 1
        self.log(f"✓ {name}")

    def failed_test(self, name: str, error: str) -> None:
        """Mark a test as failed."""
        self.failed += 1
        self.log(f"✗ {name}: {error}")

    def wait_for_api(self, max_attempts: int = 30) -> bool:
        """Wait for the API to be ready.

        Args:
            max_attempts: Maximum attempts to connect.

        Returns:
            True if API is ready, False if timeout.
        """
        for attempt in range(max_attempts):
            try:
                response = self.client.get(HEALTH_URL)
                if response.status_code == 200:
                    self.log("API is ready")
                    return True
            except Exception:
                pass

            if attempt < max_attempts - 1:
                time.sleep(1)

        return False

    def test_health_check(self) -> bool:
        """Test health check endpoint.

        Returns:
            True if test passed.
        """
        try:
            response = self.client.get(HEALTH_URL)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    self.passed_test("Health check")
                    return True
        except Exception:
            pass

        self.failed_test("Health check", "API not responding")
        return False

    def test_kv_store(self) -> bool:
        """Test KV store operations.

        Returns:
            True if test passed.
        """
        try:
            test_key = "smoke_test_key"
            test_value = "smoke_test_value"

            response = self.client.post(
                f"{API_BASE_URL}/kv/{test_key}",
                json={"value": test_value},
            )
            if response.status_code != 200:
                self.failed_test("KV store set", f"Status {response.status_code}")
                return False

            response = self.client.get(f"{API_BASE_URL}/kv/{test_key}")
            if response.status_code != 200:
                self.failed_test("KV store get", f"Status {response.status_code}")
                return False

            data = response.json()
            if data.get("value") != test_value:
                self.failed_test("KV store get", f"Value mismatch: {data.get('value')}")
                return False

            response = self.client.delete(f"{API_BASE_URL}/kv/{test_key}")
            if response.status_code != 200:
                self.failed_test("KV store delete", f"Status {response.status_code}")
                return False

            self.passed_test("KV store operations")
            return True
        except Exception as e:
            self.failed_test("KV store operations", str(e))
            return False

    def test_scan_trigger(self) -> bool:
        """Test scan triggering and status polling.

        Returns:
            True if test passed.
        """
        try:
            response = self.client.post(
                f"{API_BASE_URL}/scans",
                json={"path": "."},
            )
            if response.status_code != 200:
                self.failed_test("Scan trigger", f"Status {response.status_code}")
                return False

            data = response.json()
            job_id = data.get("job_id")
            if not job_id:
                self.failed_test("Scan trigger", "No job ID returned")
                return False

            response = self.client.get(f"{API_BASE_URL}/scans/{job_id}")
            if response.status_code != 200:
                self.failed_test("Scan status", f"Status {response.status_code}")
                return False

            data = response.json()
            status = data.get("status")
            if status not in ("queued", "running", "completed", "failed"):
                self.failed_test("Scan status", f"Invalid status: {status}")
                return False

            self.passed_test("Scan trigger and status polling")
            return True
        except Exception as e:
            self.failed_test("Scan trigger", str(e))
            return False

    def test_findings_list(self) -> bool:
        """Test findings list endpoint.

        Returns:
            True if test passed.
        """
        try:
            response = self.client.get(f"{API_BASE_URL}/findings")
            if response.status_code != 200:
                self.failed_test("Findings list", f"Status {response.status_code}")
                return False

            data = response.json()
            if not isinstance(data, list):
                self.failed_test("Findings list", "Response is not a list")
                return False

            self.passed_test("Findings list")
            return True
        except Exception as e:
            self.failed_test("Findings list", str(e))
            return False

    def test_webhooks(self) -> bool:
        """Test webhook subscription management.

        Returns:
            True if test passed.
        """
        try:
            webhook_url = "http://localhost:9999/webhook"
            response = self.client.post(
                f"{API_BASE_URL}/webhooks",
                json={
                    "url": webhook_url,
                    "event_types": "scan.completed",
                },
            )
            if response.status_code != 200:
                self.failed_test("Webhook create", f"Status {response.status_code}")
                return False

            data = response.json()
            subscription_id = data.get("id")

            response = self.client.get(f"{API_BASE_URL}/webhooks")
            if response.status_code != 200:
                self.failed_test("Webhook list", f"Status {response.status_code}")
                return False

            data = response.json()
            if not isinstance(data, list):
                self.failed_test("Webhook list", "Response is not a list")
                return False

            if subscription_id:
                response = self.client.delete(
                    f"{API_BASE_URL}/webhooks/{subscription_id}"
                )
                if response.status_code != 200:
                    self.failed_test("Webhook delete", f"Status {response.status_code}")
                    return False

            self.passed_test("Webhook management")
            return True
        except Exception as e:
            self.failed_test("Webhook management", str(e))
            return False

    def test_api_key_validation(self) -> bool:
        """Test API key validation.

        Returns:
            True if test passed.
        """
        try:
            client = httpx.Client(timeout=10.0)
            response = client.get(f"{API_BASE_URL}/findings")
            if response.status_code != 401:
                self.failed_test(
                    "API key validation", f"Expected 401, got {response.status_code}"
                )
                return False

            self.passed_test("API key validation")
            return True
        except Exception as e:
            self.failed_test("API key validation", str(e))
            return False

    def run_all_tests(self) -> int:
        """Run all smoke tests.

        Returns:
            Exit code (0 = all passed, 1 = any failed).
        """
        self.log("Starting end-to-end smoke tests...")
        self.log(f"API URL: {API_BASE_URL}")

        if not self.wait_for_api():
            self.log("ERROR: API did not become ready within timeout")
            return 1

        self.test_health_check()
        self.test_api_key_validation()
        self.test_kv_store()
        self.test_findings_list()
        self.test_scan_trigger()
        self.test_webhooks()

        self.log("")
        self.log(f"Results: {self.passed} passed, {self.failed} failed")

        if self.failed > 0:
            return 1
        return 0


def main() -> int:
    """Run smoke tests.

    Returns:
        Exit code.
    """
    try:
        test = SmokeTest()
        return test.run_all_tests()
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
