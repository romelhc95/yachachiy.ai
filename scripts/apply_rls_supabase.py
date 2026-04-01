import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import ssl

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DB_URL")

def apply_rls():
    if not DATABASE_URL:
        print("Error: SUPABASE_DB_URL not set in .env")
        return

    # Use environment variable instead of hardcoded string
    db_url = DATABASE_URL
    
    # Adapt for pg8000 if necessary
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+pg8000://", 1)
    
    # Remove sslmode from string if present for pg8000
    if "sslmode=" in db_url:
        import urllib.parse
        parsed = urllib.parse.urlparse(db_url)
        qs = urllib.parse.parse_qs(parsed.query)
        qs.pop("sslmode", None)
        new_query = urllib.parse.urlencode(qs, doseq=True)
        db_url = parsed._replace(query=new_query).geturl()

    print(f"Connecting to Supabase...")
    try:
        connect_args = {}
        if "pg8000" in db_url:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connect_args["ssl_context"] = ssl_context

        engine = create_engine(db_url, connect_args=connect_args)
        
        sql = """
        ALTER TABLE public.leads ENABLE ROW LEVEL SECURITY;
        DROP POLICY IF EXISTS "Permitir inserción pública de leads" ON public.leads;
        CREATE POLICY "Permitir inserción pública de leads" ON public.leads 
        FOR INSERT 
        TO anon 
        WITH CHECK (true);
        """
        
        with engine.connect() as conn:
            print("Applying RLS policy...")
            # Use transactional execution
            with conn.begin():
                conn.execute(text(sql))
            print("RLS policy applied successfully.")
            
    except Exception as e:
        print(f"Error applying RLS policy: {e}")

if __name__ == "__main__":
    apply_rls()
