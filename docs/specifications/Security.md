# Security & Risk Controls (Security.md)

This document outlines safety, risk mitigation, input sanitization, and runtime security rules for the Food Defect AOI system.

---

## 1. Input Validation & Attack Mitigation
* **Maximum File Upload Size:** Enforced limit of $10\text{ MB}$ per image payload to prevent Denial of Service (DoS) attacks via memory exhaustion.
* **MIME Type Whitelist:**
  * Permitted: `image/jpeg`, `image/png`, `image/bmp`.
  * All other MIME types rejected with HTTP 415 (Unsupported Media Type).
* **Payload Verification:** Images decoded using OpenCV / Pillow with strict byte validation; corrupt streams return structured HTTP 422 errors instead of crashing the process.

---

## 2. Secrets & Environment Isolation
* **Zero Hardcoded Secrets:** Configuration keys (e.g., Roboflow API keys, database credentials) loaded strictly from `.env` using `pydantic-settings`.
* **Git Protection:** `.env`, `.venv/`, raw credentials, and debug dumps are permanently excluded in `.gitignore`.

---

## 3. Container & Runtime Security
* **Non-Root Execution:** Docker containers must run under an unprivileged `appuser` (`UID 10001`), never as `root`.
* **Minimal Attack Surface:** Base image uses `python:3.10-slim` with unnecessary compiler packages purged in the final build stage.
* **Network Isolation:** In Docker Compose, the internal FastAPI service communicates with the Streamlit frontend via a private container network bridge.

---

## 4. Failure Handling & Industrial Safety
* **Fail-Safe Principle (False Acceptance Mitigation):**
  * If the model confidence on fruit presence is below $0.40$ or an image is corrupted, the item is marked as `REJECT` or flagged for manual review, never marked as `PASS`.
* **Error Masking:** API endpoints must return generic error messages (e.g., `{"detail": "Image decode error"}`) and never leak internal stack traces or server file paths to the caller.
