
import hashlib
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import delete, select

from app.database import SessionLocal
from app.models import Article, DocumentChunk


SITEMAP_URL = (
    "https://support.brilliantdirectories.com/support/sitemap.xml"
)
ALLOWED_HOST = "support.brilliantdirectories.com"
MAX_ARTICLES = 20
REQUEST_DELAY_SECONDS = 1.0


def fetch(client: httpx.Client, url: str) -> str:
    """Fetch a URL with limited retries for transient failures."""
    for attempt in range(3):
        try:
            response = client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code not in (429, 500, 502, 503, 504):
                raise
        except httpx.RequestError:
            pass

        if attempt < 2:
            time.sleep(2 ** attempt)

    raise RuntimeError(f"Could not fetch URL after retries: {url}")


def discover_urls(client: httpx.Client) -> list[tuple[str, str | None]]:
    """Read a sitemap or sitemap index and discover article URLs."""
    discovered = []
    pending = [SITEMAP_URL]
    visited_sitemaps = set()

    while pending and len(discovered) < MAX_ARTICLES:
        sitemap_url = pending.pop(0)

        if sitemap_url in visited_sitemaps:
            continue
        visited_sitemaps.add(sitemap_url)

        try:
            xml_text = fetch(client, sitemap_url)
            root = ET.fromstring(xml_text)
        except Exception as exc:
            print(f"Sitemap error: {sitemap_url}: {exc}")
            continue

        kind = root.tag.rsplit("}", 1)[-1]

        for node in root:
            loc = node.find("{*}loc")
            lastmod = node.find("{*}lastmod")

            if loc is None or not loc.text:
                continue

            url = loc.text.strip()
            modified = lastmod.text.strip() if (
                lastmod is not None and lastmod.text
            ) else None

            if kind == "sitemapindex":
                if urlparse(url).hostname == ALLOWED_HOST:
                    pending.append(url)

            elif kind == "urlset":
                parsed = urlparse(url)
                if (
                    parsed.scheme == "https"
                    and parsed.hostname == ALLOWED_HOST
                    and url not in {item[0] for item in discovered}
                ):
                    discovered.append((url, modified))
                    if len(discovered) >= MAX_ARTICLES:
                        break

    return discovered


def extract_article(html: str) -> tuple[str, str]:
    """Extract a readable title and article body from HTML."""
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(
        ["script", "style", "nav", "footer", "header", "noscript"]
    ):
        tag.decompose()

    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    main = soup.find("main") or soup.find("article") or soup.body
    content = main.get_text("\n", strip=True) if main else ""

    if not title or len(content) < 100:
        raise ValueError("Page has no usable title or sufficient content")

    return title[:500], content


def parse_lastmod(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        return None


def crawl() -> None:
    headers = {
        "User-Agent": "AITechConsultantKnowledgeBrain/0.1 (educational crawler)"
    }

    with httpx.Client(
        headers=headers,
        timeout=20.0,
        follow_redirects=True,
    ) as client:
        urls = discover_urls(client)
        print(f"Discovered {len(urls)} article URLs.")

        with SessionLocal() as session:
            for index, (url, lastmod) in enumerate(urls, start=1):
                try:
                    time.sleep(REQUEST_DELAY_SECONDS)
                    html = fetch(client, url)
                    title, content = extract_article(html)
                    content_hash = hashlib.sha256(
                        content.encode("utf-8")
                    ).hexdigest()

                    article = session.scalar(
                        select(Article).where(Article.url == url)
                    )

                    if article and article.content_hash == content_hash:
                        article.active = True
                        print(f"[{index}/{len(urls)}] Unchanged: {title}")
                        session.commit()
                        continue

                    if article is None:
                        article = Article(
                            url=url,
                            title=title,
                            content=content,
                            content_hash=content_hash,
                            last_modified=parse_lastmod(lastmod),
                            active=True,
                        )
                        session.add(article)
                        session.flush()
                    else:
                        session.execute(
                            delete(DocumentChunk).where(
                                DocumentChunk.article_id == article.id
                            )
                        )
                        article.title = title
                        article.content = content
                        article.content_hash = content_hash
                        article.last_modified = parse_lastmod(lastmod)
                        article.active = True

                    session.commit()
                    print(f"[{index}/{len(urls)}] Saved: {title}")

                except Exception as exc:
                    session.rollback()
                    print(f"[{index}/{len(urls)}] Failed: {url}: {exc}")

    print("Crawl finished.")


if __name__ == "__main__":
    crawl()
