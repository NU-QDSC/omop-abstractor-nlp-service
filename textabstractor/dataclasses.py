import datetime
from pydantic import BaseModel
from typing import List


########################################################################################################################
class Variant(BaseModel):
    value: str
    case_sensitive: bool = False


class Entry(BaseModel):
    value: str
    properties: str = None
    vocabulary_code: str
    vocabulary: str = None
    vocabulary_version: str = None
    case_sensitive: bool
    object_value_variants: List[Variant]


class AbstractionSchema(BaseModel):
    predicate: str
    display_name: str
    abstractor_object_type: str
    preferred_name: str
    predicate_variants: List[Variant]
    object_values: List[Entry]


class AbstractionSchemaMetaData(BaseModel):
    abstractor_abstraction_schema_id: int
    abstractor_abstraction_schema_uri: str
    abstractor_abstraction_id: int
    abstractor_abstraction_source_id: int
    abstractor_subject_id: int
    namespace_type: str
    namespace_id: int
    abstractor_rule_type: str  # TODO: options are value and name-value
    abstractor_object_type: str  # TODO: type of value
    updated_at: datetime.datetime


########################################################################################################################
class AbstractorSectionNameVariants(BaseModel):
    name: str


class AbstractorSection(BaseModel):
    name: str
    section_mention_type: str
    section_name_variants: List[AbstractorSectionNameVariants]


class SuggestRequest(BaseModel):
    source_id: int
    source_type: str
    source_method: str
    text: str
    namespace_type: str
    namespace_id: int
    note_abstractor_suggestions_uri: str
    abstractor_abstraction_schemas: List[AbstractionSchemaMetaData] = []
    abstractor_sections: List[AbstractorSection]


########################################################################################################################
class SentenceSpan(BaseModel):
    sentence_number: int
    begin: int
    end: int


class SectionSpan(BaseModel):
    section_number: int
    section_name: str
    begin_header: int
    end_header: int
    begin: int
    end: int


class Suggestion(BaseModel):
    predicate: str
    begin: int
    end: int
    type: str
    value: str
    assertion: str

    def __len__(self) -> int:
        return self.end - self.begin + 1


class SuggestionSet(BaseModel):
    namespace_type: str
    namespace_id: int
    sentences: List[SentenceSpan]
    sections: List[SectionSpan]
    abstractor_suggestions: List[Suggestion]


########################################################################################################################
class ProcessTextResponse(BaseModel):
    sentences: List[SentenceSpan]
    sections: List[SectionSpan]
    suggestions: List[Suggestion]
