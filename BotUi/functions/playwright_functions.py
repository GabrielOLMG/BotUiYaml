from playwright.sync_api import sync_playwright

def get_page( viewport=(1920, 1080)):
    pw = sync_playwright().start()

    browser = pw.chromium.launch(
        headless=False,   # 👈 IMPORTANTE
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
        ]
    )

    context = browser.new_context(
        viewport={"width": viewport[0], "height": viewport[1]}
    )

    page = context.new_page()
    return pw, browser, page



def finish_page(pw, browser):
    """
    Finaliza corretamente Playwright.
    """
    try:
        browser.close()
    finally:
        pw.stop()

def write_input(page, text, delay_ms=None):
    """
    Escreve texto no elemento atualmente focado.
    Compatível com Flutter Web (canvas).
    """

    # Garante que a página tem foco
    page.bring_to_front()

    # Digitação real (evento de teclado)
    if delay_ms:
        page.keyboard.type(text, delay=delay_ms)
    else:
        page.keyboard.type(text)


def click_coord(page, object_coord, delay_ms=100):
    """
    Clica numa coordenada absoluta da viewport.
    Funciona com Flutter Web (canvas).
    """

    if isinstance(object_coord, dict):
        x = object_coord.get("x")
        y = object_coord.get("y")
    else:
        x, y = object_coord

    if x is None or y is None:
        raise ValueError("Coordenadas inválidas")

    # Garante que a página tem foco
    page.mouse.move(x, y)
    page.wait_for_timeout(delay_ms)
    page.mouse.click(x, y)

from pathlib import Path

def upload_file(page, file_path, coord):
    """
    page: Playwright Page
    file_path: caminho do ficheiro
    coord: [x, y] ou (x, y) do botão Upload
    """
    print("ready to u[pload")
    file_path = str(Path(file_path).resolve())
    x, y = coord

    with page.expect_file_chooser() as fc_info:
        click_coord(page, (x, y))

    file_chooser = fc_info.value
    file_chooser.set_files(file_path)
