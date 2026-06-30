from imports import *


USERS_DATA = [
    {"username": "john_doe", "password": "securepassword123"},
    {"username": "admin", "password": "adminpass"}  # В реальной базе данных пароли должны храниться в виде хэшей
]

def get_user(username: str):
    """
    Функция для поиска пользователя по имени пользователя.
    В реальном проекте это должно быть запросом к базе данных.
    """
    for user in USERS_DATA:
        if user.get("username") == username:
            return user
    return None


def authenticate_user(username: str, password: str) -> bool:
    """
    Проверка учетных данных
    """
    for user in USERS_DATA:
        if user.get("username") == username and user.get("password") == password:
            return True

    return False


