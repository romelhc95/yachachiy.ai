import os
import requests
import unicodedata
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

def clean_slug(slug):
    if not slug:
        return ""
    # Normalize NFD to separate characters from accents
    normalized = unicodedata.normalize('NFD', slug)
    # Filter out non-spacing mark (accents)
    cleaned = "".join([c for c in normalized if unicodedata.category(c) != 'Mn'])
    cleaned = cleaned.lower()
    # Replace non-alphanumeric with -
    cleaned = re.sub(r'[^a-z0-9-]', '-', cleaned)
    # Remove duplicate hyphens
    cleaned = re.sub(r'-+', '-', cleaned)
    # Trim hyphens
    cleaned = cleaned.strip('-')
    return cleaned

def test_fetch_course(slug):
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("Error: Supabase environment variables not set.")
        return False

    print(f"🔍 Buscando programa con slug: {slug}")
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
    }

    try:
        # 1. Intentamos por slug exacto
        url = f"{SUPABASE_URL}/rest/v1/courses?slug=eq.{slug}&select=*"
        response = requests.get(url, headers=headers)
        data = response.json()

        # 2. Si falla, búsqueda robusta
        if not data or len(data) == 0:
            print("⚠️ No encontrado por slug exacto, aplicando búsqueda resiliente...")
            all_url = f"{SUPABASE_URL}/rest/v1/courses?select=*"
            all_res = requests.get(all_url, headers=headers)
            all_courses = all_res.json()

            target = clean_slug(slug)
            found = None
            for c in all_courses:
                if clean_slug(c['slug']) == target:
                    found = c
                    break

            if found:
                data = [found]
                print(f"🎯 Coincidencia encontrada mediante normalización: {found['name']}")

        if data and len(data) > 0:
            print(f"✅ Programa cargado: {data[0]['name']}")
            return True
        else:
            print(f"❌ El programa '{slug}' no está disponible.")
            return False
    except Exception as e:
        print(f"Error testing fetch: {e}")
        return False

if __name__ == "__main__":
    # Test for Quimica UNI
    test_fetch_course('maestria-en-ciencias-en-quimica-uni')
