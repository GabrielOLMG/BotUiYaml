from playwright.sync_api import sync_playwright
import time

URL = "https://staging.aiceblock.eu"
OUTPUT_FILE = "print.png"

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,   # 👈 IMPORTANTE
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
        ]
    )

    page = browser.new_page(
        viewport={"width": 1280, "height": 800}
    )

    # Para SPA / Flutter Web, 'load' é mais confiável
    page.goto(URL, wait_until="load")

    # Flutter Web precisa de tempo real para renderizar o canvas
    time.sleep(5)

    page.screenshot(
        path=OUTPUT_FILE,
        full_page=True
    )

    browser.close()

print(f"Screenshot salvo em {OUTPUT_FILE}")
