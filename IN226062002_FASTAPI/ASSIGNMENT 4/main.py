from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

cart = []
orders = []

class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)

def find_product(product_id: int):
    return next((p for p in products if p["id"] == product_id), None)

def calculate_item_subtotal(price: int, quantity: int) -> int:
    """Formula: $$subtotal = unit\_price \times quantity$$"""
    return price * quantity


@app.get("/cart")
def view_cart():
    """Returns the current state of the cart (Q2)"""
    if not cart:
        return {"message": "Cart is empty", "items": [], "item_count": 0, "grand_total": 0}
    
    grand_total = sum(item["subtotal"] for item in cart)
    
    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = Query(1, gt=0)):
    """Adds or updates items in the cart (Q1, Q3, Q4)"""
    product = find_product(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if not product["in_stock"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"{product['name']} is out of stock"
        )
    
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = calculate_item_subtotal(product["price"], item["quantity"])
            return {"message": "Cart updated", "cart_item": item}
    
    new_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": calculate_item_subtotal(product["price"], quantity)
    }
    cart.append(new_item)
    return {"message": "Added to cart", "cart_item": new_item}

@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    """Removes a specific product from the cart (Q5)"""
    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": f"Removed {item['product_name']} from cart"}
    
    raise HTTPException(status_code=404, detail="Item not in cart")

@app.post("/cart/checkout")
def checkout(request: CheckoutRequest):
    """Finalizes the purchase and creates orders (Q5, Q6, Bonus)"""
    global cart
    
    if not cart:
        raise HTTPException(
            status_code=400, 
            detail="Cart is empty — add items first"
        )
    
    grand_total = sum(item["subtotal"] for item in cart)
    items_ordered = []

    for item in cart:
        order_id = len(orders) + 1
        new_order = {
            "order_id": order_id,
            "customer_name": request.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "subtotal": item["subtotal"],
            "delivery_address": request.delivery_address
        }
        orders.append(new_order)
        items_ordered.append(item["product_name"])
    
    cart = []
    
    return {
        "message": "Checkout successful",
        "order_summary": {
            "customer": request.customer_name,
            "products": items_ordered,
            "grand_total": grand_total
        }
    }

@app.get("/orders")
def get_all_orders():
    """View all historical orders (Q6)"""
    return {"orders": orders, "total_orders": len(orders)}