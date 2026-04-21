# app/routes/plans.py
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user, flash, get_flash
from app.models.plan import Plan

router = APIRouter(prefix="/plans")
templates = Jinja2Templates(directory="templates")


def _auth(current_user):
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    return None


@router.get("", response_class=HTMLResponse)
def list_plans(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    guard = _auth(current_user)
    if guard:
        return guard
    plans = db.query(Plan).order_by(Plan.nombre).all()
    f = get_flash(request)
    return templates.TemplateResponse(
        "plans/list.html",
        {"request": request, "current_user": current_user, "plans": plans, "flash": f, "active_page": "plans"},
    )


@router.get("/create", response_class=HTMLResponse)
def create_plan_form(request: Request, current_user=Depends(get_current_user)):
    guard = _auth(current_user)
    if guard:
        return guard
    return templates.TemplateResponse(
        "plans/create.html",
        {"request": request, "current_user": current_user, "error": None, "form": {}, "active_page": "plans"},
    )


@router.post("/create")
def create_plan(
    request: Request,
    nombre: str = Form(...),
    duracion_dias: int = Form(...),
    pantallas: int = Form(...),
    precio: float = Form(...),
    activo: str = Form("off"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard

    form_data = {"nombre": nombre, "duracion_dias": duracion_dias,
                 "pantallas": pantallas, "precio": precio}

    def re_render(error):
        return templates.TemplateResponse(
            "plans/create.html",
            {"request": request, "current_user": current_user, "error": error,
             "form": form_data, "active_page": "plans"},
        )

    if not nombre.strip():
        return re_render("El nombre es obligatorio.")
    if duracion_dias <= 0 or pantallas <= 0 or precio < 0:
        return re_render("Los valores numéricos deben ser positivos.")

    plan = Plan(
        nombre=nombre.strip(),
        duracion_dias=duracion_dias,
        pantallas=pantallas,
        precio=precio,
        activo=(activo == "on"),
    )
    db.add(plan)
    db.commit()
    flash(request, "success", f"Plan '{nombre}' creado correctamente.")
    return RedirectResponse("/plans", status_code=303)


@router.get("/{plan_id}/edit", response_class=HTMLResponse)
def edit_plan_form(
    plan_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        flash(request, "error", "Plan no encontrado.")
        return RedirectResponse("/plans", status_code=302)
    return templates.TemplateResponse(
        "plans/edit.html",
        {"request": request, "current_user": current_user, "plan": plan, "error": None, "active_page": "plans"},
    )


@router.post("/{plan_id}/edit")
def edit_plan(
    plan_id: int,
    request: Request,
    nombre: str = Form(...),
    duracion_dias: int = Form(...),
    pantallas: int = Form(...),
    precio: float = Form(...),
    activo: str = Form("off"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard

    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        flash(request, "error", "Plan no encontrado.")
        return RedirectResponse("/plans", status_code=302)

    plan.nombre = nombre.strip()
    plan.duracion_dias = duracion_dias
    plan.pantallas = pantallas
    plan.precio = precio
    plan.activo = activo == "on"
    db.commit()
    flash(request, "success", "Plan actualizado correctamente.")
    return RedirectResponse("/plans", status_code=303)


@router.post("/{plan_id}/delete")
def delete_plan(
    plan_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _auth(current_user)
    if guard:
        return guard
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        flash(request, "error", "Plan no encontrado.")
        return RedirectResponse("/plans", status_code=302)
    db.delete(plan)
    db.commit()
    flash(request, "success", "Plan eliminado.")
    return RedirectResponse("/plans", status_code=303)


# JSON endpoint for JS autocompletion
@router.get("/api/{plan_id}")
def get_plan_json(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        return JSONResponse({"error": "not found"}, status_code=404)
    return {"id": plan.id, "pantallas": plan.pantallas, "precio": plan.precio,
            "duracion_dias": plan.duracion_dias}
