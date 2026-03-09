"""Business logic for venture brief creation, retrieval, search, and deletion."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.milestone import Milestone
from app.models.resource_need import ResourceNeed
from app.models.venture import Sector, Venture


class VentureService:
    """Provides CRUD-style operations for venture briefs."""

    @staticmethod
    def get_all(db: Session) -> list[Venture]:
        """Return all venture briefs ordered by creation date descending."""
        return db.query(Venture).order_by(Venture.created_at.desc()).all()

    @staticmethod
    def get_by_id(db: Session, venture_id: int) -> Optional[Venture]:
        """Return the venture with the given primary key, or None."""
        return db.query(Venture).filter(Venture.id == venture_id).first()

    @staticmethod
    def get_by_sector(db: Session, sector: Sector) -> list[Venture]:
        """Return all venture briefs in the selected sector."""
        return (
            db.query(Venture)
            .filter(Venture.sector == sector)
            .order_by(Venture.created_at.desc())
            .all()
        )

    @staticmethod
    def search(db: Session, query: str) -> list[Venture]:
        """Search venture titles and descriptions with a case-insensitive match."""
        like_pattern = f"%{query.lower()}%"
        return (
            db.query(Venture)
            .filter(Venture.title.ilike(like_pattern) | Venture.description.ilike(like_pattern))
            .order_by(Venture.created_at.desc())
            .all()
        )

    @staticmethod
    def create(
        db: Session,
        title: str,
        description: str,
        sector: Sector,
        team_size: int,
        discovery_weeks: int,
        build_weeks: int,
        resource_needs: list[dict],
        milestones: list[str],
        user_id: Optional[int] = None,
    ) -> Venture:
        """Persist a new venture brief with its capability needs and roadmap."""
        title = title.strip()
        if not title:
            raise ValueError("Venture title must not be empty.")
        if db.query(Venture).filter(Venture.title == title).first():
            raise ValueError(f"A venture named '{title}' already exists.")

        venture = Venture(
            title=title,
            description=description.strip(),
            sector=sector,
            team_size=max(1, int(team_size or 1)),
            discovery_weeks=max(0, int(discovery_weeks or 0)),
            build_weeks=max(0, int(build_weeks or 0)),
            user_id=user_id,
        )
        db.add(venture)
        db.flush()

        for item in resource_needs:
            name = (item.get("name") or "").strip()
            if not name:
                continue
            db.add(
                ResourceNeed(
                    venture_id=venture.id,
                    name=name,
                    effort=float(item.get("effort", 0) or 0),
                    unit=(item.get("unit") or "").strip(),
                )
            )

        for idx, text in enumerate(milestones, start=1):
            clean = text.strip()
            if not clean:
                continue
            db.add(Milestone(venture_id=venture.id, number=idx, description=clean))

        db.commit()
        db.refresh(venture)
        return venture

    @staticmethod
    def delete(db: Session, venture_id: int) -> bool:
        """Delete a venture brief and its dependent data."""
        venture = db.query(Venture).filter(Venture.id == venture_id).first()
        if venture is None:
            return False
        db.delete(venture)
        db.commit()
        return True
