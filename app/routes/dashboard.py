# app/routes/dashboard.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from app.core.dependencies import get_db, get_current_user, get_flash
from app.models.customer import Customer
from app.models.payment import Payment
from app.models.subscription import Subscription
from app.services.subscription import calc_status

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def index(request: Request, current_user=Depends(get_current_user)):
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    return RedirectResponse("/dashboard", status_code=302)


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user:
        return RedirectResponse("/login", status_code=302)

    hoy = date.today()

    clientes_activos = db.query(Customer).filter(Customer.estado == "activo").count()
    clientes_vencidos = db.query(Customer).filter(Customer.estado == "vencido").count()

    all_subs = db.query(Subscription).all()
    proximos = [
        s for s in all_subs
        if s.fecha_vencimiento >= hoy and (s.fecha_vencimiento - hoy).days <= 3
    ]

    ventas_dia = (
        db.query(func.sum(Payment.monto))
        .filter(Payment.estado == "confirmado", func.date(Payment.fecha) == hoy)
        .scalar()
        or 0.0
    )

    inicio_mes = hoy.replace(day=1)
    ingresos_mes = (
        db.query(func.sum(Payment.monto))
        .filter(Payment.estado == "confirmado", Payment.fecha >= inicio_mes)
        .scalar()
        or 0.0
    )

    f = get_flash(request)
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "flash": f,
            "clientes_activos": clientes_activos,
            "clientes_vencidos": clientes_vencidos,
            "proximos_count": len(proximos),
            "ventas_dia": ventas_dia,
            "ingresos_mes": ingresos_mes,
            "proximos": proximos,
            "calc_status": calc_status,
            "active_page": "dashboard",
        },
    )
