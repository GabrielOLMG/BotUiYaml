import subprocess
import sys
from pathlib import Path

def run():
    # Localiza o home.py relativo a este arquivo de CLI
    current_file = Path(__file__).resolve()
    app_path = current_file.parent.parent / "app" / "home.py"
    
    if not app_path.exists():
        print(f"Erro: Arquivo home.py não encontrado em {app_path}")
        sys.exit(1)

    try:
        # O Streamlit precisa ser chamado via subprocesso para rodar seu servidor
        print(f"Iniciando Dashboard em: {app_path}")
        subprocess.run(["streamlit", "run", str(app_path)], check=True)
    except KeyboardInterrupt:
        print("\nEncerrando...")
    except Exception as e:
        print(f"Erro inesperado: {e}")
        sys.exit(1)