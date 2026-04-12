from google.adk.agents import Agent

from .tools import (
    browser_screenshot,
    browser_navigate,
    browser_click,
    browser_type,
    browser_press_key,
    browser_scroll,
    browser_get_text,
    browser_click_element,
    browser_type_element,
    browser_wait_for,
    browser_get_elements,
)

root_agent = Agent(
    name="computer_use_agent",
    model="gemini-2.5-flash",
    description="Controls a web browser to complete tasks on behalf of the user.",
    instruction=(
        "You are a computer use agent that controls a web browser with a 1280x720 viewport.\n"
        "Workflow:\n"
        "1. Call browser_screenshot to see the current state of the screen.\n"
        "2. Alternatively, use browser_get_elements to get a list of interactive elements and their text/coordinates.\n"
        "3. Decide the next action based on what you see.\n"
        "4. Execute the action using the appropriate tool. Prefer selector-based tools (browser_click_element, browser_type_element) for reliability if you know the selector.\n"
        "5. Call browser_screenshot again to verify the result.\n"
        "6. Repeat until the task is complete.\n\n"
        "Use browser_navigate to open URLs.\n"
        "Use browser_click for pixel-based clicking when selectors are unavailable.\n"
        "Use browser_click_element with a CSS selector for reliable clicking.\n"
        "Use browser_type to enter text after clicking.\n"
        "Use browser_type_element to fill form fields by selector.\n"
        "Use browser_wait_for when you expect a page transition or an element to appear.\n"
        "Use browser_get_elements to discover interactive elements.\n"
        "Use browser_press_key for keys like Enter, Tab, Escape.\n"
        "Use browser_scroll to scroll up or down.\n"
        "Use browser_get_text when you need to read page content as plain text."
    ),
    tools=[
        browser_screenshot,
        browser_navigate,
        browser_click,
        browser_type,
        browser_press_key,
        browser_scroll,
        browser_get_text,
        browser_click_element,
        browser_type_element,
        browser_wait_for,
        browser_get_elements,
    ],
)
