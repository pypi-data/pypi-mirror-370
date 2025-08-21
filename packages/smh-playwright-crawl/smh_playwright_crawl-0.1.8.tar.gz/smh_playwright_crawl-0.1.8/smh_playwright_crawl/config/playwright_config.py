from threading import Lock
import asyncio
import sys
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

_set_policy_once = Lock()
_policy_set = False

def set_playwright_event_loop_if_needed():
    """
    Sets WindowsSelectorEventLoopPolicy if:
    - Running on Windows
    - Python version is < 3.12
    - Policy has not already been set

    Playwright on Windows requires this policy for compatibility on Python versions before 3.12.
    """
    global _policy_set

    if (
        sys.platform.startswith("win")
        and sys.version_info < (3, 12)
        and not _policy_set
    ):
        with _set_policy_once:
            if not _policy_set:
                current_policy = asyncio.get_event_loop_policy()
                # Import here to prevent AttributeError on non-Windows platforms
                try:
                    WindowsSelectorEventLoopPolicy = asyncio.WindowsSelectorEventLoopPolicy
                except AttributeError:
                    WindowsSelectorEventLoopPolicy = None

                if WindowsSelectorEventLoopPolicy is not None and not isinstance(current_policy, WindowsSelectorEventLoopPolicy):
                    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
                    logger.info("WindowsSelectorEventLoopPolicy set for Playwright on Python < 3.12")
                else:
                    logger.debug("WindowsSelectorEventLoopPolicy already set or unavailable.")
                _policy_set = True
