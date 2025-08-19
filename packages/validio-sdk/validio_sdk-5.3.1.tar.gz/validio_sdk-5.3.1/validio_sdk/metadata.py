"""Metadata information about the package."""

import importlib.metadata


def version() -> str:
    """Get the version of the SDK from the metadata."""
    try:
        return importlib.metadata.version(
            "validio-sdk"
        )  # This needs to match the distribution package name
    except importlib.metadata.PackageNotFoundError:
        return "local-dev"
