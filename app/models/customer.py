# app/models/customer.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

customer_tags = Table(
    "customer_tags",
    Base.metadata,
    Column("customer_id", Integer, ForeignKey("customers.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    whatsapp = Column(String(50))
    email = Column(String(255))
    pais = Column(String(100))
    username = Column(String(100), unique=True)
    estado = Column(String(50), default="activo")  # activo | vencido | suspendido
    notas = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    tags = relationship("Tag", secondary=customer_tags, lazy="subquery")
    subscriptions = relationship(
        "Subscription", back_populates="customer", cascade="all, delete-orphan",
        order_by="desc(Subscription.fecha_vencimiento)"
    )
    payments = relationship(
        "Payment", back_populates="customer", cascade="all, delete-orphan",
        order_by="desc(Payment.fecha)"
    )
