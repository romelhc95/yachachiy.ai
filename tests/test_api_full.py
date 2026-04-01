import os
import time
import uuid
import pytest
import requests
from dotenv import load_dotenv

# Load configuration from .env
load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
BASE_URL = f"{SUPABASE_URL}/rest/v1" if SUPABASE_URL else None

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}" if SUPABASE_KEY else None,
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Almacenamiento de resultados para el informe
test_results = []

def record_result(name, status, duration, details=""):
    test_results.append({
        "name": name,
        "status": "PASÓ" if status else "FALLÓ",
        "duration": f"{duration:.3f}s",
        "details": details
    })

@pytest.fixture(scope="session", autouse=True)
def print_report_at_end():
    if not BASE_URL or not SUPABASE_KEY:
        pytest.skip("Supabase configuration missing in .env")
    yield
    print("\n\n" + "="*50)
    print("RESUMEN DE PRUEBAS DE API - YACHACHIY.AI")
    print("="*50)
    for res in test_results:
        print(f"[{res['status']}] {res['name']} ({res['duration']})")
        if res['details'] and res['status'] == "FALLÓ":
            print(f"   Error: {res['details']}")
    print("="*50)

def test_get_courses():
    start_time = time.time()
    try:
        response = requests.get(f"{BASE_URL}/courses?select=id,name,mode&limit=5", headers=HEADERS)
        duration = time.time() - start_time
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        record_result("GET /courses (Básico)", True, duration)
    except Exception as e:
        record_result("GET /courses (Básico)", False, time.time() - start_time, str(e))
        raise

def test_get_courses_filtered():
    start_time = time.time()
    try:
        response = requests.get(f"{BASE_URL}/courses?mode=eq.Presencial&select=id,name,mode&limit=5", headers=HEADERS)
        duration = time.time() - start_time
        assert response.status_code == 200
        data = response.json()
        for course in data:
            assert course['mode'] == 'Presencial'
        record_result("GET /courses (Filtro Modalidad)", True, duration)
    except Exception as e:
        record_result("GET /courses (Filtro Modalidad)", False, time.time() - start_time, str(e))
        raise

def test_get_courses_ordered():
    start_time = time.time()
    try:
        response = requests.get(f"{BASE_URL}/courses?order=price_pen.asc&select=id,name,price_pen&limit=5", headers=HEADERS)
        duration = time.time() - start_time
        assert response.status_code == 200
        data = response.json()
        prices = [c['price_pen'] for c in data if c['price_pen'] is not None]
        assert prices == sorted(prices)
        record_result("GET /courses (Ordenamiento)", True, duration)
    except Exception as e:
        record_result("GET /courses (Ordenamiento)", False, time.time() - start_time, str(e))
        raise

def test_get_institutions():
    start_time = time.time()
    try:
        response = requests.get(f"{BASE_URL}/institutions?select=id,name,slug&limit=5", headers=HEADERS)
        duration = time.time() - start_time
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        record_result("GET /institutions", True, duration)
    except Exception as e:
        record_result("GET /institutions", False, time.time() - start_time, str(e))
        raise

def test_post_lead_info():
    course_resp = requests.get(f"{BASE_URL}/courses?select=id&limit=1", headers=HEADERS)
    course_id = course_resp.json()[0]['id']
    
    start_time = time.time()
    try:
        payload = {
            "first_name": "Test",
            "last_name": "User Info",
            "email": "test_info@example.com",
            "whatsapp": "999888777",
            "type": "info",
            "course_id": course_id
        }
        # Usar Prefer: return=minimal para evitar que RLS bloquee el SELECT post-inserción
        headers_minimal = HEADERS.copy()
        headers_minimal["Prefer"] = "return=minimal"
        response = requests.post(f"{BASE_URL}/leads", headers=headers_minimal, json=payload)
        duration = time.time() - start_time
        if response.status_code != 201:
            print(f"DEBUG POST /leads: {response.status_code} - {response.text}")
        assert response.status_code == 201
        record_result("POST /leads (Tipo Info)", True, duration)
    except Exception as e:
        record_result("POST /leads (Tipo Info)", False, time.time() - start_time, str(e))
        raise

def test_post_lead_recommendation():
    start_time = time.time()
    try:
        payload = {
            "first_name": "Test",
            "last_name": "User Rec",
            "email": "test_rec@example.com",
            "whatsapp": "111222333",
            "type": "recommendation",
            "area_interest": "Ingeniería de Software",
            "budget": 5000,
            "modality": "Remoto"
        }
        # Usar Prefer: return=minimal para evitar que RLS bloquee el SELECT post-inserción
        headers_minimal = HEADERS.copy()
        headers_minimal["Prefer"] = "return=minimal"
        response = requests.post(f"{BASE_URL}/leads", headers=headers_minimal, json=payload)
        duration = time.time() - start_time
        if response.status_code != 201:
            print(f"DEBUG POST /leads (rec): {response.status_code} - {response.text}")
        assert response.status_code == 201
        record_result("POST /leads (Tipo Recommendation)", True, duration)
    except Exception as e:
        record_result("POST /leads (Tipo Recommendation)", False, time.time() - start_time, str(e))
        raise

def test_resilience_missing_fields():
    start_time = time.time()
    try:
        payload = {
            "last_name": "Missing First",
            "email": "fail@example.com",
            "whatsapp": "000000000",
            "type": "info"
        }
        # Usar Prefer: return=minimal para evitar que RLS bloquee el SELECT post-inserción
        headers_minimal = HEADERS.copy()
        headers_minimal["Prefer"] = "return=minimal"
        response = requests.post(f"{BASE_URL}/leads", headers=headers_minimal, json=payload)
        duration = time.time() - start_time
        # Si fallan campos obligatorios, PostgREST devuelve 400 incluso con return=minimal
        assert response.status_code in [400, 409]
        record_result("Resiliencia: Campos faltantes", True, duration)
    except Exception as e:
        record_result("Resiliencia: Campos faltantes", False, time.time() - start_time, str(e))
        raise

def test_resilience_invalid_uuid():
    start_time = time.time()
    try:
        payload = {
            "first_name": "Test",
            "last_name": "Invalid UUID",
            "email": "uuid@example.com",
            "whatsapp": "000000000",
            "type": "info",
            "course_id": "esto-no-es-un-uuid"
        }
        response = requests.post(f"{BASE_URL}/leads", headers=HEADERS, json=payload)
        duration = time.time() - start_time
        assert response.status_code == 400
        record_result("Resiliencia: UUID inválido", True, duration)
    except Exception as e:
        record_result("Resiliencia: UUID inválido", False, time.time() - start_time, str(e))
        raise

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
