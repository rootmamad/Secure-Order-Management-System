# Security Policy

## Supported Versions

Currently, only the `main` branch is receiving security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please **DO NOT** open a public issue. 

Instead, please email the maintainer directly at `rootmamad06@gmail.com`. Security issues will be treated with the highest priority, and a patch will be developed and released as quickly as possible.

## Security Architecture & Mitigations

This project was built with a "security-first" mindset. The following vulnerabilities have been explicitly modeled and mitigated:

1. **Insecure Direct Object Reference (IDOR):**
   * *Mitigation:* All data retrieval logic (e.g., fetching an order) validates the `user_id` extracted from the verified JWT against the owner of the resource in the database.
   
2. **Broken Authentication & Session Management:**
   * *Mitigation:* Passwords are hashed using `bcrypt` with a high work factor.
   * *Mitigation:* The system utilizes short-lived Access Tokens and long-lived Refresh Tokens. 
   * *Mitigation:* **Refresh Token Rotation** is strictly enforced. When a refresh token is used, it is deleted from the database and a new one is issued, preventing infinite session hijacking.

3. **Race Conditions (TOCTOU):**
   * *Mitigation:* Critical operations, such as user registration checking for existing usernames, rely on database-level `UNIQUE` constraints rather than application-layer "Check-then-Act" logic.

4. **Brute Force Attacks:**
   * *Mitigation:* The API employs **SlowAPI** to enforce strict rate limits on authentication endpoints based on client IP addresses.

5. **Information Leakage:**
   * *Mitigation:* Detailed tracebacks are disabled in production. Standard HTTP exception models are used to prevent internal system configurations or stack traces from reaching the client.
