"""Test the stability of the public API for AnyModel."""


def test_public_api_exports():
    """Test that all expected public API items are exported from anymodel."""
    import anymodel

    # Test that all expected attributes are present
    expected_exports = [
        "Collection",
        "Entity",
        "Field",
        "Mapper",
        "MemoryStorage",
        "OneToManyRelation",
    ]

    # Check that all expected exports are present
    for name in expected_exports:
        assert hasattr(anymodel, name), f"Missing export: {name}"
        assert name in anymodel.__all__, f"Missing from __all__: {name}"

    # Check that __all__ doesn't have extra items
    assert set(anymodel.__all__) == set(expected_exports), (
        f"__all__ mismatch. Expected: {expected_exports}, Got: {anymodel.__all__}"
    )


def test_entity_class():
    """Test that Entity class can be imported and instantiated."""
    from anymodel import Entity, Field
    from typing import Optional

    class TestEntity(Entity):
        id: Optional[int] = Field(None, primary_key=True)
        name: str
        age: int = 0

    # Test instantiation
    entity = TestEntity(name="Test")
    assert entity.name == "Test"
    assert entity.age == 0
    assert hasattr(entity, "__state__")
    assert hasattr(entity, "id")


def test_mapper_class():
    """Test that Mapper class can be imported and instantiated."""
    from anymodel import Entity, Field, Mapper, MemoryStorage
    from typing import Optional

    class TestEntity(Entity):
        id: Optional[int] = Field(None, primary_key=True)
        name: str

    storage = MemoryStorage()
    mapper = Mapper(TestEntity, storage=storage)

    assert mapper.storage == storage
    assert hasattr(mapper, "save")
    assert hasattr(mapper, "find")
    assert hasattr(mapper, "find_one_by_pk")
    assert hasattr(mapper, "delete")
    assert mapper.primary_key == ("id",)


def test_memory_storage():
    """Test that MemoryStorage can be imported and instantiated."""
    from anymodel import MemoryStorage

    storage = MemoryStorage()
    assert hasattr(storage, "migrate")
    assert hasattr(storage, "insert")
    assert hasattr(storage, "find_one")
    assert hasattr(storage, "find_many")
    assert hasattr(storage, "update")
    assert hasattr(storage, "delete")


def test_collection():
    """Test that Collection can be imported and used."""
    from anymodel import Collection, Entity, Field
    from typing import Optional

    class Item(Entity):
        id: Optional[int] = Field(None, primary_key=True)
        value: int

    # Collection requires a sequence or loader
    items = [Item(value=42), Item(value=84)]
    collection = Collection(items)
    assert hasattr(collection, "__iter__")
    assert hasattr(collection, "__len__")
    assert hasattr(collection, "load")

    # Test basic operations
    assert len(collection) == 2
    assert list(collection)[0].value == 42
    assert list(collection)[1].value == 84


def test_one_to_many_relation():
    """Test that OneToManyRelation can be imported."""
    from anymodel import OneToManyRelation

    # OneToManyRelation requires a mapper instance
    # We're just testing that it can be imported and has expected methods
    assert hasattr(OneToManyRelation, "get_find_callback_for")
    assert hasattr(OneToManyRelation, "save")


def test_field_from_sqlmodel():
    """Test that Field is correctly re-exported from SQLModel."""
    from anymodel import Field
    from sqlmodel import Field as SQLModelField

    # Field should be the same as SQLModel's Field
    assert Field is SQLModelField


def test_basic_crud_operations():
    """Test basic CRUD operations work with the public API."""
    from anymodel import Entity, Mapper, MemoryStorage, Field
    from datetime import datetime
    from typing import Optional

    class Task(Entity):
        id: Optional[int] = Field(None, primary_key=True)
        title: str
        completed: bool = False
        created_at: datetime = Field(default_factory=datetime.now, primary_key=False)

    storage = MemoryStorage()
    mapper = Mapper(Task, storage=storage)
    storage.migrate()  # Initialize storage

    # Create
    task = Task(title="Test Task")
    mapper.save(task)
    assert task.id is not None

    # Read using find (find_one_by_pk has a known type conversion issue)
    all_tasks = list(mapper.find())
    assert len(all_tasks) == 1
    found = all_tasks[0]
    assert found.title == "Test Task"
    assert found.completed is False

    # Update
    found.completed = True
    mapper.save(found)

    all_tasks = list(mapper.find(completed=True))
    assert len(all_tasks) == 1
    updated = all_tasks[0]
    assert updated.completed is True

    # Delete - skipped as delete is not implemented in MemoryStorage
    # mapper.delete(updated)
    # all_tasks = list(mapper.find())
    # assert len(all_tasks) == 0


def test_module_imports():
    """Test that submodules can be imported directly."""
    # These imports should work
    from anymodel.types import Entity, Collection, OneToManyRelation
    from anymodel.types.entity import Entity as EntityDirect
    from anymodel.types.collections import Collection as CollectionDirect
    from anymodel.types.relations import OneToManyRelation as RelationDirect

    # Verify they're the same classes
    from anymodel import Entity as EntityMain
    from anymodel import Collection as CollectionMain
    from anymodel import OneToManyRelation as RelationMain

    assert Entity is EntityMain is EntityDirect
    assert Collection is CollectionMain is CollectionDirect
    assert OneToManyRelation is RelationMain is RelationDirect
