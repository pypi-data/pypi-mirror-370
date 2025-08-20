from pydantic import BaseModel, Field
from typing import Any, List, Dict, Union, Optional, Literal

'ProductStatus' = 'ProductStatus'

"""User model for the application"""

"""User model for the application"""
class User(BaseModel):
    """Unique identifier"""
    id: str = Field(description='Unique identifier')
    """User's email address"""
    email: str = Field(description='User's email address')
    """User's display name"""
    name: str = Field(description='User's display name')
    """User's age"""
    age: int = Field(description='User's age')
    """Optional phone number"""
    phone: Optional[str] = Field(default=None, description='Optional phone number')
    """User tags"""
    tags: List[str] = Field(description='User tags')
    """User settings"""
    settings: Dict[str, Any] = Field(description='User settings')

    class Config:
        extra = 'forbid'

"""Product status enum"""

ProductStatus = Union[Literal['draft'], Literal['published'], Literal['out-of-stock']]

"""Product model"""

"""Product model"""
class Product(BaseModel):
    id: str
    name: str
    price: float
    status: 'ProductStatus'
    categories: List[str]

    class Config:
        extra = 'forbid'
