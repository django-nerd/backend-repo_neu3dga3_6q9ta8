import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Katana, Order

app = FastAPI(title="Katana Store API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Katana Store Backend is running"}

@app.get("/api/katanas")
def list_katanas(q: Optional[str] = None):
    try:
        filter_query = {}
        if q:
            # Simple text search across name and steel
            filter_query = {"$or": [
                {"name": {"$regex": q, "$options": "i"}},
                {"steel": {"$regex": q, "$options": "i"}}
            ]}
        docs = get_documents("katana", filter_query)
        # Convert ObjectId to string
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/katanas")
def create_katana(payload: Katana):
    try:
        new_id = create_document("katana", payload)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CartItem(BaseModel):
    product_id: str
    quantity: int

class CheckoutPayload(BaseModel):
    customer_name: str
    customer_email: str
    address: str
    items: List[CartItem]

@app.post("/api/checkout")
def checkout(payload: CheckoutPayload):
    # Build order and persist
    try:
        # Fetch products to compute totals and validate
        ids = [ObjectId(i.product_id) for i in payload.items]
        products = list(db["katana"].find({"_id": {"$in": ids}}))
        product_map = {str(p["_id"]): p for p in products}

        order_items = []
        total = 0.0
        for item in payload.items:
            p = product_map.get(item.product_id)
            if not p:
                raise HTTPException(status_code=400, detail=f"Product not found: {item.product_id}")
            quantity = max(1, int(item.quantity))
            line_total = float(p.get("price", 0)) * quantity
            total += line_total
            order_items.append({
                "product_id": item.product_id,
                "name": p.get("name"),
                "price": float(p.get("price", 0)),
                "quantity": quantity
            })
        order_doc = {
            "customer_name": payload.customer_name,
            "customer_email": payload.customer_email,
            "address": payload.address,
            "items": order_items,
            "total": round(total, 2),
            "status": "pending"
        }
        from datetime import datetime, timezone
        order_doc['created_at'] = datetime.now(timezone.utc)
        order_doc['updated_at'] = datetime.now(timezone.utc)
        res = db["order"].insert_one(order_doc)
        return {"order_id": str(res.inserted_id), "total": order_doc["total"]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
