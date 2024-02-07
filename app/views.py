from typing import Type

from bson.objectid import ObjectId
from fastapi import HTTPException, Request

from schemas import ItemOut, UserOut


class View:
    collection_name: str
    schema: Type[UserOut] | Type[ItemOut]

    def __init__(self, request: Request) -> None:
        self.db = request.app.state.db

    @property
    def collection(self):
        return self.db[self.collection_name]

    def dump(self, obj) -> dict:
        data: dict = {}
        for field in self.schema.model_fields:
            if field == "id":
                v = str(obj["_id"])
            else:
                v = obj[field]
            data[field] = v
        return data

    async def list(self) -> list[dict]:
        data: list[dict] = []
        async for obj in self.collection.find():
            data.append(self.dump(obj))
        return data

    async def get(self, object_id: str) -> dict:
        obj = await self.collection.find_one({"_id": ObjectId(object_id)})
        if not obj:
            msg = f"{self.collection_name}(_id={object_id!r}) not found!"
            raise HTTPException(status_code=404, detail=msg)
        return self.dump(obj)

    async def add(self, data: dict) -> dict:
        inserted = await self.collection.insert_one(data)
        return await self.get(inserted.inserted_id)

    async def update(self, object_id: str, data: dict) -> dict:
        await self.get(object_id)
        await self.collection.update_one({"_id": ObjectId(object_id)}, {"$set": data})
        return await self.get(object_id)

    async def delete(self, object_id: str) -> None:
        await self.get(object_id)
        await self.collection.delete_one({"_id": ObjectId(object_id)})


class UserView(View):
    collection_name = "user"
    schema = UserOut


class ItemView(View):
    collection_name = "item"
    schema = ItemOut
