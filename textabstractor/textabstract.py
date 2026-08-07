import requests
import pluggy
import textabstractor
from typing import List, Dict, Tuple
from fastapi import HTTPException
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from textabstractor import hookspecs
from textabstractor.dataclasses import (
    ProcessTextResponse,
    SuggestRequest,
    SuggestionSet,
    AbstractionSchema,
    AbstractionSchemaMetaData,
)


def get_plugin_manager():
    pm = pluggy.PluginManager(textabstractor.__project_name__)
    pm.add_hookspecs(hookspecs)
    pm.load_setuptools_entrypoints(textabstractor.__project_name__)
    return pm


plugin_manager = get_plugin_manager()


# TODO: replace with TinyDB or sqlite
schema_cache: Dict[str, Tuple[AbstractionSchemaMetaData, AbstractionSchema]] = {}

SCHEMA_FETCH_TIMEOUT = (5, 30)  # (connect, read) seconds
_session = requests.Session()
_adapter = HTTPAdapter(max_retries=Retry(
    total=4, backoff_factor=0.5,
    status_forcelist=(408, 429, 500, 502, 503, 504)))
_session.mount("http://", _adapter)
_session.mount("https://", _adapter)

def get_abstraction_schema(
    schema_metadata: AbstractionSchemaMetaData,
) -> AbstractionSchema:
    if schema_metadata.abstractor_abstraction_schema_uri in schema_cache:
        m, s = schema_cache[schema_metadata.abstractor_abstraction_schema_uri]
        if schema_metadata.updated_at <= m.updated_at:
            return s

    resp = _session.get(schema_metadata.abstractor_abstraction_schema_uri, timeout=SCHEMA_FETCH_TIMEOUT)
    if not resp.ok:
        raise HTTPException(
            status_code=404,
            detail=f"schema not found: {schema_metadata.abstractor_abstraction_schema_uri}",
        )

    if "abstractor_abstraction_schema" in resp.json():
        schema = AbstractionSchema(**resp.json()["abstractor_abstraction_schema"])
    else:
        schema = AbstractionSchema(**resp.json())
    schema_cache[schema_metadata.abstractor_abstraction_schema_uri] = (
        schema_metadata,
        schema,
    )
    return schema


def extract_suggestions(request: SuggestRequest) -> SuggestionSet:
    suggestion_set = SuggestionSet(
        namespace_type=request.namespace_type,
        namespace_id=request.namespace_id,
        sentences=[],
        sections=[],
        abstractor_suggestions=[],
    )
    responses: List[ProcessTextResponse] = plugin_manager.hook.process_text(
        request=request
    )
    if len(responses) > 0:
        suggestion_set.sentences = responses[0].sentences
        suggestion_set.sections = responses[0].sections
    for resp in responses:
        suggestion_set.abstractor_suggestions += resp.suggestions
    return suggestion_set
