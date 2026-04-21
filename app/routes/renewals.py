# app/routes/renewals.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
from app.core.dependencies import get_db, get_current_user, get_flash
from app.models.subscription import Subscription
from app.services.subscription import calc_status

router = APIRouter(prefix="/renewals")
templates = Jinja2Templates(directory="templates")


@router.get("", response_class=HTMLResponse)
def renewals(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user:
        return RedirectResponse("/login", status_code=302)

    hoy = date.today()
    all_subs = db.query(Subscription).all()

    vencen_hoy = [s for s in all_subs if s.fecha_vencimiento == hoy]
    vencen_3dias = [s for s in all_subs if hoy < s.fecha_vencimiento and (s.fecha_vencimiento - hoy).days <= 3]
    ya_vencidas = [s for s in all_subs if s.fecha_vencimiento < hoy]

    f = get_flash(request)
    return templates.TemplateResponse(
        "renewals/list.html",
        {
            "request": request,
            "current_user": current_user,
            "flash": f,
            "vencen_hoy": vencen_hoy,
            "vencen_3dias": vencen_3dias,
            "ya_vencidas": ya_vencidas,
            "calc_status": calc_status,
            "today": hoy,
            "active_page": "renewals",
        },
    )
