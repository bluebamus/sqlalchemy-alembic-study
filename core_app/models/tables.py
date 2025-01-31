from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, 
    Numeric, Table, Index, UniqueConstraint, CheckConstraint,
    text
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
import uuid
from ..core.database import Base

# 공통 Mixin 클래스
class TimestampMixin:
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

class UUIDMixin:
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4, 
        unique=True, 
        nullable=False
    )

# 사용자 테이블
class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, server_default=func.now())
    
    # 관계 설정
    profile = relationship("Profile", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="user")
    
    __table_args__ = (
        Index('idx_user_email_is_active', 'email', 'is_active'),
        {'comment': '사용자 테이블'}
    )

# 프로필 테이블 (1:1)
class Profile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "profiles"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    address = Column(String(255))
    birth_date = Column(DateTime)
    
    user = relationship("User", back_populates="profile")
    
    __table_args__ = (
        Index('idx_profile_name', 'name'),
        {'comment': '사용자 프로필 테이블'}
    )

# 상품 테이블
class Product(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "products"
    
    name = Column(String(200), nullable=False)
    description = Column(String(1000))
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String(100), nullable=False)
    product_metadata = Column(JSONB)  # 추가 상품 정보
    is_available = Column(Boolean, default=True)
    
    # 관계 설정
    inventory = relationship("Inventory", back_populates="product", uselist=False)
    order_items = relationship("OrderItem", back_populates="product")
    
    __table_args__ = (
        Index('idx_product_category_price', 'category', 'price'),
        Index('idx_product_name', 'name'),
        CheckConstraint('price >= 0', name='check_positive_price'),
        {'comment': '상품 테이블'}
    )

# 재고 테이블 (1:1)
class Inventory(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "inventories"
    
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), unique=True)
    quantity = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, default=10)
    last_restock_date = Column(DateTime, server_default=func.now())
    
    product = relationship("Product", back_populates="inventory")
    
    __table_args__ = (
        CheckConstraint('quantity >= 0', name='check_positive_quantity'),
        Index('idx_inventory_low_stock', 'quantity', 'low_stock_threshold'),
        {'comment': '재고 테이블'}
    )

# 주문 테이블
class Order(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "orders"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), nullable=False, default='pending')
    payment_status = Column(String(50), nullable=False, default='pending')
    shipping_address = Column(String(255))
    tracking_number = Column(String(100))
    
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    
    __table_args__ = (
        Index('idx_order_user_status', 'user_id', 'status'),
        Index('idx_order_payment_status', 'payment_status'),
        CheckConstraint('total_amount >= 0', name='check_positive_total'),
        {'comment': '주문 테이블'}
    )

# 주문 상품 테이블 (N:M)
class OrderItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "order_items"
    
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'))
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='SET NULL'))
    quantity = Column(Integer, nullable=False)
    price_at_time = Column(Numeric(10, 2), nullable=False)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    
    __table_args__ = (
        Index('idx_order_item_order', 'order_id'),
        Index('idx_order_item_product', 'product_id'),
        CheckConstraint('quantity > 0', name='check_positive_quantity'),
        CheckConstraint('price_at_time >= 0', name='check_positive_price'),
        {'comment': '주문 상품 테이블'}
    )
