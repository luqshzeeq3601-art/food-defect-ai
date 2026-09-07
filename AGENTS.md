# Agent Developer Guidelines (AGENTS.md)

This document dictates strict developer rules, code quality standards, and operating protocols for any AI agent or contributor developing this codebase.

---

## 1. Core Operating Principles
* **Industrial Mindset:** Write code suitable for 24/7 industrial factory deployment. Prioritize deterministic logic, defensive input checks, and zero unhandled exceptions.
* **No Half-Implemented Code:** Never commit mock placeholders, `pass`, or `TODO` comments without full implementation. All functions must be working and tested.
* **Preserve Contracts:** Always maintain the data contracts defined in [Data.md](file:///c:/Users/ZeeqRyz/Desktop/Food%20Defect%20AI/Data.md) and invariants in [ARCHITECTURE-ESSENTIALS.md](file:///c:/Users/ZeeqRyz/Desktop/Food%20Defect%20AI/ARCHITECTURE-ESSENTIALS.md).

---

## 2. Python Coding Standards
* **Python Version:** Python 3.10+
* **Style Guide:** Strict adherence to PEP 8.
* **Type Annotations:** Full type hints required on all function arguments, return types, and class attributes.
  ```python
  def calculate_defect_ratio(fruit_pixels: int, defect_pixels: int) -> float:
      if fruit_pixels <= 0:
          return 0.0
      return (defect_pixels / fruit_pixels) * 100.0
  ```
* **Docstrings:** Google-style docstrings for every public class, method, and function.
* **Error Handling:** Use custom exceptions derived from a base `AOIError` in `src.core.exceptions`. Never catch bare `except:`.

---

## 3. Testing & Verification Requirements
* **Test Framework:** `pytest`
* **Test Coverage:** All business logic (`src/core/grader.py`, `src/core/detector.py`) must have unit test coverage $\ge 90\%$.
* **Run Tests Command:**
  ```bash
  pytest -v --tb=short
  ```
* **Linting & Formatting Command:**
  ```bash
  ruff check src/ tests/
  black --check src/ tests/
  ```

---

## 4. Git & Workflow Conventions
* **Branch Strategy:** `main` (production-ready) $\leftarrow$ feature branches (`feature/onnx-detector`, `feature/api-routes`).
* **Commit Messages:** Follow Conventional Commits:
  * `feat: add ONNX instance segmentation runner`
  * `fix: correct letterbox scaling offset on non-square aspect ratio`
  * `test: add unit tests for grading logic thresholds`
  * `docs: update PRD with ViTrox AOI specs`

---

## 5. Security & Safety Checklist Before Every Commit
* No hardcoded file paths (use `pathlib.Path` relative to root or environment variables).
* No secrets, API keys, or private paths checked into git.
* Memory safety: Explicitly clean up large OpenCV/NumPy arrays when processing high-volume batches.
