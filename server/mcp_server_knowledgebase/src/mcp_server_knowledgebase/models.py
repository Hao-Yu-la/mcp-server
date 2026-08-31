from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class DocFilter(BaseModel):
    """Filter applied to Viking Knowledge Base search results."""

    op: Literal["must", "must_not"]
    field: str = Field(min_length=1)
    conds: list[Any] = Field(min_length=1)


class AddDocumentResult(BaseModel):
    collection_name: str
    doc_id: str


class DocumentStatus(BaseModel):
    model_config = ConfigDict(extra="allow")

    process_status: Optional[int] = None
    failed_code: Optional[str] = None


class DocumentInfo(BaseModel):
    """Known document fields; extra upstream fields are preserved."""

    model_config = ConfigDict(extra="allow")

    collection_name: Optional[str] = None
    doc_id: Optional[str] = None
    doc_name: Optional[str] = None
    doc_type: Optional[str] = None
    url: Optional[str] = None
    add_type: Optional[str] = None
    create_time: Optional[int] = None
    update_time: Optional[int] = None
    point_num: Optional[int] = None
    status: Optional[DocumentStatus] = None


class CollectionInfoResult(BaseModel):
    collection_name: str
    description: str
    status: int


class CollectionSummary(BaseModel):
    collection_name: str
    description: str


class ListCollectionsResult(BaseModel):
    collection_list: list[CollectionSummary]


class SearchChunk(BaseModel):
    id: str
    content: str
    doc_id: Optional[str] = None
    doc_name: Optional[str] = None


class SearchKnowledgeResult(BaseModel):
    result_list: list[SearchChunk]
