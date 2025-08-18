from __future__ import annotations

import subprocess
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface  # pyright: ignore[reportMissingImports]


class CustomBuildHook(BuildHookInterface):
    """Custom build hook to compile Django message files before packaging."""

    def initialize(self, version: str, build_data: dict[str, object]) -> None:  # noqa: ARG002
        """
        Compile Django translation files (.po → .mo) before building.

        Args:
            version: The version being built (not used).
            build_data: Metadata about the build (not used).

        """
        root: Path = Path(self.root)

        try:
            subprocess.run(  # noqa: S603
                [  # noqa: S607
                    "python",
                    "-m",
                    "django",
                    "compilemessages",
                    "--ignore",
                    ".nox",
                    "--ignore",
                    ".venv",
                    "--ignore",
                    ".cache",
                ],
                cwd=root,
                check=True,
            )
            print("✅ Django messages compiled")  # noqa: T201
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Failed to compile Django translation messages") from e
