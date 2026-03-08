from google.adk.agents import Agent

from .tools import (
    browser_screenshot,
    browser_navigate,
    browser_click,
    browser_type,
    browser_press_key,
    browser_scroll,
    browser_get_text,
)

root_agent = Agent(
    name="computer_use_agent",
    model="gemini-2.0-flash",
    description="Controls a web browser to complete tasks on behalf of the user.",
    instruction=(
        "You are a computer use agent that controls a web browser with a 1280x720 viewport.\n"
        "Workflow:\n"
        "1. Call browser_screenshot to see the current state of the screen.\n"
        "2. Decide the next action based on what you see.\n"
        "3. Execute the action using the appropriate tool.\n"
        "4. Call browser_screenshot again to verify the result.\n"
        "5. Repeat until the task is complete.\n\n"
        "Use browser_navigate to open URLs.\n"
        "Use browser_click with pixel coordinates visible in the screenshot.\n"
        "Use browser_type to enter text after clicking an input field.\n"
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
    ],
)
