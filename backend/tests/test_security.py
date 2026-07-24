import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DB_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-long-enough-for-security")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.schemas import AssignRequest, EmployeeRequest, LoginRequest
from scripts.seed_users import load_admin_credentials
from security.jwt import create_token, decode_token
from security.rate_limit import SlidingWindowRateLimiter


class SecurityTests(unittest.TestCase):
    def test_jwt_has_required_claims_and_rejects_tampering(self):
        token = create_token("admin", "ADMIN")
        payload = decode_token(token)
        self.assertEqual(payload["sub"], "admin")
        self.assertEqual(payload["role"], "ADMIN")
        with self.assertRaises(Exception):
            decode_token(token + "tampered")

    def test_request_schemas_normalize_and_reject_unsafe_identifiers(self):
        self.assertEqual(EmployeeRequest(employee=" abc-123 ").employee, "ABC-123")
        self.assertEqual(AssignRequest(employee="abc123", note="  review needed ").note, "review needed")
        with self.assertRaises(Exception):
            EmployeeRequest(employee="abc'; DROP TABLE users;")
        with self.assertRaises(Exception):
            LoginRequest(username="<script>", password="password123")

    def test_rate_limiter_blocks_after_limit(self):
        limiter = SlidingWindowRateLimiter()
        for _ in range(2):
            self.assertEqual(limiter.check("ip", limit=2, window_seconds=60), 0)
        self.assertGreater(limiter.check("ip", limit=2, window_seconds=60), 0)

    def test_admin_seed_requires_a_strong_environment_password(self):
        with patch.dict(
            os.environ,
            {
                "SEED_ADMIN_USERNAME": "security-admin",
                "SEED_ADMIN_PASSWORD": "unique-seed-password-123",
            },
        ):
            self.assertEqual(
                load_admin_credentials(),
                ("security-admin", "unique-seed-password-123"),
            )

        with patch.dict(os.environ, {"SEED_ADMIN_PASSWORD": "short"}):
            with self.assertRaises(RuntimeError):
                load_admin_credentials()


if __name__ == "__main__":
    unittest.main()
