from geopy.distance import geodesic
import httpx
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

async def get_client_coordinates(ip_address: str) -> Optional[Tuple[float, float]]:
    """
    Get (lat, long) from an IP address using ip-api.com.
    Anonymization: We use the IP provided. Security Auditor requested anonymous handling.
    Note: For production, we should probably use a geoip database.
    """
    if not ip_address or ip_address == "127.0.0.1":
        # Mocking a coordinate for Lima (Miraflores area) for local dev
        return -12.1223, -77.0298

    # Anonymize IP: mask last octet
    parts = ip_address.split(".")
    if len(parts) == 4:
        parts[-1] = "0"
        ip_address = ".".join(parts)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://ip-api.com/json/{ip_address}?fields=status,lat,lon")
            data = response.json()
            if data.get("status") == "success":
                return data["lat"], data["lon"]
    except Exception as e:
        logger.error(f"Error resolving IP {ip_address}: {e}")
    
    return None

def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    Calculate geodesic distance between two points in km.
    """
    return geodesic(point1, point2).kilometers

import unicodedata
import re

def slugify(text: str) -> str:
    """
    Normaliza un texto para usarlo como slug en URLs:
    - Elimina acentos y caracteres especiales.
    - Convierte a minúsculas.
    - Reemplaza espacios y caracteres no alfanuméricos por guiones.
    - Asegura que solo contenga [a-z0-9-].
    """
    if not text:
        return ""
    # Normalizar para descomponer caracteres acentuados
    text = unicodedata.normalize('NFKD', text)
    # Eliminar caracteres no ASCII (acentos)
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Todo a minúsculas
    text = text.lower()
    # Reemplazar cualquier cosa que no sea a-z0-9 por guiones
    text = re.sub(r'[^a-z0-9]+', '-', text)
    # Limpiar guiones duplicados y extremos
    text = re.sub(r'-+', '-', text).strip('-')
    return text
