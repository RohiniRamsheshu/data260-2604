from datetime import datetime
from typing import List

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status

from src.mongo_db import vulnerability_documents
from src.mongo_schemas import (
    VulnerabilityDocumentCreate,
    VulnerabilityDocumentUpdate,
)


router = APIRouter(
    prefix="/api/documents",
    tags=["MongoDB Documents"],
)


def serialize_document(document):
    if document is None:
        return None

    return {
        "id": str(document["_id"]),
        "package_name": document["package_name"],
        "description": document.get("description"),
        "status": document["status"],
        "category": document["category"],
        "discovered_at": document["discovered_at"],
        "cve_id": document.get("cve_id"),
        "created_at": document["created_at"],
        "updated_at": document["updated_at"],
    }


def parse_id(document_id: str):
    try:
        return ObjectId(document_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid document ID",
        )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_document(payload: VulnerabilityDocumentCreate):
    now = datetime.utcnow()

    document = payload.model_dump(mode="json")
    document["created_at"] = now
    document["updated_at"] = now

    result = vulnerability_documents.insert_one(document)
    saved = vulnerability_documents.find_one({"_id": result.inserted_id})

    return serialize_document(saved)


@router.get("")
def list_documents() -> List[dict]:
    documents = vulnerability_documents.find().sort("created_at", -1)
    return [serialize_document(document) for document in documents]


@router.get("/{document_id}")
def get_document(document_id: str):
    object_id = parse_id(document_id)
    document = vulnerability_documents.find_one({"_id": object_id})

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return serialize_document(document)


@router.put("/{document_id}")
def update_document(
    document_id: str,
    payload: VulnerabilityDocumentUpdate,
):
    object_id = parse_id(document_id)
    changes = payload.model_dump(
        mode="json",
        exclude_unset=True,
    )

    if not changes:
        raise HTTPException(
            status_code=400,
            detail="At least one field is required for update",
        )

    changes["updated_at"] = datetime.utcnow()

    result = vulnerability_documents.update_one(
        {"_id": object_id},
        {"$set": changes},
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    updated = vulnerability_documents.find_one({"_id": object_id})
    return serialize_document(updated)


@router.delete("/{document_id}")
def delete_document(document_id: str):
    object_id = parse_id(document_id)

    result = vulnerability_documents.delete_one(
        {"_id": object_id}
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return {
        "message": "Document deleted successfully",
        "id": document_id,
    }