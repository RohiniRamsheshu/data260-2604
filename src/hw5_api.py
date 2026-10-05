from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db import get_db
from src.models import Researcher, Vulnerability
from src.schemas import (
    ResearcherCreate,
    ResearcherResponse,
    VulnerabilityCreate,
    VulnerabilityResponse,
)
router = APIRouter(
    prefix="/api",
    tags=["HW5 Researchers"]
)


@router.post(
    "/researchers",
    response_model=ResearcherResponse,
    status_code=status.HTTP_201_CREATED
)
def create_researcher(
    payload: ResearcherCreate,
    db: Session = Depends(get_db)
):
    researcher = Researcher(**payload.model_dump())

    db.add(researcher)

    try:
        db.commit()
        db.refresh(researcher)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A researcher with this email already exists"
        )

    return researcher


@router.get(
    "/researchers",
    response_model=list[ResearcherResponse]
)
def list_researchers(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return (
        db.query(Researcher)
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get(
    "/researchers/{researcher_id}",
    response_model=ResearcherResponse
)
def get_researcher(
    researcher_id: int,
    db: Session = Depends(get_db)
):
    researcher = db.get(Researcher, researcher_id)

    if researcher is None:
        raise HTTPException(
            status_code=404,
            detail="Researcher not found"
        )

    return researcher


@router.put(
    "/researchers/{researcher_id}",
    response_model=ResearcherResponse
)
def update_researcher(
    researcher_id: int,
    payload: ResearcherCreate,
    db: Session = Depends(get_db)
):
    researcher = db.get(Researcher, researcher_id)

    if researcher is None:
        raise HTTPException(
            status_code=404,
            detail="Researcher not found"
        )

    for field, value in payload.model_dump().items():
        setattr(researcher, field, value)

    try:
        db.commit()
        db.refresh(researcher)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A researcher with this email already exists"
        )

    return researcher


@router.delete("/researchers/{researcher_id}")
def delete_researcher(
    researcher_id: int,
    db: Session = Depends(get_db)
):
    researcher = db.get(Researcher, researcher_id)

    if researcher is None:
        raise HTTPException(
            status_code=404,
            detail="Researcher not found"
        )

    if researcher.vulnerabilities:
        raise HTTPException(
            status_code=409,
            detail=(
                "Cannot delete researcher while vulnerabilities "
                "are associated with it"
            )
        )

    db.delete(researcher)
    db.commit()

    return {
        "message": f"Researcher {researcher_id} deleted successfully"
    }

@router.post(
    "/vulnerabilities",
    response_model=VulnerabilityResponse,
    status_code=status.HTTP_201_CREATED
)
def create_vulnerability(
    payload: VulnerabilityCreate,
    db: Session = Depends(get_db)
):
    researcher = db.get(Researcher, payload.researcher_id)

    if researcher is None:
        raise HTTPException(
            status_code=400,
            detail="Researcher does not exist"
        )

    vulnerability = Vulnerability(**payload.model_dump())

    db.add(vulnerability)

    try:
        db.commit()
        db.refresh(vulnerability)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A vulnerability with this CVE already exists"
        )

    return vulnerability


@router.get(
    "/vulnerabilities",
    response_model=list[VulnerabilityResponse]
)
def list_vulnerabilities(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return (
        db.query(Vulnerability)
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get(
    "/vulnerabilities/{vulnerability_id}",
    response_model=VulnerabilityResponse
)
def get_vulnerability(
    vulnerability_id: int,
    db: Session = Depends(get_db)
):
    vulnerability = db.get(Vulnerability, vulnerability_id)

    if vulnerability is None:
        raise HTTPException(
            status_code=404,
            detail="Vulnerability not found"
        )

    return vulnerability


@router.put(
    "/vulnerabilities/{vulnerability_id}",
    response_model=VulnerabilityResponse
)
def update_vulnerability(
    vulnerability_id: int,
    payload: VulnerabilityCreate,
    db: Session = Depends(get_db)
):
    vulnerability = db.get(Vulnerability, vulnerability_id)

    if vulnerability is None:
        raise HTTPException(
            status_code=404,
            detail="Vulnerability not found"
        )

    researcher = db.get(Researcher, payload.researcher_id)

    if researcher is None:
        raise HTTPException(
            status_code=400,
            detail="Researcher does not exist"
        )

    for field, value in payload.model_dump().items():
        setattr(vulnerability, field, value)

    try:
        db.commit()
        db.refresh(vulnerability)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A vulnerability with this CVE already exists"
        )

    return vulnerability


@router.delete("/vulnerabilities/{vulnerability_id}")
def delete_vulnerability(
    vulnerability_id: int,
    db: Session = Depends(get_db)
):
    vulnerability = db.get(Vulnerability, vulnerability_id)

    if vulnerability is None:
        raise HTTPException(
            status_code=404,
            detail="Vulnerability not found"
        )

    db.delete(vulnerability)
    db.commit()

    return {
        "message": (
            f"Vulnerability {vulnerability_id} "
            "deleted successfully"
        )
    }
@router.get(
    "/researchers/{researcher_id}/vulnerabilities",
    response_model=list[VulnerabilityResponse]
)
def get_researcher_vulnerabilities(
    researcher_id: int,
    db: Session = Depends(get_db)
):
    researcher = db.get(Researcher, researcher_id)

    if researcher is None:
        raise HTTPException(
            status_code=404,
            detail="Researcher not found"
        )

    return (
        db.query(Vulnerability)
        .filter(
            Vulnerability.researcher_id == researcher_id
        )
        .all()
    )