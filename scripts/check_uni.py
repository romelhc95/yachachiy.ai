import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set database URL for local MySQL 3307
os.environ["DATABASE_URL"] = "mysql+pymysql://root:@localhost:3307/yachachiy"

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.models import Institution, Course

engine = create_engine(os.environ["DATABASE_URL"])
Session = sessionmaker(bind=engine)
db = Session()

uni = db.query(Institution).filter(Institution.name.like('%Universidad Nacional de Ingeniería%')).first()
if uni:
    print(f"FOUND|{uni.id}|{uni.name}|{uni.website_url}|{uni.slug}")
else:
    print("NOT_FOUND")

db.close()
