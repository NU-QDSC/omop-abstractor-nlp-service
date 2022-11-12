import pytest
import json
from typing import Dict
from importlib_resources import files
from starlette.testclient import TestClient
from textabstractor.main import app
import textabstractor_testdata.breast as data
from textabstractor.dataclasses import (
    AbstractionSchema,
    SuggestRequest,
    SuggestionSet,
    ProcessTextResponse,
)


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def suggest_request() -> SuggestRequest:
    json_dict = json.loads(files(data).joinpath("request.json").read_text())
    return SuggestRequest(**json_dict)


@pytest.fixture(scope="session")
def suggestion_set() -> SuggestionSet:
    json_dict = json.loads(files(data).joinpath("suggestion_set.json").read_text())
    return SuggestionSet(**json_dict)


@pytest.fixture(scope="session")
def schemas() -> Dict[int, AbstractionSchema]:
    schemas = {}
    for i in range(285, 300):
        json_dict = json.loads(files(data).joinpath(f"{str(i)}.json").read_text())
        schemas[i] = AbstractionSchema(**json_dict["abstractor_abstraction_schema"])
    return schemas


@pytest.fixture(scope="session")
def process_text_responses() -> Dict[str, ProcessTextResponse]:
    responses = {}
    predicates = [
        "has_cancer_histology",
        "has_cancer_site",
        "has_surgery_date",
        "pathological_tumor_staging_category",
    ]
    for pred in predicates:
        json_dict = json.loads(
            files(data).joinpath(f"process_text_{pred}.json").read_text()
        )
        responses[pred] = ProcessTextResponse(**json_dict)
    return responses
