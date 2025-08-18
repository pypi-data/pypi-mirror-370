import os
from unittest import TestCase

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

import models
from database import get_db
from src.api import app

postgres = PostgresContainer("postgres:17-alpine").start()

client = TestClient(app)

# Set up the in-memory SQLite database for testing
DATABASE_URL = postgres.get_connection_url(driver="psycopg")
os.environ["DATABASE_URL"] = DATABASE_URL
engine = create_engine(DATABASE_URL)
invalid_engine = create_engine(
    "postgresql+psycopg://postgres:postgres@postgres:5432/postgres2"
)
models.Base.metadata.create_all(bind=engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
InvalidSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=invalid_engine
)


# Dependency to override the get_db dependency in the main app
def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()


def override_invalid_db():
    database = InvalidSessionLocal()
    yield database
    database.close()


app.dependency_overrides[get_db] = override_get_db


class TestHealthCheck(TestCase):
    def test_health_check(self):
        response = client.get("/health-check")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
