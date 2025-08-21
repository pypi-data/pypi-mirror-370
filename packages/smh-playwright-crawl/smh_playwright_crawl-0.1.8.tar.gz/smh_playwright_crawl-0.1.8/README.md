# smh-playwright-crawl

**Async, multi-tab, domain-constrained web crawler using Playwright and BeautifulSoup. CLI and Python API.**

---

## Features

* Blazing fast, **concurrent** crawling with multiple browser tabs.
* Handles **JavaScript sites** using Playwright's real browsers.
* Extracts **title, description, headings, links, and text**.
* **Domain-restricted** recursive crawling—never "escapes" your target site.
* Skips duplicate, broken, and non-HTML resources.
* Usable as **command line tool** or **Python API**.

---

## Installation

```bash
pip install smh-playwright-crawl
playwright install
```

> **Important:**
> After installing, run `playwright install` in your environment to download the needed browser drivers!

---

## Quick CLI Usage

```bash
smh-playwright-crawl "https://example.com"
--max-depth 2
--headless # (default: True, runs headless)
--no-headless # (show browser window)
--request-timeout 30000
--max-tabs 10
--output output.json
```

**Example:**

```bash
smh-playwright-crawl "https://integramicro.com/" --max-depth 2 --no-headless --output site.json
```

### CLI Options

| Argument            | Default             | Description                           |
| ------------------- | ------------------- | ------------------------------------- |
| `url`               | (required)          | Seed/start URL                        |
| `--max-depth`       | 2                   | Recursion/crawl depth                 |
| `--headless`        | True                | Run browser headless (default)        |
| `--no-headless`     |                     | Show browser window                   |
| `--request-timeout` | 30000               | Timeout per page load in milliseconds |
| `--max-tabs`        | 15                  | Max concurrent browser tabs           |
| `--output`          | crawl\_results.json | Output file (JSON)                    |

---

## Python API Usage

```python
from smh_playwright_crawl import crawl
import asyncio

results = asyncio.run(crawl(
    "https://example.com",
    max_depth=2,
    headless=True, # set False to see browser
    request_timeout=30000,
    max_tabs=8
))
print("Pages crawled:", len(results))
```

**Each result:**

```json
{
  "url": "https://example.com/...",
  "title": "...",
  "description": "...",
  "headings": ["..."],
  "links": [ {"text": "...", "url": "..."} ],
  "summary": "",
  "domain": "...",
  "tokens": 234,
  "word_count": 564,
  "raw_text": "..."
}
```

---

## Requirements

* Python 3.8+ recommended
* Playwright browsers (ensure `playwright install` has been run after install)

## License

Licensed under the [Apache License 2.0](LICENSE).

---

## Responsible Use Notice

* Respect `robots.txt` and website terms of use.
* This tool is intended for legitimate, ethical, and legal use only.

---

## Author

Developed by \[S MUNI HARISH].

---

Happy (and responsible) crawling!
