from imports import *
import jwt as pyjwt


# Параметр tokenUrl указывает маршрут, по которому клиенты смогут получить токен
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login_4")

SECRET_KEY = "your-secret-key-here-change-in-production"  # В реальной практике генерируйте ключ, например, с помощью 'openssl rand -hex 32', и храните его в безопасности
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Время жизни токена

# Функция для создания JWT токена с заданным временем жизни
def create_jwt_token(data: Dict):
    """
    Функция для создания JWT токена. Мы копируем входные данные, добавляем время истечения и кодируем токен.
    """
    to_encode = data.copy()  # Копируем данные, чтобы не изменить исходный словарь
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Задаем время истечения токена
    to_encode.update({"exp": expire})  # Добавляем время истечения в данные токена
    return pyjwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Кодируем токен с использованием секретного ключа и алгоритма

# Функция для получения пользователя из токена
def verify_jwt_token(token: str) -> Dict:
    """
    Функция для извлечения информации о пользователе из токена. Проверяем токен и извлекаем утверждение о пользователе.
    """
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Декодируем токен с помощью секретного ключа
        return payload  # Возвращаем утверждение о пользователе (subject) из полезной нагрузки
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except pyjwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_jwt_token(token)
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return username