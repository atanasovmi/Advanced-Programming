"""Unit tests for the VentureCanvas ORM model classes."""

from app.models.milestone import Milestone
from app.models.resource_need import ResourceNeed
from app.models.review import Review
from app.models.shortlist import Shortlist
from app.models.user import User
from app.models.venture import Sector, Venture


class TestUserModel:
    """Tests for the User model."""

    def test_hash_and_verify_password(self):
        hashed = User.hash_password("secret123")
        assert User.verify_password(hashed, "secret123") is True

    def test_verify_wrong_password(self):
        hashed = User.hash_password("secret123")
        assert User.verify_password(hashed, "wrong") is False

    def test_verify_malformed_hash(self):
        assert User.verify_password("nocolon", "pw") is False
        assert User.verify_password("", "pw") is False
        assert User.verify_password(None, "pw") is False

    def test_user_repr(self, db):
        user = User(username="tester", email="t@x.com", password_hash=User.hash_password("pw1234"))
        db.add(user)
        db.commit()
        assert "tester" in repr(user)

    def test_user_default_bio(self, db):
        user = User(username="u1", email="u1@x.com", password_hash=User.hash_password("pw1234"))
        db.add(user)
        db.commit()
        assert user.bio == ""


class TestVentureModel:
    """Tests for the Venture model."""

    def test_timeline_weeks(self, db):
        venture = Venture(title="Test", discovery_weeks=3, build_weeks=5, sector=Sector.PRODUCTIVITY)
        db.add(venture)
        db.commit()
        assert venture.timeline_weeks == 8

    def test_average_score_no_reviews(self, db):
        venture = Venture(title="Empty", sector=Sector.EDUCATION)
        db.add(venture)
        db.commit()
        assert venture.average_score == 0.0

    def test_average_score_with_reviews(self, db):
        venture = Venture(title="Rated", sector=Sector.AI_DATA)
        db.add(venture)
        db.flush()
        db.add_all([
            Review(venture_id=venture.id, score=4),
            Review(venture_id=venture.id, score=2),
        ])
        db.commit()
        db.refresh(venture)
        assert venture.average_score == 3.0

    def test_sector_enum_values(self):
        expected = {
            "AI & Data",
            "Sustainability",
            "Health",
            "Education",
            "Culture",
            "Productivity",
        }
        actual = {sector.value for sector in Sector}
        assert actual == expected


class TestResourceNeedModel:
    """Tests for the ResourceNeed model."""

    def test_resource_need_defaults(self, db):
        venture = Venture(title="R", sector=Sector.HEALTH)
        db.add(venture)
        db.flush()
        need = ResourceNeed(venture_id=venture.id, name="Interviews")
        db.add(need)
        db.commit()
        assert need.effort == 0.0
        assert need.unit == ""


class TestShortlistModel:
    """Tests for the Shortlist model."""

    def test_unique_constraint(self, db):
        import sqlalchemy

        user = User(username="shorty", email="short@x.com", password_hash=User.hash_password("pw1234"))
        db.add(user)
        db.flush()
        venture = Venture(title="Brief", sector=Sector.CULTURE, user_id=user.id)
        db.add(venture)
        db.flush()
        db.add(Shortlist(user_id=user.id, venture_id=venture.id))
        db.commit()
        db.add(Shortlist(user_id=user.id, venture_id=venture.id))
        try:
            db.commit()
            assert False, "Expected IntegrityError"
        except sqlalchemy.exc.IntegrityError:
            db.rollback()
