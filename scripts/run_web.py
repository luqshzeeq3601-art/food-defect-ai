"""Launcher script for modern Food Defect AI web station."""

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Entry point for launching the modern web station."""
    parser = argparse.ArgumentParser(
        description="Launch Food Defect AI Modern Web Station"
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Run Vite development server on port 5173 with hot reload",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for the FastAPI backend / full-stack server (default: 8000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host interface (default: 127.0.0.1)",
    )
    args = parser.parse_args()

    root_dir = Path(__file__).resolve().parent.parent
    frontend_dir = root_dir / "frontend"

    if args.dev:
        print("Starting Vite development workstation on http://localhost:5173...")
        cmd = ["npm", "run", "dev"]
        subprocess.run(cmd, cwd=str(frontend_dir), shell=True, check=False)
    else:
        print(
            f"Starting Food Defect AI Unified Station on http://{args.host}:{args.port}..."
        )
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "src.api.main:app",
            "--host",
            args.host,
            "--port",
            str(args.port),
        ]
        subprocess.run(cmd, cwd=str(root_dir), check=False)


if __name__ == "__main__":
    main()
