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
models.Base.metadata.create_all(bind=engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to override the get_db dependency in the main app
def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()


app.dependency_overrides[get_db] = override_get_db


class TestIp(TestCase):
    def test_add_ip_no_identifier(self):
        api_key = os.environ["API_KEY"]
        header = {"X-API-KEY": api_key}
        response = client.post("/ip/", params={"identifier": ""}, headers=header)
        assert response.status_code == 422
        assert response.json() == {"detail": "Missing identifier query parameter"}

    def test_add_invalid_ip(self):
        api_key = os.environ["API_KEY"]
        header = {"X-API-KEY": api_key}
        response = client.post(
            "/ip/", params={"identifier": "test", "ip": "test"}, headers=header
        )
        assert response.status_code == 422
        assert response.json() == {"detail": "Invalid IP address format"}

    def test_add_ip(self):
        api_key = os.environ["API_KEY"]
        header = {"X-API-KEY": api_key}
        ip = "1.1.1.1"
        identifier = "test"

        response = client.post(
            "/ip/", params={"identifier": identifier, "ip": ip}, headers=header
        )

        assert response.status_code == 200
        res_json: dict = response.json()
        assert "id" in res_json.keys()
        assert "ip_address" in res_json.keys()
        assert "updated_at" in res_json.keys()
        assert res_json["id"] == identifier
        assert res_json["ip_address"] == ip

    def test_add_ip_with_header(self):
        api_key = os.environ["API_KEY"]
        ip = "1.1.1.1"
        identifier = "test"
        header = {"X-API-KEY": api_key, "cf-connecting-ip": ip}

        response = client.post(
            "/ip/", params={"identifier": identifier}, headers=header
        )

        assert response.status_code == 200
        res_json: dict = response.json()
        assert "id" in res_json.keys()
        assert "ip_address" in res_json.keys()
        assert "updated_at" in res_json.keys()
        assert res_json["id"] == identifier
        assert res_json["ip_address"] == ip

    def test_get_all_ips(self):
        api_key = os.environ["API_KEY"]
        header = {"X-API-KEY": api_key}
        response = client.get("/ip/", headers=header)
        print(response.json())
        assert response.status_code == 200
        res_json: list[dict] = response.json()
        assert len(res_json) == 1
        res_json: dict = res_json[0]
        assert "id" in res_json.keys()
        assert "ip_address" in res_json.keys()
        assert "updated_at" in res_json.keys()
        assert res_json["id"] == "test"
        assert res_json["ip_address"] == "1.1.1.1"

    def test_get_ip_invalid_id(self):
        api_key = os.environ["API_KEY"]
        header = {"X-API-KEY": api_key}
        response = client.get("/ip/hello", headers=header)
        assert response.status_code == 404
        assert response.json() == {"detail": "Identifier not found"}

    def test_get_ip(self):
        api_key = os.environ["API_KEY"]
        header = {"X-API-KEY": api_key}
        response = client.get("/ip/test", headers=header)
        assert response.status_code == 200
        res_json: dict = response.json()
        assert "id" in res_json.keys()
        assert "ip_address" in res_json.keys()
        assert "updated_at" in res_json.keys()
        assert res_json["id"] == "test"
        assert res_json["ip_address"] == "1.1.1.1"
