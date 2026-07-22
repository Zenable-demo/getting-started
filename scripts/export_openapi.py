#!/usr/bin/env python3
"""Export OpenAPI spec from FastAPI app to openapi.json."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from getting_started.api.app import create_app


def main() -> int:
    """Export OpenAPI spec and write to file.

    Returns:
        Exit code (0 = success).
    """
    try:
        app = create_app()
        openapi_spec = app.openapi()

        repo_root = Path(__file__).parent.parent
        output_file = repo_root / "openapi.json"

        with output_file.open("w") as f:
            json.dump(openapi_spec, f, indent=2)

        print(f"✓ OpenAPI spec exported to {output_file}")
        return 0
    except Exception as e:
        print(f"✗ Failed to export OpenAPI spec: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
