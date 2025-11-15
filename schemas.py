"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Katana-specific product schema
class Katana(BaseModel):
    """
    Katana products collection schema
    Collection name: "katana"
    """
    name: str = Field(..., description="Katana name")
    description: Optional[str] = Field(None, description="Detailed description")
    steel: Optional[str] = Field(None, description="Blade steel type")
    blade_length_cm: Optional[float] = Field(None, ge=0, description="Blade length in cm")
    price: float = Field(..., ge=0, description="Price in USD")
    stock: int = Field(0, ge=0, description="Units in stock")
    rating: Optional[float] = Field(4.5, ge=0, le=5)
    images: Optional[List[str]] = Field(default_factory=list, description="Image URLs")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="ID of the katana product")
    name: str
    price: float
    quantity: int = Field(..., ge=1)

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    customer_name: str
    customer_email: str
    address: str
    items: List[OrderItem]
    total: float = Field(..., ge=0)
    status: str = Field("pending", description="Order status")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
