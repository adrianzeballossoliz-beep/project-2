"""
models.py
Modelos SQLAlchemy ORM mapeados al schema 'superstore' de PostgreSQL.
Cada clase refleja exactamente una tabla del modelo relacional.
"""

from sqlalchemy import (
    Column, Integer, String, Numeric, Date, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from database import Base


# ─────────────────────────────────────────────────────────────
# 1. Segment  →  tabla: segments
# ─────────────────────────────────────────────────────────────
class Segment(Base):
    __tablename__ = "segments"

    segment_id   = Column(Integer, primary_key=True, autoincrement=True)
    segment_name = Column(String(100), nullable=False, unique=True)

    # Relación inversa
    customers = relationship("Customer", back_populates="segment")

    def __repr__(self):
        return f"<Segment {self.segment_name}>"


# ─────────────────────────────────────────────────────────────
# 2. Customer  →  tabla: customers
# ─────────────────────────────────────────────────────────────
class Customer(Base):
    __tablename__ = "customers"

    customer_id   = Column(String(30), primary_key=True)
    customer_name = Column(String(200), nullable=False)
    segment_id    = Column(Integer, ForeignKey("segments.segment_id"), nullable=False)

    # Relaciones
    segment = relationship("Segment", back_populates="customers")
    orders  = relationship("Order",   back_populates="customer")

    def __repr__(self):
        return f"<Customer {self.customer_name}>"


# ─────────────────────────────────────────────────────────────
# 3. ShipMode  →  tabla: ship_modes
# ─────────────────────────────────────────────────────────────
class ShipMode(Base):
    __tablename__ = "ship_modes"

    ship_mode_id   = Column(Integer, primary_key=True, autoincrement=True)
    ship_mode_name = Column(String(100), nullable=False, unique=True)

    # Relación inversa
    orders = relationship("Order", back_populates="ship_mode")

    def __repr__(self):
        return f"<ShipMode {self.ship_mode_name}>"


# ─────────────────────────────────────────────────────────────
# 4. Location  →  tabla: locations
# ─────────────────────────────────────────────────────────────
class Location(Base):
    __tablename__ = "locations"

    location_id = Column(Integer, primary_key=True, autoincrement=True)
    country     = Column(String(100))
    city        = Column(String(120))
    state       = Column(String(120))
    postal_code = Column(String(20))
    region      = Column(String(80))

    # Relación inversa
    orders = relationship("Order", back_populates="location")

    def __repr__(self):
        return f"<Location {self.city}, {self.region}>"


# ─────────────────────────────────────────────────────────────
# 5. Category  →  tabla: categories
# ─────────────────────────────────────────────────────────────
class Category(Base):
    __tablename__ = "categories"

    category_id   = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(120), nullable=False, unique=True)

    # Relación inversa
    subcategories = relationship("SubCategory", back_populates="category")

    def __repr__(self):
        return f"<Category {self.category_name}>"


# ─────────────────────────────────────────────────────────────
# 6. SubCategory  →  tabla: subcategories
# ─────────────────────────────────────────────────────────────
class SubCategory(Base):
    __tablename__ = "subcategories"

    subcategory_id   = Column(Integer, primary_key=True, autoincrement=True)
    subcategory_name = Column(String(120), nullable=False)
    category_id      = Column(Integer, ForeignKey("categories.category_id"), nullable=False)

    # Relaciones
    category = relationship("Category", back_populates="subcategories")
    products = relationship("Product",  back_populates="subcategory")

    def __repr__(self):
        return f"<SubCategory {self.subcategory_name}>"


# ─────────────────────────────────────────────────────────────
# 7. Product  →  tabla: products
# ─────────────────────────────────────────────────────────────
class Product(Base):
    __tablename__ = "products"

    product_pk    = Column(Integer, primary_key=True, autoincrement=True)
    product_code  = Column(String(60), nullable=False)
    product_name  = Column(Text, nullable=False)
    subcategory_id = Column(Integer, ForeignKey("subcategories.subcategory_id"), nullable=False)

    # Relaciones
    subcategory   = relationship("SubCategory", back_populates="products")
    order_details = relationship("OrderDetail", back_populates="product")

    def __repr__(self):
        return f"<Product {self.product_code}>"


# ─────────────────────────────────────────────────────────────
# 8. Order  →  tabla: orders
# ─────────────────────────────────────────────────────────────
class Order(Base):
    __tablename__ = "orders"

    order_id     = Column(String(50), primary_key=True)
    order_date   = Column(Date, nullable=False)
    ship_date    = Column(Date)
    customer_id  = Column(String(30), ForeignKey("customers.customer_id"), nullable=False)
    ship_mode_id = Column(Integer,    ForeignKey("ship_modes.ship_mode_id"), nullable=False)
    location_id  = Column(Integer,    ForeignKey("locations.location_id"),  nullable=False)

    # Relaciones
    customer     = relationship("Customer",    back_populates="orders")
    ship_mode    = relationship("ShipMode",    back_populates="orders")
    location     = relationship("Location",    back_populates="orders")
    order_details = relationship("OrderDetail", back_populates="order")

    def __repr__(self):
        return f"<Order {self.order_id}>"


# ─────────────────────────────────────────────────────────────
# 9. OrderDetail  →  tabla: order_details
# ─────────────────────────────────────────────────────────────
class OrderDetail(Base):
    __tablename__ = "order_details"

    order_detail_id = Column(Integer, primary_key=True, autoincrement=True)
    row_id          = Column(Integer, nullable=False, unique=True)
    order_id        = Column(String(50), ForeignKey("orders.order_id"),    nullable=False)
    product_pk      = Column(Integer,    ForeignKey("products.product_pk"), nullable=False)
    sales           = Column(Numeric(14, 4), nullable=False)
    quantity        = Column(Integer,        nullable=False)
    discount        = Column(Numeric(8, 4),  nullable=False)
    profit          = Column(Numeric(14, 4), nullable=False)

    # Relaciones
    order   = relationship("Order",   back_populates="order_details")
    product = relationship("Product", back_populates="order_details")

    def __repr__(self):
        return f"<OrderDetail order={self.order_id} product={self.product_pk}>"