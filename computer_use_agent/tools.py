import base64
from playwright.async_api import async_playwright

from google.genai import types

_ctx: dict = {"pw": None, "browser": None, "page": None}


async def _page():
    if _ctx["browser"] is None:
        _ctx["pw"] = await async_playwright().start()
        _ctx["browser"] = await _ctx["pw"].chromium.launch(headless=True)
        _ctx["page"] = await _ctx["browser"].new_page(
            viewport={"width": 1280, "height": 720}
        )
    return _ctx["page"]


async def browser_screenshot() -> types.Part:
    """Take a screenshot of the current browser page and return it as an image."""
    p = await _page()
    data = await p.screenshot(type="png")
    return types.Part.from_bytes(data=data, mime_type="image/png")


async def browser_navigate(url: str) -> dict:
    """Navigate the browser to a URL.

    Args:
        url: The full URL to navigate to (e.g. https://example.com).
    """
    p = await _page()
    await p.goto(url, wait_until="domcontentloaded")
    return {"url": p.url, "title": await p.title()}


async def browser_click(x: int, y: int) -> dict:
    """Click at the specified pixel coordinates on the browser page.

    Args:
        x: Horizontal pixel coordinate.
        y: Vertical pixel coordinate.
    """
    p = await _page()
    await p.mouse.click(x, y)
    return {"clicked_at": {"x": x, "y": y}}


async def browser_type(text: str) -> dict:
    """Type text at the current focus position in the browser.

    Args:
        text: The text to type.
    """
    p = await _page()
    await p.keyboard.type(text)
    return {"typed": text}


async def browser_press_key(key: str) -> dict:
    """Press a keyboard key in the browser.

    Args:
        key: Key name such as Enter, Tab, Escape, ArrowDown, Backspace.
    """
    p = await _page()
    await p.keyboard.press(key)
    return {"pressed": key}


async def browser_scroll(direction: str, amount: int = 3) -> dict:
    """Scroll the browser page.

    Args:
        direction: 'up' or 'down'.
        amount: Number of scroll steps (default 3).
    """
    p = await _page()
    delta = amount * 120 if direction == "down" else -(amount * 120)
    await p.mouse.wheel(0, delta)
    return {"scrolled": direction, "amount": amount}


async def browser_get_text() -> dict:
    """Get the visible text content of the current browser page (first 5000 chars)."""
    p = await _page()
    text = await p.evaluate("document.body.innerText")
    return {"text": text[:5000]}
