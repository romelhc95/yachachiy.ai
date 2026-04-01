import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import ssl

# Load environment variables
load_dotenv()

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Direct Supabase Connection (using environment variables)
DATABASE_URL = os.getenv("SUPABASE_DB_URL")

def check_leads_rls():
    global DATABASE_URL
    if not DATABASE_URL:
        print("Error: SUPABASE_DB_URL not set in .env")
        return

    # Cleanup DATABASE_URL for pg8000
    if "sslmode=" in DATABASE_URL:
        import urllib.parse
        parsed = urllib.parse.urlparse(DATABASE_URL)
        qs = urllib.parse.parse_qs(parsed.query)
        qs.pop("sslmode", None)
        new_query = urllib.parse.urlencode(qs, doseq=True)
        DATABASE_URL = parsed._replace(query=new_query).geturl()
        
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)

    print(f"Connecting to Supabase (cleaned URL)...")
    try:
        # Configuration for pg8000 + SSL if needed
        connect_args = {}
        if "pg8000" in DATABASE_URL:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connect_args["ssl_context"] = ssl_context

        engine = create_engine(DATABASE_URL, connect_args=connect_args)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("Checking if RLS is enabled on 'leads' table...")
        rls_query = text("SELECT relname, relrowsecurity FROM pg_class WHERE relname = 'leads'")
        result = session.execute(rls_query).fetchone()
        
        if result:
            print(f"Table: {result[0]}, RLS Enabled: {result[1]}")
            
            print("\nListing policies on 'leads' table...")
            policies_query = text("SELECT * FROM pg_policies WHERE tablename = 'leads'")
            policies = session.execute(policies_query).fetchall()
            
            if policies:
                for p in policies:
                    print(f"Policy: {p.policyname}, Role: {p.roles}, Command: {p.cmd}, Qual: {p.qual}")
            else:
                print("No policies found on 'leads' table.")
        else:
            print("Table 'leads' not found.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    check_leads_rls()
