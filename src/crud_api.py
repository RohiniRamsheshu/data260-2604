"""
HW4 - CRUD endpoints for the primary domain entity (Vulnerability),
backed by MySQL via SQLAlchemy. Every route requires a valid session
(get_current_user dependency) -- unauthenticated requests get a 401.
"""

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.orm import joinedload

from src.db import get_db
from src.models import Vulnerability, User
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
