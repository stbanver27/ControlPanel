# app/models/subscription.py
from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=True)
    fecha_inicio = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)
    pantallas = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)

    customer = relationship("Customer", back_populates="subscriptions")
    plan = relationship("Plan")
    payments = relationship("Payment", back_populates="subscription")
