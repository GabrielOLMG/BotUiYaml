from pathlib import Path

from playwright.sync_api import sync_playwright

def get_page( viewport=(1920, 1080)):
    pw = sync_playwright().start()

    browser = pw.chromium.launch(
        headless=False,
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

def write_input(page, text):
    try:
        page.bring_to_front()

        # injeta texto no clipboard
        page.evaluate(
            """
            async (text) => {
                await navigator.clipboard.writeText(text);
            }
            """,
            text,
        )

        # cola (Ctrl+V ou Cmd+V)
        if page.evaluate("navigator.platform").startswith("Mac"):
            page.keyboard.press("Meta+V")
        else:
            page.keyboard.press("Control+V")

        return True, None
    except Exception as e:
        return False, e


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

def upload_file(page, file_path, coord):
    """
    page: Playwright Page
    file_path: caminho do ficheiro
    coord: [x, y] ou (x, y) do botão Upload
    """
    try: 
        file_path = str(Path(file_path).resolve())
        x, y = coord

        with page.expect_file_chooser() as fc_info:
            click_coord(page, (x, y))

        file_chooser = fc_info.value
        file_chooser.set_files(file_path)
        return True, None
    except Exception as e:
        return False, e

def get_screenshot(page, output_path):
    if not output_path.lower().endswith(".png"):
        output_path += ".png"

    page.screenshot(
        path=output_path,
        #full_page=True
    )
    return output_path

# ---------------------- #
# SCROLLs
# ---------------------- #
def drag_vertical(page, coord=None, direction="DOWN", delta_y=100, delta_x=0):
    if coord is not None:
        x, y = coord
        page.mouse.move(x, y)

    if direction == "UP":
        delta_y *= -1

    page.mouse.wheel(delta_x, delta_y)

def is_at_page_edge(page, at_end: bool=True) -> bool:
    """
    Verifica se a página está no início (at_end=False)
    ou no fim (at_end=True)
    """
    return page.evaluate(
        """
        (atEnd) => {
            const scrollTop = window.scrollY || document.documentElement.scrollTop;
            const viewportHeight = window.innerHeight;
            const scrollHeight = document.documentElement.scrollHeight;

            if (atEnd) {
                return scrollTop + viewportHeight >= scrollHeight - 1;
            }
            return scrollTop <= 0;
        }
        """,
        at_end
    )

def scroll_until_edge(
    page,
    direction: str,
    delta: int = 1500,
    max_idle: int = 3,
    pause_ms: int = 80,
):
    """
    Scroll adaptativo até o topo ou fundo da página.

    direction:
        "DOWN" -> vai até o fim
        "UP"   -> vai até o topo
    """

    if direction not in ("UP", "DOWN"):
        raise ValueError("direction must be 'UP' or 'DOWN'")

    wheel_delta = delta if direction == "DOWN" else -delta
    idle_count = 0
    last_position = None

    while True:
        page.mouse.wheel(0, wheel_delta)
        page.wait_for_timeout(pause_ms)

        try:
            current_position = page.evaluate("window.scrollY")
        except Exception:
            # Flutter pode bloquear acesso ao scroll global
            break

        if current_position == last_position:
            idle_count += 1
        else:
            idle_count = 0

        if idle_count >= max_idle:
            break

        last_position = current_position
