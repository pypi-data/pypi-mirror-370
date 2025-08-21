import os
import sys

# Dynamically add the generated proto directory to sys.path
proto_path = os.path.join(os.path.dirname(__file__), "core", "protos", "generated")
if proto_path not in sys.path:
    sys.path.append(proto_path)

# Package version
try:
    from importlib import metadata
    __version__ = metadata.version("simplexpy")
except Exception:
    __version__ = "Development"  # Development version