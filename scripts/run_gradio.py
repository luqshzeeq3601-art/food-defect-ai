"""CLI runner to launch the industrial Food Defect AOI Gradio Operator Dashboard."""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ui.gradio_app import build_gradio_app


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the Gradio runner.

    Returns:
        argparse.Namespace with host, port, and share flags.
    """
    parser = argparse.ArgumentParser(
        description="Launch ViTrox Inspec-Belt AI Gradio Operator Dashboard.",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host interface to bind server (default: 127.0.0.1).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Port number to serve Gradio dashboard (default: 7860).",
    )
    parser.add_argument(
        "--share",
        action="store_true",
        default=False,
        help="Create a public shareable Hugging Face Gradio link.",
    )
    return parser.parse_args()


def main() -> None:
    """Main execution function for launching Gradio application."""
    args = parse_args()
    print("============================================================")
    print(
        f"Starting Food Defect AOI Gradio Dashboard on http://{args.host}:{args.port}"
    )
    print("============================================================")

    demo = build_gradio_app()
    demo.launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
    )


if __name__ == "__main__":
    main()
