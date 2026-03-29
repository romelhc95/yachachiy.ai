import os
from dotenv import load_dotenv

print("--- ENV VARS BEFORE load_dotenv ---")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")

load_dotenv(override=True)

print("--- ENV VARS AFTER load_dotenv(override=True) ---")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")

with open(".env", "r") as f:
    print("--- .env FILE CONTENT ---")
    print(f.read())
