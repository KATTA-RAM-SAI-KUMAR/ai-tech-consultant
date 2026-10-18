
from sqlalchemy import text

from app.database import Base, engine
from app.models import Article, DocumentChunk  # noqa: F401


def initialize_database() -> None:
    with engine.begin() as connection:
        connection.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector")
        )

    Base.metadata.create_all(bind=engine)

    print("Database initialized successfully.")
    print("Tables: articles, document_chunks")


if __name__ == "__main__":
    initialize_database()
