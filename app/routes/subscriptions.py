# app/routes/subscriptions.py
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional
from app.core.dependencies import get_db, get_current_user, flash, get_flash
from app.models.customer import Customer
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.services.subscription import calc_status

router = APIRouter(prefix="/subscriptions")
templates = Jinja2Templates(directory="templates")


def _auth(current_user):
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    return None


@router.get("", response_class=HTMLResponse)
def list_subscriptions(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard
    subscriptions = (
        db.query(Subscription)
        .join(Customer)
        .order_by(Subscription.fecha_vencimiento.desc())
        .all()
    )
    f = get_flash(request)
    return templates.TemplateResponse(
        "subscriptions/list.html",
        {
            "request": request,
            "current_user": current_user,
            "subscriptions": subscriptions,
            "flash": f,
            "calc_status": calc_status,
            "active_page": "subscriptions",
        },
    )


@router.get("/create", response_class=HTMLResponse)
def create_subscription_form(
    request: Request,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard
    customers = db.query(Customer).order_by(Customer.nombre).all()
    plans = db.query(Plan).filter(Plan.activo == True).order_by(Plan.nombre).all()
    f = get_flash(request)
    return templates.TemplateResponse(
        "subscriptions/create.html",
        {
            "request": request,
            "current_user": current_user,
            "customers": customers,
            "plans": plans,
            "flash": f,
            "error": None,
            "prefill_customer_id": customer_id,
            "today": date.today().isoformat(),
            "active_page": "subscriptions",
        },
    )


@router.post("/create")
def create_subscription(
    request: Request,
    customer_id: int = Form(...),
    plan_id: str = Form(""),
    fecha_inicio: str = Form(...),
    fecha_vencimiento: str = Form(...),
    pantallas: int = Form(...),
    precio: float = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard

    customers = db.query(Customer).order_by(Customer.nombre).all()
    plans = db.query(Plan).filter(Plan.activo == True).order_by(Plan.nombre).all()

    def re_render(error):
        return templates.TemplateResponse(
            "subscriptions/create.html",
            {
                "request": request, "current_user": current_user, "customers": customers,
                "plans": plans, "error": error, "prefill_customer_id": customer_id,
                "today": date.today().isoformat(), "active_page": "subscriptions",
            },
        )

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return re_render("Cliente no encontrado.")

    try:
        f_inicio = date.fromisoformat(fecha_inicio)
        f_vencimiento = date.fromisoformat(fecha_vencimiento)
    except ValueError:
        return re_render("Fechas inválidas.")

    if f_vencimiento <= f_inicio:
        return re_render("La fecha de vencimiento debe ser posterior al inicio.")

    plan_id_int = int(plan_id) if plan_id.strip() else None
    sub = Subscription(
        customer_id=customer_id,
        plan_id=plan_id_int,
        fecha_inicio=f_inicio,
        fecha_vencimiento=f_vencimiento,
        pantallas=pantallas,
        precio=precio,
    )
    db.add(sub)
    # Update customer estado to activo on new subscription
    customer.estado = "activo"
    db.commit()
    flash(request, "success", "Suscripción creada correctamente.")
    return RedirectResponse("/subscriptions", status_code=303)


@router.get("/{sub_id}/edit", response_class=HTMLResponse)
def edit_subscription_form(
    sub_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard
    sub = db.query(Subscription).filter(Subscription.id == sub_id).first()
    if not sub:
        flash(request, "error", "Suscripción no encontrada.")
        return RedirectResponse("/subscriptions", status_code=302)
    customers = db.query(Customer).order_by(Customer.nombre).all()
    plans = db.query(Plan).order_by(Plan.nombre).all()
    return templates.TemplateResponse(
        "subscriptions/edit.html",
        {
            "request": request, "current_user": current_user, "sub": sub,
            "customers": customers, "plans": plans, "error": None, "active_page": "subscriptions",
        },
    )


@router.post("/{sub_id}/edit")
def edit_subscription(
    sub_id: int,
    request: Request,
    customer_id: int = Form(...),
    plan_id: str = Form(""),
    fecha_inicio: str = Form(...),
    fecha_vencimiento: str = Form(...),
    pantallas: int = Form(...),
    precio: float = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard
    sub = db.query(Subscription).filter(Subscription.id == sub_id).first()
    if not sub:
        flash(request, "error", "Suscripción no encontrada.")
        return RedirectResponse("/subscriptions", status_code=302)

    try:
        f_inicio = date.fromisoformat(fecha_inicio)
        f_vencimiento = date.fromisoformat(fecha_vencimiento)
    except ValueError:
        flash(request, "error", "Fechas inválidas.")
        return RedirectResponse(f"/subscriptions/{sub_id}/edit", status_code=302)

    plan_id_int = int(plan_id) if plan_id.strip() else None
    sub.customer_id = customer_id
    sub.plan_id = plan_id_int
    sub.fecha_inicio = f_inicio
    sub.fecha_vencimiento = f_vencimiento
    sub.pantallas = pantallas
    sub.precio = precio
    db.commit()
    flash(request, "success", "Suscripción actualizada.")
    return RedirectResponse("/subscriptions", status_code=303)


@router.post("/{sub_id}/delete")
def delete_subscription(
    sub_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard
    sub = db.query(Subscription).filter(Subscription.id == sub_id).first()
    if not sub:
        flash(request, "error", "Suscripción no encontrada.")
        return RedirectResponse("/subscriptions", status_code=302)
    db.delete(sub)
    db.commit()
    flash(request, "success", "Suscripción eliminada.")
    return RedirectResponse("/subscriptions", status_code=303)
