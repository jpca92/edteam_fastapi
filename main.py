from typing import Optional, List
from urllib import response

from models.Developer import Developer
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, status

from developers import developers

app = FastAPI()

users = [
    {"id":1,"nombre":"Juan", "apellido":"Perez", "edad": 30},
    {"id":2,"nombre":"Maria", "apellido":"Gomez", "edad": 25},
    {"id":3,"nombre":"Pedro", "apellido":"Lopez", "edad": 35},
]

@app.get('/')
def mensaje():
    return {"Hola: Mundo"}


@app.get('/login')
def mensaje():
    return 'Inicie sesion'

@app.get('/auth/login/users')
def mensaje():
    return 'Inicie sesion'

@app.get('/users')
def get_user():
    return users

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = next( (user for user in users if user["id"] == user_id), None)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.get("/users/{user_id}/edad/{edad}")
def get_user_age(user_id: int, edad: int):
    user = next( (user for user in users if user["id"] == user_id and user["edad"] == edad), None)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

# Query Parameters
@app.get("/users/{user_id}")
def get_user_age_query(user_id: int, edad: int):
    user = next( (user for user in users if user["id"] == user_id and user["edad"] == edad), None)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

# Query Parameters with and
@app.get("/users_query/{user_id}")
def get_user_by_age_and_name(user_id: int, edad: int, nombre: str):
    user = next( (user for user in users if user["id"] == user_id and user["edad"] == edad and user["nombre"] == nombre), None)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

# Query Parameters with and and Optional
@app.get("/users_query_fullname/{user_id}")
def get_user_by_age_and_name_and_surname(user_id: int, edad: int, nombre: str, apellido: Optional[str]='Perez'):
    if not apellido:
        print("No se proporcionó apellido")
    user = next( (user for user in users 
                  if user["id"] == user_id 
                  and user["edad"] == edad 
                  and user["nombre"] == nombre 
                  and (apellido is None or user["apellido"] == apellido)), None)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@app.get('/welcome/{nombre}/{apellido}')
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
        response.status_code = status.HTTP_200_OK
    return {"resultado": resultado}


# Capitulo 3
@app.get("/developers")
def get_developers():
    return developers

@app.get("/developers/{id}")
def get_developer(id: int):
    developer = next((dev for dev in developers if dev["id"] == id), None)
    if developer is None:
        raise HTTPException(status_code=404, detail="Developer not found")
    return developer

@app.get("/developers/{id}/skills")
def get_developer_skills(id: int):
    developer = next((dev for dev in developers if dev["id"] == id), None)
    if developer is None:
        raise HTTPException(status_code=404, detail="Developer not found")
    return developer["skills"]

@app.get("/developers/{id}/experience")
def get_developer_experience(id: int):
    developer = next((dev for dev in developers if dev["id"] == id), None)
    if developer is None:
        raise HTTPException(status_code=404, detail="Developer not found")
    return developer["experience"]

@app.get("/developers/{id}/languages")
def get_developer_languages(id: int):
    developer = next((dev for dev in developers if dev["id"] == id), None)
    if developer is None:
        raise HTTPException(status_code=404, detail="Developer not found")
    return developer["languages"]


# Post method to create a new developer

@app.post("/developers")
def create_developer(developer: Developer):
    new_developer = developer.model_dump()
    developers.append(new_developer)

    return new_developer


# Delete method to delete a developer by id
@app.delete("/developers/{id}")
def delete_developer(id: int):
    developer = next((dev for dev in developers if dev["id"] == id), None)
    if developer is None:
        raise HTTPException(status_code=404, detail="Developer not found")
    developers.remove(developer)
    return {"message": "Developer deleted successfully"}