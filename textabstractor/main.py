import requests
import logging
import logging.handlers
import json
from rich import print
from importlib_resources import files
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
import textabstractor_testdata.breast as data
from textabstractor import textabstract
from textabstractor.dataclasses import (
    AbstractionSchema,
    SuggestRequest,
    SuggestionSet,
)


# --------------------------------------------------------------------------------------------------
app = FastAPI()


# --------------------------------------------------------------------------------------------------
LOG_FILENAME = 'nlp_service.log'
logger = logging.getLogger(__name__)
logging.basicConfig(
    filename=LOG_FILENAME,
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO)
handler = logging.handlers.RotatingFileHandler(
    LOG_FILENAME, maxBytes=2_000_0000, backupCount=5)
logger.addHandler(handler)


# --------------------------------------------------------------------------------------------------
def handle_request(request: SuggestRequest) -> bool:
    suggestions = textabstract.extract_suggestions(request)
    return post_suggestions(request.note_abstractor_suggestions_uri, suggestions)


# --------------------------------------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    pass


# --------------------------------------------------------------------------------------------------
@app.on_event("shutdown")
def shutdown_event():
    pass


# --------------------------------------------------------------------------------------------------
@app.get("/", status_code=200)
async def greeting():
    print("")
    return {"msg": "OMOP Abstractor NLP Service"}


# --------------------------------------------------------------------------------------------------
def post_suggestions(
    abstractor_suggestions_uri: str, suggestions: SuggestionSet
) -> bool:
    try:
        resp = requests.post(abstractor_suggestions_uri, json=jsonable_encoder(suggestions))
        return resp.ok
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------------------------------------------------------------
@app.post("/multiple_suggest", status_code=202)
def multiple_suggest(background_tasks: BackgroundTasks, request: SuggestRequest):
    try:
        logger.info(f"request: {request.source_id}: {request.text[:100]}")
        background_tasks.add_task(handle_request, request=request)
        return {"status": "accepted", "request.source_id": request.source_id}
    except Exception as e:
        logger.error(f"multiple_suggest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --------------------------------------------------------------------------------------------------
@app.get(
    "/abstractor_abstraction_schemas/{schema_id}",
    status_code=200,
    response_model=AbstractionSchema,
)
def get_abstraction_schema_stub(schema_id: str) -> AbstractionSchema:
    print(f"getting schema: {schema_id}")
    json_text = files(data).joinpath(f"{schema_id}").read_text()
    json_dict = json.loads(json_text)
    schema = AbstractionSchema(**json_dict["abstractor_abstraction_schema"])
    return schema


# --------------------------------------------------------------------------------------------------
@app.post(
    "/abstractor_abstractions.json",
    status_code=200,
)
def accept_suggestions_stub(suggestions: SuggestionSet):
    print(suggestions)
    return {"msg": f"accepted suggestions {suggestions.namespace_id}"}
