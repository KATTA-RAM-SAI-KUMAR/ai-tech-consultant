
import re

from sentence_transformers import SentenceTransformer
from sqlalchemy import delete, select

from app.database import SessionLocal
from app.models import Article, DocumentChunk, EMBEDDING_DIMENSIONS


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def split_into_chunks(content: str) -> list[str]:
    """Split article text into overlapping, character-based chunks."""
    content = re.sub(r"\n{3,}", "\n\n", content).strip()
    chunks = []
    start = 0

    while start < len(content):
        end = min(start + CHUNK_SIZE, len(content))
        chunk = content[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(content):
            break

        start = end - CHUNK_OVERLAP

    return chunks


def main() -> None:
    model = SentenceTransformer(MODEL_NAME)

    dimension = model.get_sentence_embedding_dimension()
    if dimension != EMBEDDING_DIMENSIONS:
        raise ValueError(
            f"Model dimension {dimension} does not match "
            f"database dimension {EMBEDDING_DIMENSIONS}"
        )

    with SessionLocal() as session:
        articles = session.scalars(
            select(Article).where(Article.active.is_(True))
        ).all()

        total_chunks = 0

        for article in articles:
            chunks = split_into_chunks(article.content)

            if not chunks:
                print(f"Skipping empty article: {article.title}")
                continue

            vectors = model.encode(
                chunks,
                normalize_embeddings=True,
                show_progress_bar=False,
            )

            # Replace existing chunks so reruns don't duplicate them.
            session.execute(
                delete(DocumentChunk).where(
                    DocumentChunk.article_id == article.id
                )
            )

            for index, (chunk, vector) in enumerate(
                zip(chunks, vectors)
            ):
                session.add(
                    DocumentChunk(
                        article_id=article.id,
                        chunk_index=index,
                        text=chunk,
                        embedding=vector.tolist(),
                    )
                )

            session.commit()
            total_chunks += len(chunks)
            print(f"Indexed {len(chunks)} chunks: {article.title}")

        print(f"\nEmbedding complete. Total chunks: {total_chunks}")


if __name__ == "__main__":
    main()
