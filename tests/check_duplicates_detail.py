import sqlite3

def check_duplicates_detail():
    conn = sqlite3.connect('yachachiy.db')
    cursor = conn.cursor()
    
    urls = [
        "https://posgrado.pucp.edu.pe/programas/maestrias/",
        "https://posgrado.utec.edu.pe/cursos-y-programas",
        "https://www.esan.edu.pe/maestrias/"
    ]
    
    for url in urls:
        print(f"\n--- URL: {url} ---")
        cursor.execute("SELECT name, institution_id, price_pen FROM courses WHERE url = ?", (url,))
        rows = cursor.fetchall()
        for row in rows:
            print(f"  Name: {row[0]}, InstID: {row[1]}, Price: {row[2]}")

    print("\n--- Records with NULL/Empty URL ---")
    cursor.execute("SELECT name, institution_id, url FROM courses WHERE url IS NULL OR url = ''")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  Name: {row[0]}, InstID: {row[1]}, URL: {row[2]}")

    conn.close()

if __name__ == "__main__":
    check_duplicates_detail()
