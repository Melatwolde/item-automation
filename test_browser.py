# test_browser.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Set headless=True later if you want no window
    page = browser.new_page()
    page.goto('https://example.com')
    print('Success! Page title:', page.title())
    # Optional: Take a screenshot as proof
    page.screenshot(path='example_success.png')
    browser.close()