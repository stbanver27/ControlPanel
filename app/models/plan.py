# app/models/plan.py
from sqlalchemy import Column, Integer, String, Float, Boolean
from app.db.session import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=False)
    duracion_dias = Column(Integer, nullable=False)
    pantallas = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)
    activo = Column(Boolean, default=True)
