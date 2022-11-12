import requests
import pluggy
import textabstractor
from typing import List, Dict, Tuple
from fastapi import HTTPException
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


def get_abstraction_schema(
    schema_metadata: AbstractionSchemaMetaData,
) -> AbstractionSchema:
    if schema_metadata.abstractor_abstraction_schema_uri in schema_cache:
        m, s = schema_cache[schema_metadata.abstractor_abstraction_schema_uri]
        if schema_metadata.updated_at <= m.updated_at:
            return s

    resp = requests.get(schema_metadata.abstractor_abstraction_schema_uri)
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
