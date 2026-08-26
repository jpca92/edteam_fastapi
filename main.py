import os
from typing import Optional

from dotenv import load_dotenv
from models.Developer import Developer
from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.responses import PlainTextResponse

from developers_data import developers_data
from mongodb_client import users_collection
from models.User import LoginRequest, UserResponse

import bcrypt
import jwt

load_dotenv()

app = FastAPI()

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET no está configurado en el entorno")
JWT_ALGORITHM = "HS256"

developers: list[Developer] = [
    Developer.model_validate(developer) for developer in developers_data
]

async def verify_token(request: Request):
    authorization = request.headers.get("Authorization")

    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = data.get("sub")
    user = users_collection.find_one({"nombre": username})

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@app.middleware("http")
async def my_middleware(request: Request, call_next):
    print("Antes de la solicitud")
    print(f'Accediendo a la ruta: {request.url.path}')
    response = await call_next(request)
    print("Después de la solicitud")
    return response

# ============================================================
# MONGODB ATLAS: USER ENDPOINTS FOR TESTING
# These routes read user data from the MongoDB users collection.
# ============================================================
@app.post("/login_users")
def login(credentials: LoginRequest):
    user = users_collection.find_one({"nombre": credentials.username})

    if user is None or not bcrypt.checkpw(
        credentials.password.encode(), user["password_hash"].encode()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    print("Inicio de sesión con usuario:", credentials.username, "Correcto")

    token = jwt.encode(
        {"sub": user["nombre"]},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }

@app.get('/')
def mensaje():
    return {"Hola: Mundo"}


@app.get('/login', response_class=PlainTextResponse)
def mensaje():
    return 'Inicie sesion'

@app.get('/auth/login/users', response_class=PlainTextResponse)
def mensaje():
    return 'Inicie sesion'

@app.get('/users', response_model=list[UserResponse])
def get_user():
    return list(users_collection.find({}, {"_id": 0, "password_hash": 0}))

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    user = users_collection.find_one(
        {"id": user_id},
        {"_id": 0, "password_hash": 0},
    )

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.get("/users/{user_id}/edad/{edad}", response_model=UserResponse)
def get_user_age(user_id: int, edad: int):
    user = users_collection.find_one(
        {"id": user_id, "edad": edad},
        {"_id": 0, "password_hash": 0},
    )

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

# Query Parameters
@app.get("/users/{user_id}/by-age", response_model=UserResponse)
def get_user_age_query(user_id: int, edad: int):
    user = users_collection.find_one(
        {"id": user_id, "edad": edad},
        {"_id": 0, "password_hash": 0},
    )

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

# Query Parameters with and
@app.get("/users_query/{user_id}", response_model=UserResponse)
def get_user_by_age_and_name(user_id: int, edad: int, nombre: str):
    user = users_collection.find_one(
        {"id": user_id, "edad": edad, "nombre": nombre},
        {"_id": 0, "password_hash": 0},
    )

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

# Query Parameters with and and Optional
@app.get("/users_query_fullname/{user_id}", response_model=UserResponse)
def get_user_by_age_and_name_and_surname(user_id: int, edad: int, nombre: str, apellido: Optional[str]='Perez'):
    if not apellido:
        print("No se proporcionó apellido")
    query = {"id": user_id, "edad": edad, "nombre": nombre}
    if apellido is not None:
        query["apellido"] = apellido
    user = users_collection.find_one(query, {"_id": 0, "password_hash": 0})

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
# ============================================================
# END OF MONGODB ATLAS USER ENDPOINTS
# ============================================================

@app.get('/welcome/{nombre}/{apellido}', response_class=PlainTextResponse)
def mensaje_bienvenida(nombre: str, apellido: str):
    return f"Bienvenido {nombre} {apellido} a la API de FastAPI"


@app.get('/suma/{numero1}/{numero2}', status_code=status.HTTP_200_OK)
def suma(numero1: int, numero2: int):
    resultado = numero1 + numero2
    return {"resultado": resultado}

@app.get('/division/{numero1}/{numero2}')
def division(numero1: int, numero2: int):
    if numero2 == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se puede dividir por cero")
    else:
        resultado = numero1 / numero2 if numero2 != 0 else 0
    return {"resultado": resultado}


# Capitulo 3
@app.get("/developers")
def get_developers(_: dict = Depends(verify_token)):
    return {
        "developers": developers,
        "total_developers": len(developers),
    }

@app.get("/developers/{developer_id}")
def get_developer(developer_id: int, _: dict = Depends(verify_token)):
    developer = next(
        (dev for dev in developers if dev.id == developer_id),
        None,
    )

    if developer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Developer not found",
        )

    return developer

@app.get("/developers/{developer_id}/skills")
def get_developer_skills(developer_id: int):
    developer = next((dev for dev in developers if dev.id == developer_id), None)
    if developer is None:
        raise HTTPException(status_code=404, detail="Developer not found")
    return developer.skills

@app.get("/developers/{developer_id}/experience")
def get_developer_experience(developer_id: int):
    developer = next((dev for dev in developers if dev.id == developer_id), None)
    if developer is None:
        raise HTTPException(status_code=404, detail="Developer not found")
    return developer.experience

@app.get("/developers/{developer_id}/languages")
def get_developer_languages(developer_id: int):
    developer = next((dev for dev in developers if dev.id == developer_id), None)
    if developer is None:
        raise HTTPException(status_code=404, detail="Developer not found")
    return developer.languages


# Post method to create a new developer

@app.post("/developers", status_code=status.HTTP_201_CREATED)
def create_developer(developer: Developer):
    if any(dev.id == developer.id for dev in developers):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Developer ID already exists",
        )

    developers.append(developer)

    return {
        "developer": developer,
        "total_developers": len(developers),
    }


# Delete method to delete a developer by id
@app.delete("/developers/{developer_id}")
def delete_developer(developer_id: int):
    developer = next((dev for dev in developers if dev.id == developer_id), None)
    if developer is None:
        raise HTTPException(status_code=404, detail="Developer not found")
    developers.remove(developer)
    return {
        "message": "Developer deleted successfully",
        "total_developers": len(developers),
    }

# Put method to update a developer by id
@app.put("/developers/{developer_id}")
def update_developer(developer_id: int, updated_developer: Developer):
    if updated_developer.id != developer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path ID and developer ID must match",
        )

    developer = next((dev for dev in developers if dev.id == developer_id), None)
    if developer is None:
        raise HTTPException(status_code=404, detail="Developer not found")

    developer.name = updated_developer.name
    developer.country = updated_developer.country
    developer.age = updated_developer.age
    developer.skills = updated_developer.skills
    developer.experience = updated_developer.experience
    developer.languages = updated_developer.languages

    return developer
