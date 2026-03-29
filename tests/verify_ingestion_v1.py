import sqlite3
from datetime import datetime

def verify_ingestion():
    conn = sqlite3.connect('yachachiy.db')
    cursor = conn.cursor()
    
    # 1. Duplicates check
    print("--- Check for duplicates ---")
    cursor.execute("SELECT name, institution_id, count(*) as count FROM courses GROUP BY name, institution_id HAVING count(*) > 1")
    duplicates_name = cursor.fetchall()
    if not duplicates_name:
        print("No duplicates found by (name, institution_id).")
    else:
        print(f"Found {len(duplicates_name)} duplicates by (name, institution_id):")
        for row in duplicates_name:
            print(f"  - {row[0]} (institution_id: {row[1]}) x{row[2]}")

    cursor.execute("SELECT url, count(*) as count FROM courses WHERE url IS NOT NULL AND url != '' GROUP BY url HAVING count(*) > 1")
    duplicates_url = cursor.fetchall()
    if not duplicates_url:
        print("No duplicates found by url.")
    else:
        print(f"Found {len(duplicates_url)} duplicates by url:")
        for row in duplicates_url:
            print(f"  - {row[0]} x{row[1]}")

    # 2. Mandatory fields check
    # name, institution_id, price_pen, mode, category, url
    print("\n--- Check mandatory fields ---")
    fields = ['name', 'institution_id', 'price_pen', 'mode', 'category', 'url']
    for field in fields:
        cursor.execute(f"SELECT count(*) FROM courses WHERE {field} IS NULL OR {field} = ''")
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"Field '{field}' has {count} empty/null records.")
        else:
            print(f"Field '{field}' is 100% complete.")

    # 3. New vs Updated
    # Assuming v1.0 ingestion was the most recent batch.
    # Let's see if we have any records where updated_at > created_at.
    print("\n--- New vs Updated records ---")
    
    cursor.execute("SELECT count(*) FROM courses")
    total = cursor.fetchone()[0]
    
    # In SQLite, if created_at and updated_at are set to the same value on insert, 
    # we can use that.
    cursor.execute("SELECT count(*) FROM courses WHERE created_at = updated_at")
    new_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT count(*) FROM courses WHERE updated_at > created_at")
    updated_count = cursor.fetchone()[0]
    
    print(f"Total records in 'courses': {total}")
    print(f"New records (created_at == updated_at): {new_count}")
    print(f"Updated records (updated_at > created_at): {updated_count}")

    conn.close()

if __name__ == "__main__":
    verify_ingestion()
