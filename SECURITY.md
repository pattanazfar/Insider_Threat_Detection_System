# Security and production operations

This system processes employee-behavior data. Deploy only with authorization, data minimization, and the retention controls required by your organization. Do not use public demo infrastructure for real employee data.

## Implemented application controls

- **Confidentiality:** secrets are environment-only, CORS is allowlisted, TLS is required at the deployment edge, API responses are no-store, browser security headers and CSP are set, and employee identifiers are no longer sent to an external avatar service.
- **Integrity:** Argon2 password verification, signed JWTs with issuer/audience/expiry claims, role checks on every privileged API route, strict request validation, ORM query parameters, and audit events for privileged actions.
- **Availability:** database health check, connection-pool health checks, request-size limit, login rate limit, timeouts, and generic error responses.

## Deployment requirements

1. Generate a 48-byte random `SECRET_KEY`; never reuse the local value.
2. Set `ENVIRONMENT=production`, `CORS_ORIGINS` to the exact Netlify HTTPS origin, and `VITE_API_URL` to the exact Render HTTPS API origin.
3. Enforce HTTPS at Netlify, Render, and the database. Use a least-privilege database account and do not expose the database publicly except to the backend's allowed network path.
4. Keep database backups encrypted and test restoration. Retain audit logs in a protected central log system; Render stdout logs alone are not a durable audit store.
5. Set a unique `SEED_ADMIN_PASSWORD`, run the admin seed once, then remove that variable from the deployment environment. Restrict administrator access and implement MFA through an identity provider before handling real data.
6. Configure `BREVO_API_KEY`, a verified Brevo sender in `MAIL_FROM_EMAIL`, an optional display name in `MAIL_FROM_NAME`, and the intended recipient in `ANALYST_EMAIL`. `ADMIN_EMAIL` is supported only as a fallback for older deployments. Email is sent through Brevo's HTTPS API, so no SMTP port is required.
7. Put rate limiting, a web-application firewall, DDoS protection, monitoring, alerting, vulnerability scanning, and incident-response procedures at the hosting layer.
8. After upgrading scikit-learn, retrain and validate the included model artifacts before release; serialized ML models are version-sensitive.

## OWASP coverage and remaining infrastructure work

The code addresses broken access control, cryptographic failures, injection, insecure design safeguards, security misconfiguration, authentication failures, integrity checks, logging, and request abuse controls. No source change alone can make a system OWASP-complete: keep dependencies patched, use a secrets manager, run SAST/DAST and a penetration test, and have an independent security review before production use.
