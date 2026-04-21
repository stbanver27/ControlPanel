# create_first_admin.py
import sys
import getpass
from app.db.session import engine, SessionLocal, Base
from app.models import User, Tag, customer_tags, Customer, Plan, Subscription, Payment
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

existing = db.query(User).filter(User.rol == "superadmin", User.is_active == True).first()
if existing:
    print(f"⚠️  Ya existe un superadmin activo: {existing.email}")
    print("   Gestiona los usuarios desde el panel web.")
    db.close()
    sys.exit(0)

print("=== Crear primer Superadmin ===")
email = input("Email: ").strip().lower()
if not email:
    print("El email no puede estar vacío.")
    db.close()
    sys.exit(1)

if db.query(User).filter(User.email == email).first():
    print(f"Ya existe un usuario con el email {email}.")
    db.close()
    sys.exit(1)

while True:
    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirmar password: ")
    if password != confirm:
        print("Las contraseñas no coinciden. Intenta de nuevo.")
        continue
    if len(password) < 6:
        print("La contraseña debe tener al menos 6 caracteres.")
        continue
    break

user = User(email=email, hashed_password=hash_password(password), rol="superadmin", is_active=True)
db.add(user)

# Seed tags
default_tags = ["Cliente frecuente", "Internacional", "Soporte frecuente"]
for nombre in default_tags:
    if not db.query(Tag).filter(Tag.nombre == nombre).first():
        db.add(Tag(nombre=nombre))

db.commit()
db.close()

print(f"\n✅ Superadmin creado: {email}")
print("   Ya puedes ingresar al panel en http://localhost:8000")
