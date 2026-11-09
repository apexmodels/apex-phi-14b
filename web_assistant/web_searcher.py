"""
ApexPhi-Think Web Search & Grounding Engine.
Provides autonomous web querying, HTML content extraction, and source attribution for ApexPhi-Think-14B.
"""

import json
import logging
import re
import ssl
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger("apex_phi.web_searcher")

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 "
        "ApexPhi-Think/1.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def search_duckduckgo(query: str, max_results: int = 4) -> List[Dict[str, str]]:
    """Search DuckDuckGo using ddgs or fallback html parsing."""
    results: List[Dict[str, str]] = []
    logger.info("Executing DuckDuckGo search: %s", query)

    # 1. Try python ddgs library
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            raw = list(ddgs.text(query, max_results=max_results))
            for item in raw:
                results.append({
                    "title": item.get("title", ""),
                    "href": item.get("href", ""),
                    "body": item.get("body", "")
                })
        if results:
            return results
    except Exception as e:
        logger.warning("ddgs package search failed: %s. Falling back to direct HTML search.", e)

    # 2. Fallback: DuckDuckGo HTML endpoint
    try:
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query)}"
        req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html, "html.parser")

            for res in soup.find_all("div", class_="result", limit=max_results):
                title_elem = res.find("a", class_="result__a")
                snippet_elem = res.find("a", class_="result__snippet")
                if title_elem:
                    href = title_elem.get("href", "")
                    # Extract redirect if present
                    if "uddg=" in href:
                        match = re.search(r"uddg=([^&]+)", href)
                        if match:
                            href = urllib.parse.unquote(match.group(1))
                    results.append({
                        "title": title_elem.get_text(strip=True),
                        "href": href,
                        "body": snippet_elem.get_text(strip=True) if snippet_elem else ""
                    })
    except Exception as e:
        logger.error("DuckDuckGo HTML fallback failed: %s", e)

    return results


def fetch_page_text(url: str, max_chars: int = 4000) -> Dict[str, Any]:
    """Fetch URL and extract clean readability text and main paragraphs."""
    if not url.startswith("http://") and not url.startswith("https://"):
        return {"url": url, "title": "Invalid URL", "content": "", "status": "error"}

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
        with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" not in content_type and "text/plain" not in content_type:
                return {"url": url, "title": "Skipped Non-HTML", "content": "", "status": "skipped"}

            html = resp.read().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html, "html.parser")

            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "svg", "noscript", "iframe"]):
                tag.decompose()

            title = soup.title.string.strip() if soup.title and soup.title.string else url

            # Extract main text
            paragraphs = []
            for p in soup.find_all(["p", "article", "section", "h1", "h2", "h3", "li"]):
                txt = p.get_text(strip=True)
                if len(txt) > 25:
                    paragraphs.append(txt)

            content = "\n\n".join(paragraphs)
            if len(content) > max_chars:
                content = content[:max_chars] + "\n...[truncated]..."

            return {
                "url": url,
                "title": title,
                "content": content,
                "status": "success"
            }
    except Exception as e:
        logger.warning("Could not fetch page %s: %s", url, e)
        return {"url": url, "title": "Error", "content": "", "status": "failed", "error": str(e)}


def perform_grounded_web_research(query: str, max_pages: int = 2) -> Dict[str, Any]:
    """Autonomous search and scraping pipeline returning synthesized source context."""
    search_hits = search_duckduckgo(query, max_results=max_pages + 2)
    sources = []
    combined_context = []

    valid_hits = [h for h in search_hits if h.get("href")]
    for idx, hit in enumerate(valid_hits[:max_pages], 1):
        url = hit["href"]
        title = hit.get("title", f"Source {idx}")
        snippet = hit.get("body", "")

        page_res = fetch_page_text(url, max_chars=3000)
        detailed_text = page_res.get("content") or snippet

        source_entry = {
            "id": idx,
            "title": title,
            "url": url,
            "snippet": snippet,
            "preview": detailed_text[:600]
        }
        sources.append(source_entry)
        combined_context.append(
            f"[Source {idx}]: {title}\nURL: {url}\nContent:\n{detailed_text}\n"
        )

    context_str = "\n".join(combined_context)
    return {
        "query": query,
        "sources": sources,
        "context_text": context_str
    }
