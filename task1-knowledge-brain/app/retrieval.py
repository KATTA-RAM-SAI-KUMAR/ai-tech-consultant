
from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Article, DocumentChunk


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model():
    return SentenceTransformer(MODEL_NAME)


def search_knowledge(question: str, top_k: int = 5) -> list[dict]:
    model = get_embedding_model()
    query_vector = model.encode(
        question,
        normalize_embeddings=True,
    ).tolist()

    distance = DocumentChunk.embedding.cosine_distance(query_vector)

    statement = (
        select(DocumentChunk, Article, distance.label("distance"))
        .join(Article, DocumentChunk.article_id == Article.id)
        .where(
            Article.active.is_(True),
            DocumentChunk.embedding.is_not(None),
        )
        .order_by(distance)
        .limit(top_k)
    )

    with SessionLocal() as session:
        rows = session.execute(statement).all()

        results = []
        for chunk, article, cosine_distance in rows:
            results.append({
                "title": article.title,
                "url": article.url,
                "snippet": chunk.text,
                "similarity": round(
                    max(0.0, min(1.0, 1.0 - float(cosine_distance))),
                    4,
                ),
            })

        return results
