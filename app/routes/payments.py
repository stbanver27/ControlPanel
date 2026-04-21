# app/routes/payments.py
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.core.dependencies import get_db, get_current_user, flash, get_flash
from app.models.customer import Customer
from app.models.subscription import Subscription
from app.models.payment import Payment

router = APIRouter(prefix="/payments")
templates = Jinja2Templates(directory="templates")

METODOS = ["Binance", "PayPal", "Transferencia bancaria", "Efectivo", "Otro"]
MONEDAS = ["USD", "EUR", "BS", "COP", "MXN"]


def _auth(current_user):
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    return None


@router.get("", response_class=HTMLResponse)
def list_payments(
    request: Request,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard
    query = db.query(Payment)
    if customer_id:
        query = query.filter(Payment.customer_id == customer_id)
    payments = query.order_by(Payment.fecha.desc()).all()
    customers = db.query(Customer).order_by(Customer.nombre).all()
    f = get_flash(request)
    return templates.TemplateResponse(
        "payments/list.html",
        {
            "request": request, "current_user": current_user, "payments": payments,
            "customers": customers, "flash": f, "customer_filter": customer_id,
            "active_page": "payments",
        },
    )


@router.get("/create", response_class=HTMLResponse)
def create_payment_form(
    request: Request,
    customer_id: Optional[int] = None,
    subscription_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard
    customers = db.query(Customer).order_by(Customer.nombre).all()
    subscriptions = db.query(Subscription).order_by(Subscription.fecha_vencimiento.desc()).all()
    f = get_flash(request)
    return templates.TemplateResponse(
        "payments/create.html",
        {
            "request": request, "current_user": current_user, "customers": customers,
            "subscriptions": subscriptions, "flash": f, "error": None,
            "metodos": METODOS, "monedas": MONEDAS,
            "prefill_customer_id": customer_id, "prefill_subscription_id": subscription_id,
            "active_page": "payments",
        },
    )


@router.post("/create")
def create_payment(
    request: Request,
    customer_id: int = Form(...),
    subscription_id: str = Form(""),
    metodo: str = Form(...),
    monto: float = Form(...),
    moneda: str = Form("USD"),
    notas: str = Form(""),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard

    customers = db.query(Customer).order_by(Customer.nombre).all()
    subscriptions = db.query(Subscription).order_by(Subscription.fecha_vencimiento.desc()).all()

    def re_render(error):
        return templates.TemplateResponse(
            "payments/create.html",
            {
                "request": request, "current_user": current_user, "customers": customers,
                "subscriptions": subscriptions, "error": error,
                "metodos": METODOS, "monedas": MONEDAS,
                "prefill_customer_id": customer_id, "active_page": "payments",
            },
        )

    if metodo not in METODOS:
        return re_render("Método de pago inválido.")
    if moneda not in MONEDAS:
        return re_render("Moneda inválida.")
    if monto <= 0:
        return re_render("El monto debe ser mayor a 0.")

    sub_id = int(subscription_id) if subscription_id.strip() else None
    payment = Payment(
        customer_id=customer_id,
        subscription_id=sub_id,
        metodo=metodo,
        monto=monto,
        moneda=moneda,
        notas=notas.strip() or None,
    )
    db.add(payment)
    db.commit()
    flash(request, "success", "Pago registrado correctamente.")
    return RedirectResponse("/payments", status_code=303)


@router.get("/{payment_id}/edit", response_class=HTMLResponse)
def edit_payment_form(
    payment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        flash(request, "error", "Pago no encontrado.")
        return RedirectResponse("/payments", status_code=302)
    customers = db.query(Customer).order_by(Customer.nombre).all()
    subscriptions = db.query(Subscription).order_by(Subscription.fecha_vencimiento.desc()).all()
    return templates.TemplateResponse(
        "payments/edit.html",
        {
            "request": request, "current_user": current_user, "payment": payment,
            "customers": customers, "subscriptions": subscriptions,
            "metodos": METODOS, "monedas": MONEDAS, "error": None, "active_page": "payments",
        },
    )


@router.post("/{payment_id}/edit")
def edit_payment(
    payment_id: int,
    request: Request,
    customer_id: int = Form(...),
    subscription_id: str = Form(""),
    metodo: str = Form(...),
    monto: float = Form(...),
    moneda: str = Form("USD"),
    notas: str = Form(""),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        flash(request, "error", "Pago no encontrado.")
        return RedirectResponse("/payments", status_code=302)
    sub_id = int(subscription_id) if subscription_id.strip() else None
    payment.customer_id = customer_id
    payment.subscription_id = sub_id
    payment.metodo = metodo
    payment.monto = monto
    payment.moneda = moneda
    payment.notas = notas.strip() or None
    db.commit()
    flash(request, "success", "Pago actualizado.")
    return RedirectResponse("/payments", status_code=303)


@router.post("/{payment_id}/confirm")
def confirm_payment(
    payment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        flash(request, "error", "Pago no encontrado.")
        return RedirectResponse("/payments", status_code=302)
    payment.estado = "confirmado"
    db.commit()
    flash(request, "success", "Pago confirmado correctamente.")
    return RedirectResponse("/payments", status_code=303)


@router.post("/{payment_id}/delete")
def delete_payment(
    payment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        flash(request, "error", "Pago no encontrado.")
        return RedirectResponse("/payments", status_code=302)
    db.delete(payment)
    db.commit()
    flash(request, "success", "Pago eliminado.")
    return RedirectResponse("/payments", status_code=303)
