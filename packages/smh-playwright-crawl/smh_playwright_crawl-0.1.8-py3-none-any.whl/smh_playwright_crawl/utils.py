from urllib.parse import urljoin,urlparse
import tldextract
from pathlib import Path

def is_valid_link(href: str) -> bool:
    if not href or not isinstance(href, str):
        return False
    h = href.strip().lower()
    nones = {"", "#", "/", "about:blank", "about:", "./", ".", ".."}
    if h in nones:
        return False
    if h.startswith(("#", "javascript:", "mailto:", "tel:", "data:", "void(", "ftp:")):
        return False
    if h.startswith("//"):
        parser = urlparse("http:" + h)
        if parser.scheme not in ("http", "https"):
            return False
    return True


def count_tokens(text: str) -> int:
    return len(text) // 4

def word_counter(text: str) -> int:
    return len(text.split())

tld = tldextract.TLDExtract(cache_dir=str(Path.home() / ".tld_cache"))
extract_domain = lambda u: tld(u).registered_domain