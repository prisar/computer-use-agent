import base64
from playwright.async_api import async_playwright

from google.genai import types

_ctx: dict = {"pw": None, "browser": None, "page": None}


async def _reset_ctx() -> None:
    """Tear down any stale browser context."""
    if _ctx["pw"] is not None:
        try:
            await _ctx["pw"].stop()
        except Exception:
            pass
    _ctx["pw"] = None
    _ctx["browser"] = None
    _ctx["page"] = None


async def _page():
    """Return the active Playwright page, relaunching if the browser/page has crashed."""
    # Check for a stale context and reset if needed.
    if _ctx["browser"] is not None:
        crashed = False
        try:
            if not _ctx["browser"].is_connected():
                crashed = True
            elif _ctx["page"] is None or _ctx["page"].is_closed():
                crashed = True
        except Exception:
            crashed = True

        if crashed:
            await _reset_ctx()

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


async def browser_click_element(selector: str) -> dict:
    """Click on an element specified by a CSS selector.

    Args:
        selector: The CSS selector of the element to click (e.g. 'button#submit').
    """
    p = await _page()
    await p.click(selector)
    return {"clicked_selector": selector}


async def browser_type_element(selector: str, text: str) -> dict:
    """Type text into an element specified by a CSS selector.

    Args:
        selector: The CSS selector of the input field.
        text: The text to type.
    """
    p = await _page()
    await p.fill(selector, text)
    return {"typed": text, "selector": selector}


async def browser_wait_for(selector: str, timeout_ms: int = 5000) -> dict:
    """Wait for an element to appear in the DOM.

    Args:
        selector: The CSS selector to wait for.
        timeout_ms: Timeout in milliseconds (default 5000).
    """
    p = await _page()
    await p.wait_for_selector(selector, timeout=timeout_ms)
    return {"waited_for": selector}


async def browser_get_elements(selector: str = "button, a, input, [role='button']") -> dict:
    """Get a list of interactive elements on the page with their text and coordinates.

    Args:
        selector: The CSS selector to find elements (default: common interactive elements).
    """
    p = await _page()
    elements = await p.query_selector_all(selector)
    results = []
    for el in elements:
        if await el.is_visible():
            box = await el.bounding_box()
            text = await el.inner_text()
            if box:
                results.append({
                    "text": text.strip(),
                    "x": box["x"] + box["width"] / 2,
                    "y": box["y"] + box["height"] / 2,
                    "selector": selector,
                    "box": box
                })
    return {"elements": results[:50]}  # limit to 50 for context efficiency
