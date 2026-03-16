from playwright.sync_api import sync_playwright
"""
Helper script for creating a saved login session for bizi.si.

Run this script once, log in manually in the browser,
and the login session will be saved to `bizi_state.json`.

The scraper can then reuse this session to access
authenticated pages without logging in again.
"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.bizi.si/prijava/")

    print("Ročno se prijavi, potem pritisni Enter v terminalu...")
    input()

    context.storage_state(path="bizi_state.json")
    browser.close()
    print(context.storage_state)
