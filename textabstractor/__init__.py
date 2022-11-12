from textabstractor.about import __project_name__, __version__  # noqa F401
from textabstractor import dataclasses  # noqa F401
from textabstractor import textabstract  # noqa: E402, F401
from textabstractor import hookspecs  # noqa: E402, F401
from textabstractor import main  # noqa: E402, F401
import pluggy

hookimpl = pluggy.HookimplMarker(__project_name__)
