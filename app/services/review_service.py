"""Business logic for submitting and reading venture peer reviews."""

from sqlalchemy.orm import Session

from app.models.review import Review


class ReviewService:
    """Provides operations for creating and reading venture reviews."""

    @staticmethod
    def get_for_venture(db: Session, venture_id: int) -> list[Review]:
        """Return all reviews for the selected venture, newest first."""
        return (
            db.query(Review)
            .filter(Review.venture_id == venture_id)
            .order_by(Review.created_at.desc())
            .all()
        )

    @staticmethod
    def submit(db: Session, venture_id: int, score: int, comment: str = "") -> Review:
        """Persist a peer review score and optional comment for a venture."""
        if not 1 <= score <= 5:
            raise ValueError(f"Score must be between 1 and 5, got {score}.")

        review = Review(
            venture_id=venture_id,
            score=score,
            comment=comment.strip(),
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        return review
