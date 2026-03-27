import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime
from decimal import Decimal
from collections import namedtuple

from api.main import app
from api.database import get_db
from api import schemas

# Namedtuple to simulate database row results
Row = namedtuple("Row", [
    "id", "institution_id", "name", "slug", "price_pen", 
    "mode", "address", "duration", "url", "last_scraped_at", 
    "created_at", "updated_at", "institution_name", 
    "location_lat", "location_long"
])

@pytest.fixture
def mock_db():
    mock = MagicMock(spec=Session)
    yield mock

@pytest.fixture
def client(mock_db):
    def override_get_db():
        try:
            yield mock_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_get_courses_integration_structure(client, mock_db):
    """
    Validates that the GET /courses endpoint returns the correct structure
    expected by the frontend, including the distance_km field.
    """
    # Mock data setup
    mock_course_id = uuid4()
    mock_inst_id = uuid4()
    now = datetime.now()
    
    mock_row = Row(
        id=mock_course_id,
        institution_id=mock_inst_id,
        name="Ciencia de Datos Aplicada",
        slug="ciencia-de-datos-aplicada",
        price_pen=Decimal("1500.00"),
        mode="Híbrido",
        address="Av. Salaverry 2020, Jesús María",
        duration="6 meses",
        url="https://example.edu.pe/curso",
        last_scraped_at=now,
        created_at=now,
        updated_at=now,
        institution_name="Universidad de Prueba",
        location_lat=Decimal("-12.0848"),
        location_long=Decimal("-77.0494")
    )

    # Mock DB query results
    mock_query = mock_db.query.return_value
    mock_join = mock_query.join.return_value
    mock_join.all.return_value = [mock_row]

    # Mock geolocation to test distance calculation
    # Client is in Miraflores, Lima
    with patch("api.utils.get_client_coordinates", return_value=(-12.1223, -77.0298)):
        response = client.get("/courses")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check that it's a list
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Validate structure of the first item
    course = data[0]
    expected_keys = {
        "id", "name", "institution_name", "price_pen", 
        "mode", "address", "duration", "url", "distance_km",
        "institution_id", "last_scraped_at", "created_at", "updated_at"
    }
    
    for key in expected_keys:
        assert key in course, f"Missing key: {key}"
    
    # Validate data types and values
    assert course["name"] == "Ciencia de Datos Aplicada"
    assert course["institution_name"] == "Universidad de Prueba"
    assert float(course["price_pen"]) == 1500.00
    assert course["mode"] == "Híbrido"
    assert isinstance(course["distance_km"], (float, int))
    assert course["distance_km"] > 0 # Should be some distance between Jesus Maria and Miraflores

    # Validate against Pydantic schema to ensure frontend compatibility
    try:
        schemas.CourseResponse(**course)
    except Exception as e:
        pytest.fail(f"Response does not match CourseResponse schema: {e}")

def test_get_courses_empty_results(client, mock_db):
    """Ensures the API handles empty results gracefully for the frontend."""
    mock_query = mock_db.query.return_value
    mock_join = mock_query.join.return_value
    mock_join.all.return_value = []

    response = client.get("/courses?name=NonExistentCourse")
    
    assert response.status_code == 200
    assert response.json() == []

def test_get_courses_no_geolocation(client, mock_db):
    """Ensures the API works even if geolocation fails (distance_km should be null)."""
    mock_row = Row(
        id=uuid4(),
        institution_id=uuid4(),
        name="Curso Sin Geo",
        slug="curso-sin-geo",
        price_pen=Decimal("0.00"),
        mode="Remoto",
        address="Virtual",
        duration="1 semana",
        url="https://virtual.edu",
        last_scraped_at=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        institution_name="Inst Virtual",
        location_lat=None,
        location_long=None
    )
    
    mock_query = mock_db.query.return_value
    mock_join = mock_query.join.return_value
    mock_join.all.return_value = [mock_row]

    with patch("api.utils.get_client_coordinates", return_value=None):
        response = client.get("/courses")
    
    assert response.status_code == 200
    data = response.json()
    assert data[0]["distance_km"] is None
