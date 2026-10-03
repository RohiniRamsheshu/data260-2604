"""
HW4 - SQLAlchemy models.

Domain entity: Vulnerability (primary field = package_name, secondary
field = cve_id) -- matches DOMAIN_ID=4 (open-source package vulnerabilities).

Auth tables: User, Session -- session token stored server-side, referenced
only by an opaque token in the browser's cookie.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from src.db import Base


class Vulnerability(Base):
    """Primary domain entity."""
    __tablename__ = "vulnerabilities"

    id = Column(Integer, primary_key=True, autoincrement=True)

    package_name = Column(
        String(255),
        nullable=False
    )

    cve_id = Column(
        String(50),
        nullable=False,
        unique=True
    )

    severity = Column(
        Integer,
        nullable=False,
        default=0
    )

    researcher_id = Column(
        Integer,
        ForeignKey("researchers.id", ondelete="RESTRICT"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    researcher = relationship(
        "Researcher",
        back_populates="vulnerabilities"
    )

    advisories = relationship(
        "Advisory",
        back_populates="vulnerability"
    )

class Researcher(Base):
    """Related entity for HW5."""

    __tablename__ = "researchers"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    first_name = Column(
        String(100),
        nullable=False
    )

    last_name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        nullable=False,
        unique=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    vulnerabilities = relationship(
        "Vulnerability",
        back_populates="researcher"
    )

class Advisory(Base):
    """
    Related table used for the N+1 demonstration in Part 3.
    Just test data for now -- a full CRUD-able related entity comes later.
    """
    __tablename__ = "advisories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vulnerability_id = Column(Integer, ForeignKey("vulnerabilities.id"), nullable=False)
    note = Column(String(500), nullable=False)

    vulnerability = relationship("Vulnerability", back_populates="advisories")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    sessions = relationship("Session", back_populates="user")


class Session(Base):
    """
    Server-side session record. The session token (id) is what the
    browser's HTTP-only cookie stores -- no user data lives in the cookie
    itself, only this opaque reference.
    """
    __tablename__ = "sessions"

    id = Column(String(64), primary_key=True)  # the opaque session token
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="sessions")