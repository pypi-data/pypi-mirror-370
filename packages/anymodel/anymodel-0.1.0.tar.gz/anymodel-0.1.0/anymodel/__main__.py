from typing_extensions import Optional

from anymodel.mapper import Mapper
from anymodel.storages.sqlalchemy import SqlAlchemyStorage
from anymodel.types.entity import Entity


class Restaurant(Entity):
    id: Optional[int] = None
    name: str = ""
    address: str = ""
    phone: str = ""


class RestaurantMapper(Mapper[Restaurant]):
    __type__ = Restaurant
    __tablename__ = "restaurants"

    fields = ["name", "address", "phone"]
    primary_key = "id"


def main():
    storage = SqlAlchemyStorage("postgresql://postgres:postgres@localhost:5432")
    mapper = RestaurantMapper(storage)
    storage.migrate()
    mapper.save(Restaurant(name="test"))


if __name__ == "__main__":
    main()
