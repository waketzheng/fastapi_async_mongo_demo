from pathlib import Path
from typing import TYPE_CHECKING

import motor.motor_asyncio

if TYPE_CHECKING:
    from motor.core import AgnosticClient

client: "AgnosticClient" = motor.motor_asyncio.AsyncIOMotorClient("localhost", 27017)
db_name = Path(__file__).parent.parent.name.replace("-", "_")
database = client[db_name]
