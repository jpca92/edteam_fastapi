from getpass import getpass

import bcrypt

from mongodb_client import users_collection


users = [
    {"id": 1, "nombre": "Juan", "apellido": "Perez", "edad": 30},
    {"id": 2, "nombre": "Maria", "apellido": "Gomez", "edad": 25},
    {"id": 3, "nombre": "Pedro", "apellido": "Lopez", "edad": 35},
]

for user in users:
    password = getpass(f"Password for {user['nombre']}: ")
    user["password_hash"] = bcrypt.hashpw(
        password.encode(), bcrypt.gensalt()
    ).decode()

for user in users:
    users_collection.replace_one({"id": user["id"]}, user, upsert=True)

users_collection.create_index("nombre", unique=True)
print(f"Inserted {len(users)} users into MongoDB")
