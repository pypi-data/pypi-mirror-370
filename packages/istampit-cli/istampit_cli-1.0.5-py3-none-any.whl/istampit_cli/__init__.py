"""Version constant for istampit-cli.

We intentionally keep this minimal to avoid indentation tooling issues.
Runtime version is resolved via importlib.metadata in __main__ when needed.
"""

__all__ = ["__version__"]

# Fallback source version; packaging metadata provides the real version when installed.
__version__ = "0.0.0"

