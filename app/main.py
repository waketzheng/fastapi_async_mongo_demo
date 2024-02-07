import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi_cdn_host import monkey_patch_for_docs_ui
from loguru import logger

from db import database
from schemas import ItemCreate, ItemOut, ItemUpdate, UserCreate, UserOut, UserUpdate
from utils import get_ip
from views import ItemView, UserView


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = database
    logger.remove()
    logger.add(sys.stdout, level=os.getenv("LOG_LEVEL", "info").upper())
    logger.info(f"Using db: {database.name}")
    yield


app = FastAPI(lifespan=lifespan)
monkey_patch_for_docs_ui(app)


@app.get("/users", response_model=list[UserOut])
async def user_list(request: Request) -> list[dict]:
    return await UserView(request).list()


@app.post("/users", response_model=UserOut)
async def create_user(request: Request, user_in: UserCreate) -> dict:
    return await UserView(request).add(user_in.model_dump())


@app.get("/users/{user_id}", response_model=UserOut)
async def user_data(request: Request, user_id: str) -> dict:
    return await UserView(request).get(user_id)


@app.patch("/users/{user_id}", response_model=UserOut)
async def update_user(request: Request, user_id: str, user_in: UserUpdate) -> dict:
    return await UserView(request).update(
        user_id, user_in.model_dump(exclude_unset=True)
    )


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(request: Request, user_id: str) -> None:
    await UserView(request).delete(user_id)


@app.get("/items", response_model=list[ItemOut])
async def item_list(request: Request) -> list[dict]:
    return await ItemView(request).list()


@app.post("/items", response_model=ItemOut)
async def create_item(request: Request, item_in: ItemCreate) -> dict:
    return await ItemView(request).add(item_in.model_dump())


@app.get("/items/{item_id}", response_model=ItemOut)
async def item_data(request: Request, item_id: str) -> dict:
    return await ItemView(request).get(item_id)


@app.patch("/items/{item_id}", response_model=ItemOut)
async def update_item(request: Request, item_id: str, item_in: ItemUpdate) -> dict:
    return await ItemView(request).update(
        item_id, item_in.model_dump(exclude_unset=True)
    )


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(request: Request, item_id: str) -> None:
    await ItemView(request).delete(item_id)


def runserver() -> None:
    """This is for debug mode to start server. For prod, use supervisor+gunicorn/uvicorn instead."""
    from pathlib import Path

    import uvicorn

    host_allow_all = "0.0.0.0"
    host, port = os.getenv("APP_HOST", host_allow_all), 8000
    if sys.argv[1:] and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    app_name = Path(__file__).stem + ":app"
    docs_tip = f"API Document:\n    http://127.0.0.1:{port}/docs\n"
    if host == host_allow_all:
        if (ip := get_ip()) != "127.0.0.1":
            docs_tip += f"    http://{ip}:{port}/docs"
    print(docs_tip)
    uvicorn.run(app_name, host=host, port=port, reload=True)


if __name__ == "__main__":
    runserver()
