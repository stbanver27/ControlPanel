# app/models/payment.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    metodo = Column(String(100), nullable=False)
    monto = Column(Float, nullable=False)
    moneda = Column(String(10), nullable=False, default="USD")
    fecha = Column(DateTime, default=datetime.utcnow)
    estado = Column(String(50), default="pendiente")  # pendiente | confirmado
    notas = Column(String(500))

    customer = relationship("Customer", back_populates="payments")
    subscription = relationship("Subscription", back_populates="payments")
