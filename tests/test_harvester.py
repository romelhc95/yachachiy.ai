import pytest
import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user_amauta:password_amauta@localhost:5432/amauta_db")

@pytest.fixture(scope="module")
def db_connection():
    """Fixture to provide a database connection."""
    conn = psycopg2.connect(DATABASE_URL)
    yield conn
    conn.close()

def test_no_null_prices(db_connection):
    """Verify that no courses have null prices (must be at least 0)."""
    cur = db_connection.cursor()
    cur.execute("SELECT COUNT(*) FROM courses WHERE price_pen IS NULL")
    count = cur.fetchone()[0]
    assert count == 0, f"Found {count} courses with NULL price_pen."
    cur.close()

def test_no_duplicate_courses(db_connection):
    """Verify that there are no duplicate courses for the same institution."""
    cur = db_connection.cursor()
    cur.execute("""
        SELECT institution_id, name, COUNT(*) 
        FROM courses 
        GROUP BY institution_id, name 
        HAVING COUNT(*) > 1
    """)
    duplicates = cur.fetchall()
    assert len(duplicates) == 0, f"Found duplicate courses: {duplicates}"
    cur.close()

def test_pilot_institutions_exist(db_connection):
    """Ensure UTEC and UPC are correctly seeded."""
    cur = db_connection.cursor()
    cur.execute("SELECT slug FROM institutions WHERE slug IN ('utec', 'upc')")
    slugs = [r[0] for r in cur.fetchall()]
    assert 'utec' in slugs
    assert 'upc' in slugs
    cur.close()

def test_new_institutions_exist(db_connection):
    """Ensure newly discovered institutions are correctly seeded."""
    cur = db_connection.cursor()
    new_slugs = ['upn', 'uni', 'esan', 'ulima', 'senati', 'dsrp']
    cur.execute("SELECT slug FROM institutions WHERE slug IN %s", (tuple(new_slugs),))
    found_slugs = [r[0] for r in cur.fetchall()]
    for slug in new_slugs:
        assert slug in found_slugs, f"Institution {slug} not found in database."
    cur.close()
