# app/services/subscription.py
from datetime import date


def calc_status(fecha_vencimiento) -> str:
    if fecha_vencimiento is None:
        return "sin fecha"
    hoy = date.today()
    if hoy > fecha_vencimiento:
        return "vencida"
    diff = (fecha_vencimiento - hoy).days
    if diff <= 3:
        return "por vencer"
    return "activa"
