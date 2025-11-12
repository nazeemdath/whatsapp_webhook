import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Connect with SSL (required by Supabase)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ✅ Function to query products safely
def query_products_by_name(term):
    """Search for a product by name or model."""
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT id, name, model, price, stock, category
                FROM products
                WHERE LOWER(name) LIKE :q OR LOWER(model) LIKE :q
                LIMIT 10
            """)

            result = conn.execute(query, {"q": f"%{term.lower()}%"})

            # ✅ Convert rows safely across all SQLAlchemy versions
            products = []
            for row in result:
                if hasattr(row, "_mapping"):
                    products.append(dict(row._mapping))  # SQLAlchemy 2.x
                else:
                    products.append(dict(zip(result.keys(), row)))  # Fallback

            return products

    except Exception as e:
        print("❌ Database query error:", e)
        return []


# ✅ Test Supabase connection
if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW();"))
            print("✅ Supabase connection test passed! Current server time:", list(result)[0][0])

            # Optional: test query here
            print("🔍 Testing product query:", query_products_by_name("iphone"))
    except Exception as e:
        print("❌ Database connection failed:", e)
