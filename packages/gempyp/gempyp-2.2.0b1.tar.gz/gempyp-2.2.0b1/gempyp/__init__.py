try:
    from importlib import metadata
    __version__ = metadata.version("gempyp")
except metadata.PackageNotFoundError:
    __version__ = "2.1.0"  # fallback for local dev
