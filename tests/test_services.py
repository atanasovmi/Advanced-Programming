"""Unit tests for the VentureCanvas service layer."""

import pytest

from app.models.venture import Sector
from app.services.review_service import ReviewService
from app.services.user_service import UserService
from app.services.venture_service import VentureService


class TestUserService:
    """Tests for user registration, authentication, and shortlists."""

    def test_register_success(self, db):
        user = UserService.register(
            db,
            username="newuser",
            email="new@example.com",
            password="pass123",
            bio="Hi!",
        )
        assert user.id is not None
        assert user.username == "newuser"
        assert user.bio == "Hi!"

    def test_register_short_username(self, db):
        with pytest.raises(ValueError, match="at least 3 characters"):
            UserService.register(db, username="ab", email="a@b.com", password="pass123")

    def test_register_short_password(self, db):
        with pytest.raises(ValueError, match="at least 6 characters"):
            UserService.register(db, username="valid", email="a@b.com", password="12345")

    def test_register_invalid_email(self, db):
        with pytest.raises(ValueError, match="valid email"):
            UserService.register(db, username="valid", email="bademail", password="pass123")

    def test_register_duplicate_username(self, db):
        UserService.register(db, username="dup", email="a@b.com", password="pass123")
        with pytest.raises(ValueError, match="already taken"):
            UserService.register(db, username="dup", email="b@c.com", password="pass123")

    def test_register_duplicate_email(self, db):
        UserService.register(db, username="user1", email="dup@x.com", password="pass123")
        with pytest.raises(ValueError, match="already exists"):
            UserService.register(db, username="user2", email="dup@x.com", password="pass123")

    def test_authenticate_success(self, db):
        UserService.register(db, username="auth", email="a@a.com", password="pass123")
        user = UserService.authenticate(db, "auth", "pass123")
        assert user is not None
        assert user.username == "auth"

    def test_authenticate_wrong_password(self, db):
        UserService.register(db, username="auth2", email="a2@a.com", password="pass123")
        assert UserService.authenticate(db, "auth2", "wrong") is None

    def test_authenticate_unknown_user(self, db):
        assert UserService.authenticate(db, "ghost", "pw") is None

    def test_get_by_id_and_username(self, db):
        user = UserService.register(db, username="finder", email="f@x.com", password="pass123")
        assert UserService.get_by_id(db, user.id) is not None
        assert UserService.get_by_username(db, "finder") is not None
        assert UserService.get_by_id(db, 9999) is None
        assert UserService.get_by_username(db, "nope") is None

    def test_update_bio(self, db):
        user = UserService.register(db, username="biouser", email="b@x.com", password="pass123")
        updated = UserService.update_bio(db, user.id, "  New bio  ")
        assert updated.bio == "New bio"

    def test_shortlist_add_and_remove(self, db):
        user = UserService.register(db, username="shortuser", email="short@x.com", password="pass123")
        venture = VentureService.create(
            db,
            title="Pilot Brief",
            description="d",
            sector=Sector.CULTURE,
            team_size=2,
            discovery_weeks=1,
            build_weeks=2,
            resource_needs=[],
            milestones=[],
        )
        assert UserService.is_shortlisted(db, user.id, venture.id) is False
        UserService.add_shortlist(db, user.id, venture.id)
        assert UserService.is_shortlisted(db, user.id, venture.id) is True
        UserService.add_shortlist(db, user.id, venture.id)
        assert UserService.is_shortlisted(db, user.id, venture.id) is True
        UserService.remove_shortlist(db, user.id, venture.id)
        assert UserService.is_shortlisted(db, user.id, venture.id) is False
        assert UserService.remove_shortlist(db, user.id, venture.id) is False


