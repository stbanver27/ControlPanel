# app/routes/users.py
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user, flash, get_flash
from app.core.security import hash_password, verify_password
from app.models.user import User

router = APIRouter(prefix="/users")
templates = Jinja2Templates(directory="templates")


def _guard(current_user):
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    if current_user.rol != "superadmin":
        return RedirectResponse("/dashboard", status_code=302)
    return None


@router.get("", response_class=HTMLResponse)
def list_users(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    guard = _guard(current_user)
    if guard:
        return guard
    users = db.query(User).order_by(User.id).all()
    f = get_flash(request)
    return templates.TemplateResponse(
        "users/list.html",
        {"request": request, "current_user": current_user, "users": users, "flash": f, "active_page": "users"},
    )


@router.get("/create", response_class=HTMLResponse)
def create_user_form(request: Request, current_user=Depends(get_current_user)):
    guard = _guard(current_user)
    if guard:
        return guard
    return templates.TemplateResponse(
        "users/create.html",
        {"request": request, "current_user": current_user, "error": None, "active_page": "users"},
    )


@router.post("/create")
def create_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    rol: str = Form(...),
    is_active: bool = Form(True),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _guard(current_user)
    if guard:
        return guard

    def re_render(error):
        return templates.TemplateResponse(
            "users/create.html",
            {"request": request, "current_user": current_user, "error": error,
             "form": {"email": email, "rol": rol}, "active_page": "users"},
        )

    if password != confirm_password:
        return re_render("Las contraseñas no coinciden.")
    if len(password) < 6:
        return re_render("La contraseña debe tener al menos 6 caracteres.")
    email = email.strip().lower()
    if db.query(User).filter(User.email == email).first():
        return re_render("Ya existe un usuario con ese email.")
    if rol not in ("superadmin", "admin"):
        return re_render("Rol inválido.")

    user = User(email=email, hashed_password=hash_password(password), rol=rol, is_active=is_active)
    db.add(user)
    db.commit()
    flash(request, "success", f"Usuario {email} creado correctamente.")
    return RedirectResponse("/users", status_code=303)


@router.get("/{user_id}/edit", response_class=HTMLResponse)
def edit_user_form(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _guard(current_user)
    if guard:
        return guard
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        flash(request, "error", "Usuario no encontrado.")
        return RedirectResponse("/users", status_code=302)
    return templates.TemplateResponse(
        "users/edit.html",
        {"request": request, "current_user": current_user, "user": user, "error": None, "active_page": "users"},
    )


@router.post("/{user_id}/edit")
def edit_user(
    user_id: int,
    request: Request,
    email: str = Form(...),
    rol: str = Form(...),
    is_active: str = Form("off"),
    password: str = Form(""),
    confirm_password: str = Form(""),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _guard(current_user)
    if guard:
        return guard

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        flash(request, "error", "Usuario no encontrado.")
        return RedirectResponse("/users", status_code=302)

    active_bool = is_active == "on"

    def re_render(error):
        return templates.TemplateResponse(
            "users/edit.html",
            {"request": request, "current_user": current_user, "user": user,
             "error": error, "active_page": "users"},
        )

    email = email.strip().lower()
    if email != user.email and db.query(User).filter(User.email == email).first():
        return re_render("Ya existe otro usuario con ese email.")
    if rol not in ("superadmin", "admin"):
        return re_render("Rol inválido.")

    # Prevent deactivating last superadmin
    if (not active_bool or rol != "superadmin") and user.rol == "superadmin":
        active_superadmins = (
            db.query(User)
            .filter(User.rol == "superadmin", User.is_active == True, User.id != user_id)
            .count()
        )
        if active_superadmins == 0:
            return re_render("No se puede modificar al único superadmin activo.")

    if password:
        if password != confirm_password:
            return re_render("Las contraseñas no coinciden.")
        if len(password) < 6:
            return re_render("La contraseña debe tener al menos 6 caracteres.")
        user.hashed_password = hash_password(password)

    user.email = email
    user.rol = rol
    user.is_active = active_bool
    db.commit()
    flash(request, "success", "Usuario actualizado correctamente.")
    return RedirectResponse("/users", status_code=303)


@router.post("/{user_id}/delete")
def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    guard = _guard(current_user)
    if guard:
        return guard

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        flash(request, "error", "Usuario no encontrado.")
        return RedirectResponse("/users", status_code=302)

    if user.id == current_user.id:
        flash(request, "error", "No puedes eliminar tu propio usuario.")
        return RedirectResponse("/users", status_code=302)

    if user.rol == "superadmin":
        remaining = (
            db.query(User)
            .filter(User.rol == "superadmin", User.is_active == True, User.id != user_id)
            .count()
        )
        if remaining == 0:
            flash(request, "error", "No se puede eliminar al único superadmin activo.")
            return RedirectResponse("/users", status_code=302)

    db.delete(user)
    db.commit()
    flash(request, "success", "Usuario eliminado.")
    return RedirectResponse("/users", status_code=303)
