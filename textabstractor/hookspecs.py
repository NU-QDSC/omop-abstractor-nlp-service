import pluggy
import textabstractor
from textabstractor.dataclasses import (
    SuggestRequest,
    ProcessTextResponse,
)


hookspec = pluggy.HookspecMarker(textabstractor.__project_name__)


@hookspec
def handles_predicate(predicate: str) -> bool:
    """ """


@hookspec
def process_text(request: SuggestRequest) -> ProcessTextResponse:
    """ """
