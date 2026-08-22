import pytest
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.main import app
from app.database import Base, get_db
from app.models import ContactSubmission

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
@pytest.mark.asyncio
async def test_contact_submission_duplicate_email(setup_db):
    transport = ASGITransport(app=app)
    # Mock validate_email to skip DNS checks
    with patch("app.routers.api.validate_email"):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            data = {
                "name": "Test User",
                "email": "duplicate@test.com",
                "link": "https://example.com",
                "constraint": "Time",
                "fix_attempt": "Manual",
                "performance_gap": "Large",
                "impact_bottleneck": "Revenue"
            }
            # First submission
            await ac.post("/contact", data=data)
            
            # Second submission with same email
            response = await ac.post("/contact", data=data)
    
    # Check that it returns an error (or 200 with error message as currently implemented)
    assert response.status_code == 200
    assert "Email already submitted" in response.text
