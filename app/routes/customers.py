# app/routes/customers.py
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.dependencies import get_db, get_current_user, flash, get_flash
from app.models.customer import Customer, Tag
from app.services.subscription import calc_status

router = APIRouter(prefix="/customers")
templates = Jinja2Templates(directory="templates")


def _auth(current_user):
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    return None


@router.get("", response_class=HTMLResponse)
def list_customers(
    request: Request,
    q: str = "",
    estado: str = "",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard
    query = db.query(Customer)
    if q:
        query = query.filter(
            (Customer.nombre.ilike(f"%{q}%")) | (Customer.username.ilike(f"%{q}%"))
        )
    if estado:
        query = query.filter(Customer.estado == estado)
    customers = query.order_by(Customer.nombre).all()
    f = get_flash(request)
    return templates.TemplateResponse(
        "customers/list.html",
        {
            "request": request,
            "current_user": current_user,
            "customers": customers,
            "flash": f,
            "q": q,
            "estado_filter": estado,
            "active_page": "customers",
        },
    )


@router.get("/create", response_class=HTMLResponse)
def create_customer_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard
    tags = db.query(Tag).all()
    return templates.TemplateResponse(
        "customers/create.html",
        {"request": request, "current_user": current_user, "tags": tags, "error": None,
         "form": {}, "active_page": "customers"},
    )


@router.post("/create")
def create_customer(
    request: Request,
    nombre: str = Form(...),
    whatsapp: str = Form(""),
    email: str = Form(""),
    pais: str = Form(""),
    username: str = Form(""),
    estado: str = Form("activo"),
    notas: str = Form(""),
    tag_ids: List[int] = Form(default=[]),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard

    tags = db.query(Tag).all()
    form_data = {"nombre": nombre, "whatsapp": whatsapp, "email": email,
                 "pais": pais, "username": username, "estado": estado, "notas": notas}

    def re_render(error):
        return templates.TemplateResponse(
            "customers/create.html",
            {"request": request, "current_user": current_user, "tags": tags,
             "error": error, "form": form_data, "selected_tags": tag_ids, "active_page": "customers"},
        )

    if not nombre.strip():
        return re_render("El nombre es obligatorio.")
    if username.strip():
        existing = db.query(Customer).filter(Customer.username == username.strip()).first()
        if existing:
            return re_render("El username ya está en uso.")

    customer = Customer(
        nombre=nombre.strip(),
        whatsapp=whatsapp.strip() or None,
        email=email.strip() or None,
        pais=pais.strip() or None,
        username=username.strip() or None,
        estado=estado,
        notas=notas.strip() or None,
    )
    if tag_ids:
        customer.tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
    db.add(customer)
    db.commit()
    flash(request, "success", f"Cliente '{nombre}' creado correctamente.")
    return RedirectResponse("/customers", status_code=303)


@router.get("/{customer_id}", response_class=HTMLResponse)
def customer_detail(
    customer_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        flash(request, "error", "Cliente no encontrado.")
        return RedirectResponse("/customers", status_code=302)
    f = get_flash(request)
    return templates.TemplateResponse(
        "customers/detail.html",
        {
            "request": request,
            "current_user": current_user,
            "customer": customer,
            "flash": f,
            "calc_status": calc_status,
            "active_page": "customers",
        },
    )


@router.get("/{customer_id}/edit", response_class=HTMLResponse)
def edit_customer_form(
    customer_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        flash(request, "error", "Cliente no encontrado.")
        return RedirectResponse("/customers", status_code=302)
    tags = db.query(Tag).all()
    return templates.TemplateResponse(
        "customers/edit.html",
        {"request": request, "current_user": current_user, "customer": customer,
         "tags": tags, "error": None, "active_page": "customers"},
    )


@router.post("/{customer_id}/edit")
def edit_customer(
    customer_id: int,
    request: Request,
    nombre: str = Form(...),
    whatsapp: str = Form(""),
    email: str = Form(""),
    pais: str = Form(""),
    username: str = Form(""),
    estado: str = Form("activo"),
    notas: str = Form(""),
    tag_ids: List[int] = Form(default=[]),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        flash(request, "error", "Cliente no encontrado.")
        return RedirectResponse("/customers", status_code=302)

    tags = db.query(Tag).all()

    def re_render(error):
        return templates.TemplateResponse(
            "customers/edit.html",
            {"request": request, "current_user": current_user, "customer": customer,
             "tags": tags, "error": error, "active_page": "customers"},
        )

    if not nombre.strip():
        return re_render("El nombre es obligatorio.")
    if username.strip() and username.strip() != customer.username:
        existing = db.query(Customer).filter(
            Customer.username == username.strip(), Customer.id != customer_id
        ).first()
        if existing:
            return re_render("El username ya está en uso.")

    customer.nombre = nombre.strip()
    customer.whatsapp = whatsapp.strip() or None
    customer.email = email.strip() or None
    customer.pais = pais.strip() or None
    customer.username = username.strip() or None
    customer.estado = estado
    customer.notas = notas.strip() or None
    customer.tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all() if tag_ids else []
    db.commit()
    flash(request, "success", "Cliente actualizado correctamente.")
    return RedirectResponse(f"/customers/{customer_id}", status_code=303)


@router.post("/{customer_id}/delete")
def delete_customer(
    customer_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        flash(request, "error", "Cliente no encontrado.")
        return RedirectResponse("/customers", status_code=302)
    db.delete(customer)
    db.commit()
    flash(request, "success", "Cliente eliminado.")
    return RedirectResponse("/customers", status_code=303)
