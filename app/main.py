# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import SESSION_SECRET
from app.db.session import engine, Base
from app.models import User, Customer, Tag, customer_tags, Plan, Subscription, Payment
from app.routes import auth, dashboard, users, customers, plans, subscriptions, payments, renewals

app = FastAPI(title="IPTV Control Center", docs_url=None, redoc_url=None)

app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(users.router)
app.include_router(customers.router)
app.include_router(plans.router)
app.include_router(subscriptions.router)
app.include_router(payments.router)
app.include_router(renewals.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    _seed_tags()


def _seed_tags():
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        default_tags = ["Cliente frecuente", "Internacional", "Soporte frecuente"]
        for nombre in default_tags:
            if not db.query(Tag).filter(Tag.nombre == nombre).first():
                db.add(Tag(nombre=nombre))
        db.commit()
    finally:
        db.close()
