import os
import json
import pluggy
import pytest
from rich import print
from importlib_resources import files
import textabstractor
import textabstractor_testdata.breast as data
from pathlib import Path
from textabstractor import hookspecs
from textabstractor.dataclasses import (
    SuggestionSet,
    SuggestRequest,
    ProcessTextResponse,
)

# ---------------------------------------------------------------
# Plugin project setup.py contents:
# ---------------------------------------------------------------
# from setuptools import setup
#
# setup(
#     name="omop_nlp_plugin",
#     install_requires=["omop_abstractor_nlp"],
#     entry_points={"omop_abstractor_nlp": ["nlp = omop_nlp"]},
#     py_modules=["omop_nlp"],
# )
# ---------------------------------------------------------------

dir_path = Path(os.path.dirname(os.path.realpath(__file__)))


class Plugin1:
    predicate = "has_cancer_histology"

    @staticmethod
    @textabstractor.hookimpl
    def process_text(request: SuggestRequest) -> ProcessTextResponse:
        json_dict = json.loads(
            files(data).joinpath(f"process_text_{Plugin1.predicate}.json").read_text()
        )
        suggestions = ProcessTextResponse(**json_dict)
        return suggestions


class Plugin2:
    predicate = "has_cancer_site"

    @staticmethod
    @textabstractor.hookimpl
    def process_text(request: SuggestRequest) -> ProcessTextResponse:
        json_dict = json.loads(
            files(data).joinpath(f"process_text_{Plugin2.predicate}.json").read_text()
        )
        suggestions = ProcessTextResponse(**json_dict)
        return suggestions


class Plugin3:
    predicate = "has_surgery_date"

    @staticmethod
    @textabstractor.hookimpl
    def process_text(request: SuggestRequest) -> ProcessTextResponse:
        json_dict = json.loads(
            files(data).joinpath(f"process_text_{Plugin3.predicate}.json").read_text()
        )
        suggestions = ProcessTextResponse(**json_dict)
        return suggestions


class Plugin4:
    predicate = "pathological_tumor_staging_category"

    @staticmethod
    @textabstractor.hookimpl
    def process_text(request: SuggestRequest) -> ProcessTextResponse:
        json_dict = json.loads(
            files(data).joinpath(f"process_text_{Plugin4.predicate}.json").read_text()
        )
        suggestions = ProcessTextResponse(**json_dict)
        return suggestions


@pytest.mark.parametrize(
    "plugins",
    [
        ([Plugin1]),
        ([Plugin2]),
        ([Plugin1, Plugin2]),
        ([Plugin1, Plugin2, Plugin3]),
        ([Plugin1, Plugin2, Plugin3, Plugin4]),
    ],
)
def test_nlp_plugins(
    suggest_request,
    schemas,
    suggestion_set,
    process_text_responses,
    monkeypatch,
    plugins,
):
    # monkeypatch the plugin manager
    pm = pluggy.PluginManager(textabstractor.__project_name__)
    pm.add_hookspecs(hookspecs)
    for p in plugins:
        pm.register(p)
    monkeypatch.setattr(textabstractor.textabstract, "plugin_manager", pm)

    # extract suggestions
    result = textabstractor.textabstract.extract_suggestions(suggest_request)

    # create expected result
    sections = []
    sentences = []
    suggestions = []
    for p in plugins:
        sections = process_text_responses[p.predicate].sections
        sentences = process_text_responses[p.predicate].sentences
        suggestions.extend(process_text_responses[p.predicate].suggestions)
    expected = SuggestionSet(
        namespace_type="Abstractor::AbstractorNamespace",
        namespace_id=48,
        sections=sections,
        sentences=sentences,
        abstractor_suggestions=suggestions,
    )

    # validate result
    assert result.namespace_type == expected.namespace_type
    assert result.namespace_id == expected.namespace_id
    assert result.sections == expected.sections
    assert result.sentences == expected.sentences
    assert len(result.abstractor_suggestions) == len(expected.abstractor_suggestions)
