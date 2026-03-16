from fastapi import FastAPI, Response, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

class NewProduct(BaseModel):
    name: str = Field(..., min_length=2)
    price: int = Field(..., gt=0)
    category: str = Field(..., min_length=2)
    in_stock: bool = True

def find_product(product_id: int):
    return next((p for p in products if p["id"] == product_id), None)


@app.get("/products/audit")
def product_audit():
    in_stock_list = [p for p in products if p["in_stock"]]
    out_stock_list = [p for p in products if not p["in_stock"]]
    
   
    stock_value = sum(p["price"] * 10 for p in in_stock_list)
    
   
    priciest = max(products, key=lambda p: p["price"])
    
    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_list),
        "out_of_stock_names": [p["name"] for p in out_stock_list],
        "total_stock_value": stock_value,
        "most_expensive": {"name": priciest["name"], "price": priciest["price"]}
    }

@app.put("/products/discount")
def bulk_discount(
    category: str = Query(..., description="Category to discount"),
    discount_percent: int = Query(..., ge=1, le=99, description="% off")
):
    updated_items = []
    for p in products:
        if p["category"].lower() == category.lower():
            # Apply discount and convert to int
            p["price"] = int(p["price"] * (1 - discount_percent / 100))
            updated_items.append(p)
            
    if not updated_items:
        return {"message": f"No products found in category: {category}"}
        
    return {
        "message": f"{discount_percent}% discount applied to {category}",
        "updated_count": len(updated_items),
        "updated_products": updated_items
    }

@app.get("/products")
def get_all_products():
    return {"products": products, "total": len(products)}

@app.post("/products", status_code=status.HTTP_201_CREATED)
def add_product(new_data: NewProduct, response: Response):
   
    if any(p["name"].lower() == new_data.name.lower() for p in products):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f"Product with name '{new_data.name}' already exists"}
    
    new_id = max(p["id"] for p in products) + 1 if products else 1
    
    product_dict = new_data.dict()
    product_dict["id"] = new_id
    
    products.append(product_dict)
    return {"message": "Product added", "product": product_dict}

@app.get("/products/{product_id}")
def get_single_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}
    return product

@app.put("/products/{product_id}")
def update_product(
    product_id: int, 
    response: Response,
    price: Optional[int] = Query(None, gt=0),
    in_stock: Optional[bool] = Query(None)
):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}
    
    if price is not None:
        product["price"] = price
    if in_stock is not None:
        product["in_stock"] = in_stock
        
    return {"message": "Product updated", "product": product}

@app.delete("/products/{product_id}")
def delete_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}
    
    products.remove(product)
    return {"message": f"Product '{product['name']}' deleted"}