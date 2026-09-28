"""
HW4 - CRUD endpoints for the primary domain entity (Vulnerability),
backed by MySQL via SQLAlchemy. Every route requires a valid session
(get_current_user dependency) -- unauthenticated requests get a 401.
"""

from fastapi import APIRouter, Depends, HTTPException, Form, Query
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.orm import joinedload, selectinload

from src.db import get_db
from src.models import Vulnerability, Advisory, User
from src.auth_api import get_current_user

router = APIRouter()


@router.get("/api/vulnerabilities")
def list_vulnerabilities(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """GET - view all records."""
    rows = db.query(Vulnerability).all()
    return [
        {"id": v.id, "package_name": v.package_name, "cve_id": v.cve_id}
        for v in rows
    ]


@router.get("/api/vulnerabilities/naive")
def get_vulnerabilities_naive(
    limit: int = Query(10, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: DBSession = Depends(get_db),
):
    """
    Naive Endpoint: Triggers N+1 queries by accessing relationship in a loop.
    Unauthenticated to support benchmark runner script.
    """
    vulns = db.query(Vulnerability).offset(offset).limit(limit).all()
    results = []
    for vuln in vulns:
        advisories_data = [
            {"id": adv.id, "note": adv.note} 
            for adv in vuln.advisories
        ]
        results.append({
            "id": vuln.id,
            "package_name": vuln.package_name,
            "cve_id": vuln.cve_id,
            "advisories": advisories_data
        })
    return results


@router.get("/api/vulnerabilities/fixed")
def get_vulnerabilities_fixed(
    limit: int = Query(10, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: DBSession = Depends(get_db),
):
    """
    Fixed Endpoint: Prevents N+1 queries using eager loading via selectinload.
    Unauthenticated to support benchmark runner script.
    """
    vulns = (
        db.query(Vulnerability)
        .options(selectinload(Vulnerability.advisories))
        .offset(offset)
        .limit(limit)
        .all()
    )
    results = []
    for vuln in vulns:
        advisories_data = [
            {"id": adv.id, "note": adv.note} 
            for adv in vuln.advisories
        ]
        results.append({
            "id": vuln.id,
            "package_name": vuln.package_name,
            "cve_id": vuln.cve_id,
            "advisories": advisories_data
        })
    return results


@router.get("/api/vulnerabilities/{vuln_id}")
def get_vulnerability(
    vuln_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """GET - view a single record by ID."""
    v = db.query(Vulnerability).filter(Vulnerability.id == vuln_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    return {"id": v.id, "package_name": v.package_name, "cve_id": v.cve_id}


@router.post("/api/vulnerabilities")
def create_vulnerability(
    package_name: str = Form(...),
    cve_id: str = Form(...),
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """POST - add a new record."""
    v = Vulnerability(package_name=package_name, cve_id=cve_id)
    db.add(v)
    db.commit()
    db.refresh(v)
    return {"id": v.id, "package_name": v.package_name, "cve_id": v.cve_id}


@router.put("/api/vulnerabilities/{vuln_id}")
def update_vulnerability(
    vuln_id: int,
    package_name: str = Form(...),
    cve_id: str = Form(...),
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """PUT - update record details."""
    v = db.query(Vulnerability).filter(Vulnerability.id == vuln_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    v.package_name = package_name
    v.cve_id = cve_id
    db.commit()
    db.refresh(v)
    return {"id": v.id, "package_name": v.package_name, "cve_id": v.cve_id}


@router.delete("/api/vulnerabilities/{vuln_id}")
def delete_vulnerability(
    vuln_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """DELETE - remove a record."""
    v = db.query(Vulnerability).filter(Vulnerability.id == vuln_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    db.delete(v)
    db.commit()
    return {"message": f"Vulnerability {vuln_id} deleted"}