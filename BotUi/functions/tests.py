def test_driver(driver, verbose: bool = False) -> bool:
    """
    Testa se o driver Selenium está funcional.

    ✅ Tenta abrir uma página simples (Google)
    ✅ Verifica se o título foi carregado corretamente
    🚫 Se falhar, captura o erro e retorna False

    Args:
        driver: instância ativa de webdriver (Chrome, Firefox, etc)
        verbose: se True, imprime mensagens no console

    Returns:
        bool: True se o driver estiver funcional, False caso contrário
    """
    test_url = "https://www.google.com"
    try:
        driver.get(test_url)
        title = driver.title.strip()
        if title:
            if verbose:
                print(f"✅ Driver funcional. Página carregada: '{title}'")
            return True
        else:
            if verbose:
                print("⚠️ Driver abriu a página mas não retornou título — pode estar em modo headless incorreto.")
            return False
    except Exception as e:
        if verbose:
            print(f"❌ Driver falhou no teste: {e}")
        return False
