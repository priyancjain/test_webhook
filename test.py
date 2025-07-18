from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://playaebikes.com/faq/", timeout=60000)
    html = page.content()
    browser.close()

    with open("faq_page.html", "w", encoding="utf-8") as f:
        f.write(html)

print("HTML saved to faq_page.html ✅")
