import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DB_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-long-enough-for-security")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.assign_routes import BREVO_EMAIL_URL, EmailDeliveryError, send_email


class EmailNotificationTests(unittest.TestCase):
    @patch("api.assign_routes.httpx.Client")
    def test_assignment_uses_brevo_https_api(self, client_class):
        client = client_class.return_value.__enter__.return_value
        response = client.post.return_value

        with patch.dict(
            os.environ,
            {
                "BREVO_API_KEY": "test-brevo-key",
                "ADMIN_EMAIL": "verified-sender@example.com",
                "MAIL_FROM_NAME": "InsiderSentinel",
                "ANALYST_EMAIL": "analyst@example.com",
            },
        ):
            send_email("ABC123", "Review unusual activity")

        client_class.assert_called_once_with(timeout=10)
        response.raise_for_status.assert_called_once_with()
        client.post.assert_called_once_with(
            BREVO_EMAIL_URL,
            headers={
                "accept": "application/json",
                "api-key": "test-brevo-key",
                "content-type": "application/json",
            },
            json={
                "sender": {
                    "name": "InsiderSentinel",
                    "email": "verified-sender@example.com",
                },
                "to": [{"email": "analyst@example.com"}],
                "subject": "Employee ABC123 Assigned for Review",
                "textContent": (
                    "Employee: ABC123\n\n"
                    "Admin Note:\n"
                    "Review unusual activity\n"
                ),
            },
        )

    @patch("api.assign_routes.httpx.Client")
    def test_missing_configuration_does_not_attempt_delivery(self, client_class):
        with patch.dict(
            os.environ,
            {
                "BREVO_API_KEY": "",
                "ADMIN_EMAIL": "",
                "MAIL_FROM_EMAIL": "",
                "ANALYST_EMAIL": "",
            },
        ):
            with self.assertRaises(EmailDeliveryError):
                send_email("ABC123", "Review")

        client_class.assert_not_called()

    @patch("api.assign_routes.httpx.Client")
    def test_brevo_rejection_is_reported(self, client_class):
        client = client_class.return_value.__enter__.return_value
        response = client.post.return_value
        response.status_code = 400
        response.json.return_value = {"code": "invalid_parameter"}
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Rejected",
            request=httpx.Request("POST", BREVO_EMAIL_URL),
            response=httpx.Response(400),
        )

        with patch.dict(
            os.environ,
            {
                "BREVO_API_KEY": "test-brevo-key",
                "MAIL_FROM_EMAIL": "unverified@example.com",
                "MAIL_FROM_NAME": "InsiderSentinel",
                "ANALYST_EMAIL": "analyst@example.com",
            },
        ):
            with self.assertRaises(EmailDeliveryError):
                send_email("ABC123", "Review")

    @patch("api.assign_routes.httpx.Client")
    def test_mail_from_email_takes_priority_over_admin_email(self, client_class):
        with patch.dict(
            os.environ,
            {
                "BREVO_API_KEY": "test-brevo-key",
                "ADMIN_EMAIL": "old-sender@example.com",
                "MAIL_FROM_EMAIL": "notifications@insidersentinel.live",
                "MAIL_FROM_NAME": "InsiderSentinel",
                "ANALYST_EMAIL": "analyst@example.com",
            },
        ):
            send_email("ABC123", "Review unusual activity")

        client = client_class.return_value.__enter__.return_value
        client.post.assert_called_once()
        _, kwargs = client.post.call_args
        self.assertEqual(
            kwargs["json"]["sender"],
            {
                "name": "InsiderSentinel",
                "email": "notifications@insidersentinel.live",
            },
        )


if __name__ == "__main__":
    unittest.main()
