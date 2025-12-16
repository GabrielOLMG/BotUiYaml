import time
import os
from tqdm import tqdm
import platform
import shutil

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import MoveTargetOutOfBoundsException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager


def get_driver():
    chromium_path = shutil.which("chromium-browser") or shutil.which("chromium")
    chromedriver_path = shutil.which("chromedriver")

    if not chromium_path:
        raise RuntimeError("❌ Chromium não encontrado. Instale com: sudo apt install -y chromium-browser")
    if not chromedriver_path:
        raise RuntimeError("❌ ChromeDriver não encontrado. Instale com: sudo apt install -y chromium-chromedriver")

    options = Options()
    options.binary_location = chromium_path
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions")
    options.add_argument("--remote-debugging-port=0")  # 👈 evita DevToolsActivePort bug
    options.add_argument("--window-size=1920,1080")

    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def finish_driver(driver):
    if driver is not None:
        driver.quit()
    else:
        print("⚠️ Nenhum driver ativo para encerrar.")




def get_screenshot(driver, output_path):
    if not output_path.lower().endswith(".png"):
        output_path += ".png"
    driver.save_screenshot(output_path)
    return output_path

def write_input(driver, text):
    result = driver.execute_script("""
        const el = document.activeElement;
        if (!el) return 'no_active';
        try {
            el.value = arguments[0];
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            return 'ok';
        } catch (e) {
            return e.toString();
        }
    """, text)
    
    if result != 'ok':
        _write_input(driver, text)


def _write_input(driver, text, delay=0.005, block_size=20):
    lines = text.split('\n')
    total_blocks = range(0, len(lines), block_size)

    for i in tqdm(total_blocks, desc="Digitando texto no campo", unit="bloco"):
        block = '\n'.join(lines[i:i+block_size])
        actions = ActionChains(driver)
        actions.send_keys(block)

        # adiciona ENTER se não for o último bloco
        if i + block_size < len(lines):
            actions.send_keys(Keys.ENTER)

        actions.pause(delay)
        actions.perform()


def drag_vertical(driver, coord=None, direction="DOWN", delta_y=100, delta_x=0):
    if direction=="UP":
        delta_y*=-1
    params = {
        "type": "mouseWheel",
        "x": coord[0],
        "y": coord[1],
        "deltaX": delta_x,
        "deltaY": delta_y,
        "modifiers": 0,
        "clickCount": 0
    }
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", params)

    
    params_move = {
        "type": "mouseMoved",
        "x": 0,
        "y": 0,
        "modifiers": 0,
    }
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", params_move)



def click_coord(driver, coords):
    x, y = coords

    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mousePressed",
        "x": x,
        "y": y,
        "button": "left",
        "clickCount": 1
    })

    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mouseReleased",
        "x": x,
        "y": y,
        "button": "left",
        "clickCount": 1
    })

def upload_file(page, file_path):
    print("NOT WORKING!")
    raise RuntimeError("Upload File is not working, wait!")



from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def wait_for_flutter_ready(driver, timeout=30):
    """
    Aguarda até o contêiner principal do Flutter Web ser renderizado.
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "flt-glass-pane"))
        )
        return True
    except Exception:
        return False
