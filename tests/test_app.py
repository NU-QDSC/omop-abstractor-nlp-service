import textabstractor
from fastapi.encoders import jsonable_encoder
from textabstractor.dataclasses import (
    AbstractionSchema,
    AbstractionSchemaMetaData,
)


def test_greeting(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "OMOP Abstractor NLP Service"}


def test_get_abstraction_schema(client, schemas, suggest_request, monkeypatch):
    def mock_get_abstraction_schema(schema_meta_data: AbstractionSchemaMetaData):
        return schemas[285]

    monkeypatch.setattr(
        textabstractor.textabstract,
        "get_abstraction_schema",
        mock_get_abstraction_schema,
    )

    # test the web service api
    response = client.get(f"/abstractor_abstraction_schemas/{'285.json'}")
    assert response.status_code == 200
    schema = AbstractionSchema(**response.json())
    assert schema is not None

    # test the textabstract api
    schema_meta_285 = suggest_request.abstractor_abstraction_schemas[0]
    schema = textabstractor.textabstract.get_abstraction_schema(schema_meta_285)
    assert schema is not None
    assert schema.predicate == "has_cancer_histology"


def test_accept_suggestions(client, suggestion_set):
    response = client.post(
        "/abstractor_abstractions.json",
        json=jsonable_encoder(suggestion_set),
    )
    assert response.status_code == 200
    assert response.json() == {
        "msg": f"accepted suggestions {suggestion_set.namespace_id}"
    }


def test_multiple_suggest(
    client, suggest_request, suggestion_set, schemas, monkeypatch
):
    def mock_extract_suggestions(request):
        return suggestion_set

    def mock_post_suggestions(abstractor_suggestions_uri, suggestions) -> bool:
        return True

    def mock_get_abstraction_schema(schema_uri):
        return schemas[285]

    monkeypatch.setattr(
        textabstractor.textabstract,
        "get_abstraction_schema",
        mock_get_abstraction_schema,
    )
    monkeypatch.setattr(
        textabstractor.textabstract, "extract_suggestions", mock_extract_suggestions
    )
    monkeypatch.setattr(textabstractor.main, "post_suggestions", mock_post_suggestions)

    response = client.post(
        "/multiple_suggest",
        json=jsonable_encoder(suggest_request),
    )

    assert response.status_code == 202
    assert response.json() == {"request.source_id": 2823317, "status": "accepted"}
