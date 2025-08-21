import argparse
import json
from .crawler import Seed, crawl
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

def main():
    parser = argparse.ArgumentParser(
        description="Async Playwright web crawler")
    parser.add_argument("url", help="Starting URL to crawl")
    parser.add_argument("--request-timeout", type=int, default=30000,
                        help="Request timeout in milliseconds (default: 30000)")
    parser.add_argument("--max-tabs", type=int, default=15,
                        help="Maximum number of tabs to open concurrently (default: 15)")
    # Headless by default, user can use --no-headless to show the browser
    try:
        # Python 3.9+ only (best style)
        parser.add_argument("--headless", action=argparse.BooleanOptionalAction,
                            default=True, help="Run browser headless (default: True)")
    except AttributeError:
        # Fallback for Python <3.9
        parser.add_argument("--headless", dest="headless", action="store_true",
                            help="Run browser in headless mode (default)")
        parser.add_argument("--no-headless", dest="headless",
                            action="store_false", help="Run browser with UI")
        parser.set_defaults(headless=True)
    parser.add_argument("--output", type=str,
                        default="crawl_results.json", help="Output file")
    args = parser.parse_args()
    
    logger.info(f"Starting crawl with seed URL: {args.url}")

    import asyncio
    seed = Seed(
        url=args.url,
        headless=args.headless,
        request_timeout=args.request_timeout,
        max_tabs=args.max_tabs
    )
    results = asyncio.run(crawl(seed))

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    logger.info(f"Wrote {len(results)} pages to {args.output}")


if __name__ == "__main__":
    main()
