from fastapi import FastAPI

app = FastAPI()

products = [
    {"id": 1, "name": "Notebook", "price": 150, "category": "Stationery", "in_stock": True},
    {"id": 2, "name": "Wireless Mouse", "price": 899, "category": "Electronics", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "Backpack", "price": 1599, "category": "Electronics", "in_stock": False},
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False},
]

# Q1
@app.get("/products")
def get_all_products():
    """Returns all products and the total count (Q1)"""
    return {"products": products, "total": len(products)}

# Q2
@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):
    """Filters products by category name (Case-sensitive based on your scenario)"""
    result = [p for p in products if p["category"] == category_name]
    if not result:
        return {"error": "No products found in this category"}
    return {"category": category_name, "products": result, "total": len(result)}

# Q3
@app.get("/products/instock")
def get_instock():
    """Returns only products where in_stock is True (Q3)"""
    available = [p for p in products if p["in_stock"] == True]
    return {"in_stock_products": available, "count": len(available)}

# Q4
@app.get("/store/summary")
def store_summary():
    """Returns a high-level overview of the store (Q4)"""
    in_stock_count = len([p for p in products if p["in_stock"]])
    out_stock_count = len(products) - in_stock_count
    # Set comprehension to get unique categories
    unique_categories = list({p["category"] for p in products})
    
    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock_count,
        "out_of_stock": out_stock_count,
        "categories": unique_categories,
    }

# Q5
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    """Searches product names for a keyword, case-insensitively (Q5)"""
    results = [
        p for p in products 
        if keyword.lower() in p["name"].lower()
    ]
    if not results:
        return {"message": "No products matched your search"}
    return {"keyword": keyword, "results": results, "total_matches": len(results)}

# Q6
@app.get("/products/deals")
def get_deals():
    """Returns the cheapest and most expensive products (Bonus)"""
    if not products:
        return {"error": "No products available"}
        
    cheapest = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])
    
    return {
        "best_deal": cheapest,
        "premium_pick": expensive,
    }