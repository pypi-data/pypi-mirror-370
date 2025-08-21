import asyncio
import re
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator, List, Dict, Set
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page

from .utils import is_valid_link, count_tokens, word_counter, extract_domain
from .config.playwright_config import set_playwright_event_loop_if_needed

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


@asynccontextmanager
async def browser_context_manager(headless: bool = True) -> AsyncIterator[Browser]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless, args=["--disable-dns-prefetch"])
        try:
            yield browser
        finally:
            await browser.close()


@dataclass
class CrawlItem:
    url: str


async def fetch_page(page: Page, url: str, request_timeout: int) -> str:
    skip_exts = {"pdf", "jpg", "jpeg", "png", "gif", "svg",
                 "doc", "docx", "xls", "xlsx", "zip", "rar", "tar", "gz"}
    ext = urlparse(url).path.lower().split(".")[-1]
    if ext in skip_exts:
        logger.info(f"Skipping non-HTML resource: {url}")
        return ""
    await page.goto(url, timeout=request_timeout, wait_until="domcontentloaded")
    return await page.content()


async def parse_links(html: str, base_url: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        raw_href = a["href"]
        if not is_valid_link(raw_href):
            continue
        resolved = urljoin(base_url, raw_href)
        parsed = urlparse(resolved)
        if parsed.scheme not in ("http", "https"):
            continue
        url_wo_frag = resolved.split('#')[0]
        if not is_valid_link(url_wo_frag):
            continue
        links.append({"text": a.get_text(strip=True), "url": url_wo_frag})
    return links


async def visit_url(context, item: CrawlItem, base_domain: str, request_timeout: int) -> Any:
    page = await context.new_page()
    try:
        html = await fetch_page(page, item.url, request_timeout)
        if not html:
            return None, []
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(" ", strip=True)
        title = soup.title.string.strip() if soup.title else ""
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = (
            description_tag["content"].strip()
            if description_tag and "content" in description_tag.attrs
            else ""
        )
        headings = [h.get_text(strip=True) for h in soup.find_all(re.compile("^h[1-3]$"))]
        links = await parse_links(html, item.url)
        domain = extract_domain(item.url)
        tokens = count_tokens(text)
        word_count = word_counter(text)
        result = {
            "url": item.url,
            "title": title,
            "description": description,
            "headings": headings,
            "links": links,
            "summary": "",
            "domain": domain,
            "tokens": tokens,
            "word_count": word_count,
            "raw_text": text
        }
        # Only keep links from the same domain that have not been visited yet
        new_link_urls = [link["url"] for link in links if extract_domain(link["url"]) == base_domain]
        new_items = [CrawlItem(url) for url in new_link_urls]
        return result, new_items
    except Exception as e:
        logger.warning(f"Failed to fetch {item.url}: {e}")
        return None, []
    finally:
        await page.close()


@dataclass
class Seed:
    url: str
    headless: bool = True
    request_timeout: int = 30000
    max_tabs: int = 15


async def crawl(seed: Seed) -> List[Dict[str, Any]]:
    set_playwright_event_loop_if_needed()
    visited: Set[str] = set()
    visited_lock = asyncio.Lock()
    results: List[Dict] = []
    queue: List[CrawlItem] = [CrawlItem(seed.url)]
    base_domain = extract_domain(seed.url)

    async with browser_context_manager(headless=seed.headless) as browser:
        context = await browser.new_context()
        while queue:
            # Pop a batch of URLs
            batch, queue = queue[:seed.max_tabs], queue[seed.max_tabs:]
            async with visited_lock:
                for item in batch:
                    visited.add(item.url)

            tasks = [visit_url(context, item, base_domain, seed.request_timeout) for item in batch]
            results_and_new = await asyncio.gather(*tasks)
            for res, new_items in results_and_new:
                if res:
                    results.append(res)
                for new_item in new_items:
                    async with visited_lock:
                        if new_item.url not in visited:
                            visited.add(new_item.url)
                            queue.append(new_item)
        await context.close()
    return results


async def crawl_multiple(seeds: List[Seed]) -> List[Dict[str, Any]]:
    tasks = [asyncio.create_task(crawl(seed)) for seed in seeds]
    all_results = [r for res in await asyncio.gather(*tasks) for r in res]
    return all_results