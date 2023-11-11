from enum import Enum
from time import time
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException

app = FastAPI()


class DogType(str, Enum):
    terrier = "terrier"
    bulldog = "bulldog"
    dalmatian = "dalmatian"


class Dog(BaseModel):
    name: str
    pk: int
    kind: DogType


class Timestamp(BaseModel):
    id: int
    timestamp: int


dogs_db = {
    0: Dog(name='Bob', pk=0, kind='terrier'),
    1: Dog(name='Marli', pk=1, kind="bulldog"),
    2: Dog(name='Snoopy', pk=2, kind='dalmatian'),
    3: Dog(name='Rex', pk=3, kind='dalmatian'),
    4: Dog(name='Pongo', pk=4, kind='dalmatian'),
    5: Dog(name='Tillman', pk=5, kind='bulldog'),
    6: Dog(name='Uga', pk=6, kind='bulldog')
}

post_db = [
    Timestamp(id=0, timestamp=12),
    Timestamp(id=1, timestamp=10)
]


@app.get('/')
def root():
    return "root"


@app.post("/post", response_model=Timestamp)
def get_post():
    # TODO: В идеале инкремент должен быть атомарный, для конкурентной целостности
    new_id = post_db[-1].id + 1  # Эмулируем 'БД' - генерируем следующий id
    new_post = Timestamp(id=new_id, timestamp=time.time_ns())  # Создаем post с новым id, время в наносекундах
    post_db.append(new_post)
    return new_post  # Возвращаем экземпляр


@app.get("/dog", response_model=list[Dog])
def get_dogs(dog_type: DogType = None):
    dogs = dogs_db.values()  # Берем все значения из БД
    if dog_type:  # Если задан фильтр - по типу - применяем его
        dogs = [dog for dog in dogs_db.values() if dog.kind == dog_type]
    return list(dogs)


@app.post("/dog", response_model=Dog)
def create_dog(new_dog: Dog):
    # TODO: В идеале инкремент должен быть атомарный, для конкурентной целостности
    pk = max(dogs_db.keys()) + 1  # Эмулируем 'БД' - генерируем автоинкрементный pk
    new_dog.pk = pk  # Переписываем pk собаки
    dogs_db[pk] = new_dog  # Сохраняем собаку в 'БД'
    return new_dog


@app.get("/dog/{pk}", response_model=Dog)
def get_dog_by_pk(pk: int):
    if pk in dogs_db:
        return dogs_db[pk]
    # Если не найдена собака - возвращаем 404, хотя такая ошибка не задукоментирована в swagger
    raise HTTPException(status_code=404, detail="Dog not found")


@app.patch("/dog/{pk}", response_model=Dog)
def update_dog(pk: int, dog: Dog):
    # TODO: Возможно, стоит добавить проверку pk == dog.id
    if pk in dogs_db:
        updating_dog = dogs_db[pk]
        updating_dog.name = dog.name
        updating_dog.kind = dog.kind
        return updating_dog
    # Если не найдена собака - возвращаем 404, хотя такая ошибка не задокументирована в swagger
    raise HTTPException(status_code=404, detail="Dog not found")
