# classes/playwright_driver.py
import os
import time
import subprocess


from pathlib import Path
from playwright.sync_api import sync_playwright
from BotUi.drivers.abstracts.BotDriver import BotDriver
from BotUi.config.BotConstants import MODIFIER_KEYS, PW_KEYS



class PlaywrightDriver(BotDriver):

    def __init__(self, viewport=(1920, 1080), headless=False):
        # config básica
        self.viewport = viewport
        self.headless = headless

        # lazy state (NÃO inicia nada aqui)
        self.pw = None
        self.browser = None
        self.context = None
        self.page = None

    def init(self):
        if self.browser is not None:
            return  # já iniciado

        self.pw = sync_playwright().start()

        self.browser = self.pw.chromium.launch(
            headless=self.headless,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
            ]
        )

        self.context = self.browser.new_context(
            viewport={
                "width": self.viewport[0],
                "height": self.viewport[1]
            }
        )

        self.page = self.context.new_page()

    # ---------------------- #
    # Actions
    # ---------------------- #
    def goto(self, url: str, wait_time: float = 3.0):
        try:
            self.page.goto(url, wait_until="networkidle")
            time.sleep(wait_time)
            return True
        except Exception as e:
            return False

    def reload(self):
        self.page.reload()
    
    def click(self, coord: tuple, delay_ms:int=100):
        try:
            if isinstance(coord, dict):
                x = coord.get("x")
                y = coord.get("y")
            else:
                x, y = coord

            if x is None or y is None:
                raise ValueError("[PlaywrightDriver.click] Coordenadas inválidas")

            # Garante que a página tem foco
            self.page.mouse.move(x, y)
            self.page.wait_for_timeout(delay_ms)
            self.page.mouse.click(x, y)
            return True, None
        except Exception as e:
            return False, f"[PlaywrightDriver.click] Falha ao clicar na coord {coord}: {e}"
        
    def upload_file(self, file_path: str, coord: tuple):
        try: 
            file_path = str(Path(file_path).resolve())
        except Exception as e:
            return False, f"[PlaywrightDriver.upload_file] Erro ao resolver path do arquivo '{file_path}': {e}"

        try:
            x, y = coord
        except Exception as e:
            return False, f"[PlaywrightDriver.upload_file] Coord inválida {coord}: {e}"

        try:
            with self.page.expect_file_chooser() as fc_info:
                self.click(coord=(x, y))

            file_chooser = fc_info.value
        except Exception as e:
            return False, f"[PlaywrightDriver.upload_file] Falha ao abrir file chooser: {e}"

        try:
            file_chooser.set_files(file_path)
        except Exception as e:
            return False, f"[PlaywrightDriver.upload_file] Falha ao setar arquivo '{file_path}' no file chooser: {e}"

        return True, None

    def write(self, text):
        try:
            self.page.keyboard.insert_text(text)
            return True, None
        except Exception as e:
            return False, f"[PlaywrightDriver.write] {e}"
            
    def scroll(self, direction: str, delta_x: int=0, delta_y: int=100, coord: tuple=None):
        try:
            if coord is not None:
                x, y = coord
                self.page.mouse.move(x, y)

            if direction == "UP":
                delta_y *= -1

            self.page.mouse.wheel(delta_x, delta_y)
            
            return True, None
        except Exception as e:
            return False, f"[PlaywrightDriver.scroll] {e}"
        

    def close(self):
        # 1️⃣ Tenta fechar o browser, se existir
        if self.browser is not None:
            try:
                self.browser.close()
            except Exception as e:
                print(f"[WARN] Browser já fechado ou erro ao fechar: {e}")

        # 2️⃣ Tenta parar o Playwright
        try:
            self.pw.stop()
        except Exception as e:
            print(f"[WARN] Playwright já parado ou erro ao parar: {e}")

        # 3️⃣ Kill “processos zumbis” do Playwright (Linux/Mac/Windows)
        try:
            # Busca por processos de node que são usados pelo Playwright
            if os.name == "posix":
                subprocess.run("pkill -f 'playwright'", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif os.name == "nt":
                subprocess.run('taskkill /F /IM node.exe /T', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[WARN] Erro ao matar processos zumbis do Playwright: {e}")
    
    def key_sequence(self, keys: list):
        try:
            pressed_modifiers = []

            for item in keys:
                key = item.upper()

                # Modificadores
                if key in MODIFIER_KEYS:
                    pw_key = PW_KEYS[key]
                    self.page.keyboard.down(pw_key)
                    pressed_modifiers.append(pw_key)

                # Teclas especiais
                elif key in PW_KEYS:
                    pw_key = PW_KEYS[key]
                    if pw_key == " ":
                        self.page.keyboard.type(" ")
                    else:
                        self.page.keyboard.press(pw_key)

                # Texto normal
                else:
                    self.page.keyboard.type(item)

            # Solta modificadores no final
            for mod in reversed(pressed_modifiers):
                self.page.keyboard.up(mod)

            return True, None

        except Exception as e:
            return False, f"[PlaywrightDriver.key_sequence] Falha ao executar key_sequence: {e}"

        
    # ---------------------- #
    # Gets
    # ---------------------- #
    def get_url(self):
        return self.page.url
    
    def get_screenshot(self, output_path) -> tuple:
        if not output_path.lower().endswith(".png"):
            output_path += ".png"

        data = self.page.screenshot(
            path=output_path,
        )
        
        return output_path, data