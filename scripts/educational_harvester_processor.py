import json
import re

def standardize_modality(modality):
    if not modality:
        return "Presencial"
    modality = modality.lower()
    if any(word in modality for word in ["distancia", "online", "remoto", "virtual"]):
        return "Remoto"
    if any(word in modality for word in ["semipresencial", "hibrido", "híbrido", "blended"]):
        return "Híbrido"
    return "Presencial"

def infer_category(name):
    name = name.upper()
    if "MAESTRÍA" in name or "MAESTRIA" in name or "MASTER" in name:
        return "Maestría"
    if "DOCTORADO" in name:
        return "Doctorado"
    if "MBA" in name:
        return "Maestría"
    if "DIPLOMADO" in name:
        return "Diplomado"
    if "PROGRAMA" in name or "CURSO" in name:
        return "Curso"
    return "Otros"

def process_data():
    raw_file = r"C:\xampp\htdocs\yachachiy_ai\scripts\scraped_courses_2026_v3.json"
    try:
        with open(raw_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {raw_file}")
        return

    processed_courses = []

    for entry in raw_data:
        institution = entry.get("institution", "Unknown")
        text = entry.get("extracted_text", "")
        url_base = entry.get("url", "")

        # Logic for PUCP
        if institution == "PUCP":
            # Pattern: Maestría en\n[Name]\n Inicio: [Date]\n Modalidad: [Modality]\n Área: [Area]
            pucp_matches = re.finditer(r"Maestría en\n(.*?)\n Inicio: (.*?)\n Modalidad: (.*?)\n Área: (.*?)", text)
            for m in pucp_matches:
                name = f"Maestría en {m.group(1).strip()}"
                start_date = m.group(2).strip()
                modality = m.group(3).strip()
                
                if "2026" in start_date:
                    course = {
                        "nombre": name,
                        "institucion": institution,
                        "modalidad": standardize_modality(modality),
                        "sede": "Lima (San Miguel)",
                        "inversion": 0.0, # Not found in text
                        "descripcion": f"Programa de {name} en el área de {m.group(4).strip()}.",
                        "tiempo": "24 meses (Estimado)", # Default for master
                        "publico": "Profesionales y Bachilleres",
                        "temario": url_base,
                        "url": url_base,
                        "category": infer_category(name),
                        "year": 2026
                    }
                    processed_courses.append(course)

        # Logic for ESAN
        elif institution == "ESAN":
            # Pattern for ESAN seems to be: [Name] [Modality] [Duration] [Start Date] [Year]
            # Based on: Maestría en Desarrollo Sostenible Semipresencial\nsemipresencial\n24 meses\n15 Abr\n2026
            esan_matches = re.finditer(r"(Maestría en.*?)\n(semipresencial|presencial|a distancia)\n(\d+ meses)\n(\d+ [A-Za-z]+)\n(2026)", text)
            for m in esan_matches:
                name = m.group(1).strip()
                modality = m.group(2).strip()
                duration = m.group(3).strip()
                
                course = {
                    "nombre": name,
                    "institucion": institution,
                    "modalidad": standardize_modality(modality),
                    "sede": "Lima (Surco)",
                    "inversion": 0.0,
                    "descripcion": f"Programa de {name} ofrecido por ESAN.",
                    "tiempo": duration,
                    "publico": "Ejecutivos y Profesionales",
                    "temario": url_base,
                    "url": url_base,
                    "category": infer_category(name),
                    "year": 2026
                }
                processed_courses.append(course)
                
            # Other pattern for ESAN (Renovated programs)
            esan_renovated = re.finditer(r"Maestría en (.*?) Semipresencial\nInauguración: (.*?) 2026", text)
            for m in esan_renovated:
                name = f"Maestría en {m.group(1).strip()}"
                course = {
                    "nombre": name,
                    "institucion": institution,
                    "modalidad": "Híbrido",
                    "sede": "Lima (Surco)",
                    "inversion": 0.0,
                    "descripcion": f"Programa renovado de {name} en ESAN.",
                    "tiempo": "24 meses (Estimado)",
                    "publico": "Ejecutivos y Profesionales",
                    "temario": url_base,
                    "url": url_base,
                    "category": infer_category(name),
                    "year": 2026
                }
                processed_courses.append(course)

        # Logic for UTEC
        elif institution == "UTEC":
            # Pattern: [NAME] Inicio: [Date] Modalidad: [Modality]
            utec_matches = re.finditer(r"([A-Z\s&]+) Inicio: (.*?) 2026 Modalidad: (.*?)(?:\n|$)", text)
            for m in utec_matches:
                name = m.group(1).strip()
                modality = m.group(3).strip()
                
                course = {
                    "nombre": name,
                    "institucion": institution,
                    "modalidad": standardize_modality(modality),
                    "sede": "Lima (Barranco)",
                    "inversion": 0.0,
                    "descripcion": f"Programa de {name} en UTEC.",
                    "tiempo": "N/A",
                    "publico": "Profesionales del sector tecnológico",
                    "temario": url_base,
                    "url": url_base,
                    "category": infer_category(name),
                    "year": 2026
                }
                processed_courses.append(course)

    # Dedup
    unique_courses = []
    seen_names = set()
    for c in processed_courses:
        if c["nombre"] not in seen_names:
            unique_courses.append(c)
            seen_names.add(c["nombre"])

    with open(r"C:\xampp\htdocs\yachachiy_ai\scripts\processed_courses_2026.json", 'w', encoding='utf-8') as f:
        json.dump(unique_courses, f, indent=2, ensure_ascii=False)
    
    print(f"Processed {len(unique_courses)} courses.")

if __name__ == "__main__":
    process_data()
