from auth.login import create_user, get_user_by_username
from database.db import init_db


# إنشاء database والجداول
init_db()


print("==============================")
print("   SMART FILAHA - ADMIN")
print("==============================")

username = input("Nom d'utilisateur Admin: ")
email = input("Email Admin: ")
password = input("Mot de passe Admin: ")


# نتأكد واش username موجود
existing_user = get_user_by_username(username)

if existing_user:

    print("\n❌ Ce nom d'utilisateur existe déjà.")

else:

    create_user(
        username=username,
        email=email,
        password=password,
        role="admin"
    )

    print("\n✅ Compte Admin créé avec succès !")
    print("Username :", username)
    print("Role     : admin")