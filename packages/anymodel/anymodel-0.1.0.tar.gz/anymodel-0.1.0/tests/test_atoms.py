def test_create_engine():
    from sqlalchemy import create_engine

    engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")
    assert engine is not None