class TestVentureService:
    """Tests for venture CRUD and search."""

    def test_create_and_get(self, db):
        venture = VentureService.create(
            db,
            title="Signal Studio",
            description="Insight room",
            sector=Sector.AI_DATA,
            team_size=4,
            discovery_weeks=3,
            build_weeks=6,
            resource_needs=[{"name": "Research", "effort": 12, "unit": "hours"}],
            milestones=["Interview teams", "Prototype dashboard"],
        )
        assert venture.id is not None
        assert len(venture.resource_needs) == 1
        assert len(venture.milestones) == 2
        fetched = VentureService.get_by_id(db, venture.id)
        assert fetched.title == "Signal Studio"

    def test_create_empty_title_raises(self, db):
        with pytest.raises(ValueError, match="must not be empty"):
            VentureService.create(
                db,
                title="",
                description="d",
                sector=Sector.HEALTH,
                team_size=1,
                discovery_weeks=0,
                build_weeks=0,
                resource_needs=[],
                milestones=[],
            )

    def test_create_duplicate_title_raises(self, db):
        VentureService.create(
            db,
            title="Unique",
            description="d",
            sector=Sector.HEALTH,
            team_size=1,
            discovery_weeks=0,
            build_weeks=0,
            resource_needs=[],
            milestones=[],
        )
        with pytest.raises(ValueError, match="already exists"):
            VentureService.create(
                db,
                title="Unique",
                description="d2",
                sector=Sector.CULTURE,
                team_size=2,
                discovery_weeks=1,
                build_weeks=1,
                resource_needs=[],
                milestones=[],
            )

    def test_get_all_and_by_sector(self, db):
        VentureService.create(
            db,
            title="Learning Loop",
            description="Education venture",
            sector=Sector.EDUCATION,
            team_size=4,
            discovery_weeks=2,
            build_weeks=4,
            resource_needs=[],
            milestones=[],
        )
        VentureService.create(
            db,
            title="Green Grid",
            description="Sustainability venture",
            sector=Sector.SUSTAINABILITY,
            team_size=3,
            discovery_weeks=1,
            build_weeks=3,
            resource_needs=[],
            milestones=[],
        )
        assert len(VentureService.get_all(db)) == 2
        assert len(VentureService.get_by_sector(db, Sector.EDUCATION)) == 1
        assert len(VentureService.get_by_sector(db, Sector.AI_DATA)) == 0

    def test_search(self, db):
        VentureService.create(
            db,
            title="Banana Signal",
            description="Moist opportunity mapping",
            sector=Sector.PRODUCTIVITY,
            team_size=2,
            discovery_weeks=1,
            build_weeks=2,
            resource_needs=[],
            milestones=[],
        )
        assert len(VentureService.search(db, "banana")) == 1
        assert len(VentureService.search(db, "moist")) == 1
        assert len(VentureService.search(db, "xyz")) == 0

    def test_delete(self, db):
        venture = VentureService.create(
            db,
            title="ToDelete",
            description="d",
            sector=Sector.PRODUCTIVITY,
            team_size=1,
            discovery_weeks=0,
            build_weeks=0,
            resource_needs=[],
            milestones=[],
        )
        assert VentureService.delete(db, venture.id) is True
        assert VentureService.get_by_id(db, venture.id) is None
        assert VentureService.delete(db, venture.id) is False


class TestReviewService:
    """Tests for review submission and retrieval."""

    def make_venture(self, db):
        return VentureService.create(
            db,
            title=f"R-{id(db)}",
            description="d",
            sector=Sector.HEALTH,
            team_size=1,
            discovery_weeks=0,
            build_weeks=0,
            resource_needs=[],
            milestones=[],
        )

    def test_submit_and_get(self, db):
        venture = self.make_venture(db)
        review = ReviewService.submit(db, venture.id, score=4, comment="Great!")
        assert review.id is not None
        assert review.score == 4
        reviews = ReviewService.get_for_venture(db, venture.id)
        assert len(reviews) == 1

    def test_submit_invalid_score(self, db):
        venture = self.make_venture(db)
        with pytest.raises(ValueError, match="between 1 and 5"):
            ReviewService.submit(db, venture.id, score=0)
        with pytest.raises(ValueError, match="between 1 and 5"):
            ReviewService.submit(db, venture.id, score=6)
