from fastapi import FastAPI, Query, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()

# --- DATA ---
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

orders = [] # This would be populated by your POST /cart/checkout from Day 5

# --- DAY 6: NEW ENDPOINTS (Placed above GET /products/{product_id}) ---

# Q4: Search Orders by Customer Name
@app.get("/orders/search")
def search_orders(customer_name: str = Query(..., description="Name to search for")):
    results = [
        o for o in orders 
        if customer_name.lower() in o["customer_name"].lower()
    ]
    if not results:
        return {"message": f"No orders found for: {customer_name}"}
    return {
        "customer_name": customer_name,
        "total_found": len(results),
        "orders": results
    }

# Q5: Grouped Sorting (Category then Price)
@app.get("/products/sort-by-category")
def sort_by_category():
    # Uses a tuple as a key: Sort by category (A-Z), then by price (Low-High)
    result = sorted(products, key=lambda p: (p["category"], p["price"]))
    return {"products": result, "total": len(result)}

# Q6: The "Master" Endpoint (Search + Sort + Paginate)
@app.get("/products/browse")
def browse_products(
    keyword: Optional[str] = Query(None),
    sort_by: str = Query("price", regex="^(price|name)$"),
    order: str = Query("asc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1, le=20),
):
    # Step 1: Filter (Search)
    result = products
    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]

    # Step 2: Sort
    reverse_order = (order == "desc")
    result = sorted(result, key=lambda p: p[sort_by], reverse=reverse_order)

    # Step 3: Paginate
    total_found = len(result)
    # Start Index Formula: $$start = (page - 1) \times limit$$
    start = (page - 1) * limit
    paged_result = result[start : start + limit]

    # Total Pages Formula: $$\lceil \frac{total}{limit} \rceil$$
    total_pages = -(-total_found // limit)

    return {
        "filters": {"keyword": keyword, "sort_by": sort_by, "order": order},
        "pagination": {
            "page": page,
            "limit": limit,
            "total_found": total_found,
            "total_pages": total_pages
        },
        "products": paged_result
    }

# BONUS: Paginated Orders
@app.get("/orders/page")
def get_orders_paged(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=20),
):
    start = (page - 1) * limit
    total_orders = len(orders)
    return {
        "page": page,
        "limit": limit,
        "total": total_orders,
        "total_pages": -(-total_orders // limit),
        "orders": orders[start : start + limit]
    }

# --- EXISTING BASE ENDPOINTS ---

@app.get("/products/search")
def product_search(keyword: str):
    results = [p for p in products if keyword.lower() in p["name"].lower()]
    if not results:
        return {"message": f"No products found for: {keyword}"}
    return {"results": results, "total_found": len(results)}

@app.get("/products/sort")
def sort_products(sort_by: str = "price", order: str = "asc"):
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}
    
    is_desc = (order == "desc")
    result = sorted(products, key=lambda p: p[sort_by], reverse=is_desc)
    return {"sort_by": sort_by, "order": order, "products": result}

@app.get("/products/page")
def paginate_products(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    total_pages = -(-len(products) // limit)
    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "products": products[start : start + limit]
    }

@app.get("/products/{product_id}")
def get_product(product_id: int):
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product