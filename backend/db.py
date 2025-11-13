# backend/db.py
import os
import requests
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")        # e.g. https://yourproject.supabase.co
SUPABASE_KEY = os.getenv("SUPABASE_KEY")        # anon/public key (or service key for server)
SUPABASE_TIMEOUT = 10                           # seconds

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing SUPABASE_URL or SUPABASE_KEY in environment variables")


def _build_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def query_products_by_name(term, limit: int = 10):
    """
    Query Supabase 'products' table using REST API.
    Matches name, model or sku (case-insensitive).
    Returns a list of product dicts (may be empty).
    """
    try:
        if not term:
            return []

        term = str(term).strip()
        # escape percent, spaces etc. quote_plus will help in URL params if required
        # Build an 'or' filter: (name.ilike.%term%,model.ilike.%term%,sku.ilike.%term%)
        # Supabase REST expects filters supplied either as params or in the URL.
        # We'll build the 'or' param manually.
        escaped = quote_plus(term)  # for safety inside param values (not strictly necessary for ilike)
        ilike_part = f"%{term}%"

        # The 'or' param must be URL encoded in requests automatically when provided in params dict.
        or_filter = f"(name.ilike.%{term}%,model.ilike.%{term}%,sku.ilike.%{term}%)"

        url = f"{SUPABASE_URL}/rest/v1/products"
        params = {
            "select": "id,name,model,sku,price,stock,category,description",
            "or": or_filter,
            "limit": str(limit)
        }

        resp = requests.get(url, headers=_build_headers(), params=params, timeout=SUPABASE_TIMEOUT)

        if resp.status_code == 200:
            products = resp.json()
            # optional: normalize numeric fields
            for p in products:
                # convert price to float if string
                if "price" in p and p["price"] is not None:
                    try:
                        p["price"] = float(p["price"])
                    except Exception:
                        pass
                if "stock" in p and p["stock"] is not None:
                    try:
                        p["stock"] = int(p["stock"])
                    except Exception:
                        pass
            # debug log
            print(f"🔍 Supabase returned {len(products)} products for term='{term}'")
            return products
        else:
            print("❌ Supabase REST API error:", resp.status_code, resp.text)
            return []

    except requests.RequestException as e:
        print("❌ Network error contacting Supabase REST API:", e)
        return []
    except Exception as e:
        print("❌ Exception during Supabase REST query:", e)
        return []
