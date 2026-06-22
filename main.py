import os
from http.client import HTTPException
from fastapi import FastAPI, Query, File, UploadFile, HTTPException
from config import load_config
from logger import logger
import re
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Annotated
from typing import List


# Загружаем конфигурацию
config = load_config()

app = FastAPI()


class Contact(BaseModel):
    email: EmailStr
    phone: Optional[str] = Field(None, min_length=7, max_length=15)

    @validator('phone')
    def validate_phone(cls, phone):
        if phone is not None:
            if not re.match(r'^\d{7,15}$', phone):
                raise ValueError('Invalid phone number')
        return phone


class Feedback(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    message: str = Field(..., min_length=10, max_length=500)
    contact: Contact

    @validator('message')
    def validate_message(cls, message):
        forbidden = ["редиска", "бяка", "козявка"]
        # ИСПРАВЛЕНО: правильный паттерн с закрывающей скобкой
        pattern = r'\b(' + '|'.join(forbidden) + r')\b'
        # ИСПРАВЛЕНО: re.search вместо re.rearch
        if re.search(pattern, message, re.IGNORECASE):
            raise ValueError("Сообщение содержит запрещенные слова")
        return message


@app.get("/")
def read_root():
    logger.info("Корневой маршрут вызван")
    return {"message": "Hello, World!"}



class User(BaseModel):
    name: str
    age: int

class UserResponse(BaseModel):
    message: str
    user: User

@app.post("/users/", response_model=UserResponse)
async def create_user(user: User):
    return {"message": f"Пользователь {user.name} создан!", "user": user}


class Event(BaseModel):
    name: str
    timestamp: datetime


@app.post("/events/")
async def create_event(event: Event):
    return event


@app.get("/custom")
def read_custom_message():
    logger.info("Маршрут /custom вызван")
    return {"message": "This is a custom message!"}


@app.get("/config")
def get_config():
    """Маршрут для проверки конфигурации"""
    return {
        "secret_key": config.secret_key,
        "database_url": config.db.database_url,
        "debug": config.debug,
    }



@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


# другой пример обновления роута из main.py
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    with open(file.filename, "wb") as f:
        while chunk := await file.read(1024):  # Читаем по 1 КБ
            f.write(chunk)
    return {"filename": file.filename}


@app.post("/multiple-files/")
async def upload_multiple_files(files: List[UploadFile]):
    return {"filenames": [file.filename for file in files]}


@app.get("/hello/{name}")
def hello(name: str):
    logger.info(f"Приветствие для {name}")
    return {"message": f"Привет, {name}!"}


# ИСПРАВЛЕНО: create_feedback вместо cleate_feedback
@app.post('/feedback')
async def create_feedback(feedback: Feedback, is_premium: bool = Query(False)):
    response_message = f'Спасибо, {feedback.name}! Ваш отзыв сохранён.'

    if is_premium:
        response_message += " Ваш отзыв будет рассмотрен в приоритетном порядке."

    return {'message': response_message}


@app.get("/items/")
async def read_item(
    skip: int = Query(0, alias="start", ge=0),
    limit: int = Query(10, le=100)
):
    return {"skip": skip, "limit": limit}


class UserCreate(BaseModel):
    name: str
    email: str
    age: int
    is_subscribed: bool


@app.post("/create_user/")
async def create_item(create_user: UserCreate):
    return create_user

sample_products = [
    {"product_id": 123, "name": "Smartphone", "category": "Electronics", "price": 599.99},
    {"product_id": 456, "name": "Phone Case", "category": "Accessories", "price": 19.99},
    {"product_id": 789, "name": "Iphone", "category": "Electronics", "price": 1299.99},
    {"product_id": 101, "name": "Headphones", "category": "Accessories", "price": 99.99},
    {"product_id": 202, "name": "Smartwatch", "category": "Electronics", "price": 299.99}
]


@app.get('/product/{product_id}')
async def get_product(product_id: int):
    for product in sample_products:
        if product["product_id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.get('/products/search')
async def search_psoducts(
        keyword: str,
        category: Optional[str] = None,
        limit: int = Query(10, ge=1, le=100)
):
    res = []
    keyword = keyword.lower()

    for product in sample_products:
        if keyword not in product['name'].lower():
            continue

        if category and product['category'].lower() != category.lower():
            continue

        res.append(product)

        if len(res) >= limit:
            break

    return res






# Запуск (если файл выполняется напрямую)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=config.debug)