# 🤖 BotUI — Framework de Automação de UI via YAML

**BotUI** é um framework modular para automação de interfaces gráficas (UI) utilizando **Selenium**, **OpenCV**, **OCR (Tesseract/EasyOCR)** e **YAML pipelines**.

O foco é permitir **automação visual** (baseada em imagens e texto) de aplicações web — inclusive **Flutter**, **React**, **HTML puro**, ou sistemas híbridos.

---

## 🚀 Principais Funcionalidades

- **Pipelines declarativas** em YAML  
- Suporte a **loops (`FOR_EACH`)** e **variáveis globais**  
- Detecção de elementos via **imagem (`IMG`)** ou **texto (`TEXT`)**  
- **Scroll automático** para localizar objetos fora da viewport  
- Integração com **Tesseract OCR** e **EasyOCR**  
- **Logging detalhado** com logs coloridos e arquivo persistente  
- Módulo independente (`BotActions`) com ações reutilizáveis  

---

## 📁 Estrutura de Projeto

```bash
BotUi/
├── BotUI.py                # Classe principal - coordena pipelines e execução
├── classes/
│   ├── BotActions.py       # Ações executáveis (Find, Write, Scroll, etc.)
│   └── validation_models.py
├── functions/
│   ├── selenium_functions.py
│   ├── image_functions.py
│   ├── key_map.py
│   └── utils.py
└── requirements.txt

examples/
├── images/                 # Diretório com templates de referência
├── screenshots/            # Capturas de execução
└── spaceflight_module_loop.yaml  # Exemplo de configuração YAML

setup.py # Setup do Python
setup_system.sh # Instalação necessarias
```

---

## ⚙️ Instalação

TODO


---

## 🧩 Estrutura de um YAML

Um arquivo YAML contém duas seções principais:

```yaml
config:         # Variáveis globais disponíveis em todo o pipeline
pipelines:      # Sequência de ações a executar
```



---

### ✅ Exemplo Basico

```yaml
config:
  variables:
    USERNAME: j_bauer@org.fraunhofer.pt
    PASSWORD: j_bauerpw
    MODULE_PATH: /home/user/modules/modelling.py

pipelines:
  login:
    url: http://example.com
    steps:
      - action: FIND
        object_type: IMG
        click: True
        image_path: examples/images/login_pipeline/username.png
      - action: WRITE
        text: $USERNAME
      - action: FIND
        object_type: IMG
        click: True
        image_path: examples/images/login_pipeline/password.png
      - action: WRITE
        text: $PASSWORD
      - action: FIND
        object_type: IMG
        click: True
        image_path: examples/images/login_pipeline/login_button.png
        wait: 1

  navigate_to_modules:
    steps:
     - action: FIND
       object_type: IMG
       click: True 
       image_path: $IMG_DIR/module_pipeline/module_button.png
       wait: 0.5

```

---

### ✅ Exemplo Basico com **YAML Anchors (`<<:`)**

O YAML oferece um recurso poderoso chamado anchors e aliases, que permite reutilizar blocos de configuração sem precisar copiá-los manualmente.
Isso é especialmente útil quando vários steps compartilham parâmetros comuns, como scroll, object_type, click, etc.

```yaml
config:
  variables:
    USERNAME: j_bauer@org.fraunhofer.pt
    PASSWORD: j_bauerpw
    SCROLL_PATH: examples/images/scroll.png
    IMG_DIR: examples/images
    MODULES_DIR: /home/aiceblocks/aiceblocks/developmentAmbient/modules/python/tests/pipelines/spaceflight/modules/modelling/

templates:
  # Macro para ação de scroll + clique + texto
  find_text_scroll: &find_text_scroll
    action: FIND
    object_type: TEXT
    click: True
    scroll: True
    scroll_image_path: $SCROLL_PATH

  # Macro para FIND IMG padrão
  find_img_scroll: &find_img_scroll
    action: FIND
    object_type: IMG
    click: True
    scroll: True
    scroll_image_path: $SCROLL_PATH

pipelines:
  login:
    url: http://b8-85-84-b4-e4-97.lab.fraunhofer.pt
    steps:
      - <<: *find_img_scroll
        image_path: $IMG_DIR/login_pipeline/username.png
      - action: WRITE
        text: $USERNAME
      - <<: *find_img_scroll
        image_path: $IMG_DIR/login_pipeline/password.png
        debug: True
      - action: WRITE
        text: $PASSWORD
      - <<: *find_img_scroll
        image_path: $IMG_DIR/login_pipeline/login_button.png
        wait: 1

  navigate_to_modules:
    steps:
     - action: FIND
       object_type: IMG
       click: True 
       image_path: $IMG_DIR/module_pipeline/module_button.png
       wait: 0.5

  modules_new:
    steps:
      - <<: *find_img_scroll
        image_path: $IMG_DIR/module_pipeline/new_module_button.png
        wait: 0.5
  
  modules_init:
    steps:
      - <<: *find_text_scroll
        text: "Pre-processing"
        helper: "Tenta Localizar Type"
```

No exemplo dado, usamos '&find_text_scroll' e '&find_img_scroll' para criar uma âncora — ou seja, um “modelo reutilizável” de parâmetros.

```yaml
templates:
  # Define um template (âncora) chamado "find_text_scroll"
  find_text_scroll: &find_text_scroll
    action: FIND
    object_type: TEXT
    click: True
    scroll: True
    scroll_image_path: $SCROLL_PATH
```

 Depois, podemos usar essas âncoras em qualquer parte do YAML com '<<: *find_text_scroll':
```yaml
modules_init:
  steps:
    - <<: *find_text_scroll   # importa todos os campos do template
      text: "Pre-processing"  # adiciona ou sobrescreve campos
      helper: "Tenta localizar type"

```

O operador <<: é chamado de merge key, e o *find_text_scroll é o alias, que referencia o bloco ancorado.
Quando o YAML é carregado com yaml.safe_load(), o Python já recebe o dicionário totalmente expandido — você não precisa tratar nada no código.

🧠 Vantagens principais
- 📉 Reduz duplicação e facilita manutenção;
- 🧱 Permite criar "macros" reutilizáveis (como find_img_scroll, find_text_scroll);
- 🔄 Totalmente nativo do YAML — sem necessidade de código extra em Python;

---
## Ações 

### 🔄 Ação `FOR_EACH` — Repetição dinâmica de steps

A ação FOR_EACH permite repetir blocos de steps de forma dinâmica, substituindo variáveis dentro das strings.
Isso elimina a necessidade de duplicar manualmente ações idênticas com pequenas variações.

#### 📘 Exemplo Antes De Expandir
```yaml
  generate_files:
    steps:
      - action: FOR_EACH
        loop_var: file
        items:
          - name: "modelling"
            path: "modules/modelling.py"
          - name: "training"
            path: "modules/training.py"
        steps:
          - action: FIND
            object_type: TEXT
            click: True
            text: "Add file"
            scroll: True
            scroll_image_path: examples/images/scroll.png
          - action: WRITE
            file_path: "{file.path}"
```

Neste caso:

- `loop_var: file` define o nome da variável que será usada para acessar os campos dentro de items;
- Cada item da lista em `items:` será usado para gerar uma nova sequência de steps;
- As expressões entre `{}` (ex.: `{file.path}`) serão substituídas pelos valores correspondentes.

#### 🔍 Exemplo expandido automaticamente pelo método expand_for_each()
Após a leitura do YAML e execução da expansão no Python, o bloco acima se transforma logicamente nisto:

```yaml
generate_files:
  steps:
    # Iteração 1 (file = {"name": "modelling", "path": "modules/modelling.py"})
    - action: FIND
      object_type: TEXT
      click: True
      text: "Add file"
      scroll: True
      scroll_image_path: examples/images/scroll.png

    - action: WRITE
      file_path: "modules/modelling.py"

    # Iteração 2 (file = {"name": "training", "path": "modules/training.py"})
    - action: FIND
      object_type: TEXT
      click: True
      text: "Add file"
      scroll: True
      scroll_image_path: examples/images/scroll.png

    - action: WRITE
      file_path: "modules/training.py"

```
Ou seja, o FOR_EACH é apenas uma camada sintática de conveniência.
Internamente, a classe BotUI expande esses blocos usando o método expand_for_each(), antes da execução dos steps reais.

---

### 🔄 Ação `FIND` — Localização de objetos na tela

A ação `FIND` é usada para localizar um elemento na tela (por imagem ou por texto), podendo clicar, rolar até encontrá-lo ou apenas validar sua presença.

#### 🧩 Estrutura Geral
```yaml
- action: FIND
  object_type: IMG | TEXT          # Tipo do objeto a localizar
  image_path: caminho/para/imagem  # Usado se object_type = IMG
  text: "Texto a localizar"        # Usado se object_type = TEXT
  click: True | False              # Clica no objeto após encontrar
  scroll: True | False             # Rola até o objeto, se necessário
  scroll_image_path: caminho/scroll.png  # Imagem da barra de scroll (se usada)
  scroll_direction: DOWN | UP  # Direção da rolagem
  x_coord: 0                       # Ajuste fino na posição X do clique
  y_coord: 0                       # Ajuste fino na posição Y do clique
  wait: 1.0                        # Espera após encontrar o objeto
  debug: True | False              # Mostra o ponto encontrado visualmente
  helper: "Mensagem opcional de debug"
```
#### 🖼️ Exemplo 1 — Localizando um botão por imagem
```yaml
- action: FIND
  object_type: IMG
  click: True
  image_path: examples/images/login_pipeline/login_button.png
  wait: 1
```
Neste caso:

- O bot procura a imagem `login_button.png` na tela;
- Após encontrar, clica automaticamente no `centro do botão`;
- Espera 1 segundo antes de seguir para o próximo passo.

#### 🔤 Exemplo 2 — Localizando texto na interface
```yaml
- action: FIND
  object_type: TEXT
  text: "Add file"
  click: True
  scroll: True
  scroll_image_path: examples/images/scroll.png
```
Aqui:
- O bot procura pelo texto `"Add file"` na tela usando OCR;
- Se não estiver visível, rola a página para baixo até encontrar;
- Clica sobre o texto quando for localizado.

#### ⚙️ Comportamento interno
Internamente, o FIND:

- Chama find_image_center() (para IMG) ou encontrar_texto_central() (para TEXT);
- Caso não encontre e scroll=True, tenta rolar a tela (limitado por scroll_max_attempts);
- Ao encontrar:
  - Aplica deslocamento (x_coord, y_coord);
  - Mostra o ponto (se debug=True);
  - Executa o clique (se click=True).
- A busca é recursiva: se o elemento não for encontrado após o scroll, o método tenta novamente até atingir o número máximo de tentativas.

### 🎹 Ação `KEYS_SELECTIONS` — Envio de combinações de teclas

A ação KEYS_SELECTIONS é usada para enviar atalhos de teclado ou combinações de teclas (como `CTRL+S`, `ENTER`, `TAB`, etc.) diretamente para a `janela ativa do navegador` controlado pelo Selenium.

Essa ação é útil para `interagir com menus, atalhos da interface, confirmações ou inputs invisíveis, onde um clique não é suficiente`.

#### 🧩 Estrutura geral
```yaml
- action: KEYS_SELECTIONS
  keys:
    - "CTRL"
    - "S"

```

#### ⚙️ Parâmetros
| Campo | Tipo | Obrigatorio | Descrição|
|-------|------|-------------|----------|
|keys   |List[str]|✅| Lista de teclas a serem pressionadas em sequência. Cada item deve ser reconhecido pelo Selenium (ENTER, CTRL, TAB, SHIFT, ESC, etc.).|
|wait| float | ❌ | Tempo de espera (em segundos)|
|helper| str | ❌ | Mensagem Descritiva que aparece no log antes da execução|


#### 🧠 Funcionamento interno
Internamente, o método:
- Cria uma sequência de ações (`ActionChains`) com o Selenium;
- Converte cada string da lista keys em uma tecla reconhecida (`Keys.<tecla>`);
- Envia os comandos de teclado para a janela ativa (`driver.active_element`).

#### 💻 Exemplo 1 — Salvando um módulo (CTRL + S)
```yaml
- action: KEYS_SELECTIONS
  keys:
    - "CTRL"
    - "S"
```
➡️ O bot simula o atalho CTRL+S, equivalente ao comando Salvar em muitas interfaces web e IDEs.

#### 🧭 Exemplo 2 — Navegando entre campos
```yaml
- action: KEYS_SELECTIONS
  keys:
    - "TAB"
    - "TAB"
    - "ENTER"
```
➡️ Move o foco duas vezes com TAB e confirma com ENTER.
Excelente para formulários ou quando o botão não tem imagem/texto detectável.


### 🎹 Ação `WRITE` — Escrita de texto ou arquivo no campo ativo

A ação `WRITE` é responsável por inserir texto (manual ou a partir de um arquivo) no campo atualmente ativo na interface controlada pelo Selenium.
Normalmente é usada após localizar um campo de input com `FIND`, simulando a digitação do usuário.

#### 🧩 Estrutura geral
```yaml
- action: WRITE
  text: "Exemplo de texto a ser digitado"
```
ou
```yaml
- action: WRITE
  file_path: "/caminho/para/arquivo.txt"
```

#### ⚙️ Parâmetros

| Campo | Tipo | Obrigatorio | Descrição|
|-------|------|-------------|----------|
|text   |str |⚙️ Opcional (exclusivo com `file_path`)| Texto a ser inserido diretamente no campo ativo. |
|file_path   |str |⚙️ Opcional (exclusivo com `text`)| Caminho para um arquivo cujo conteúdo será escrito no campo. |
|wait| float | ❌ | Tempo de espera (em segundos)|
|helper| str | ❌ | Mensagem Descritiva que aparece no log antes da execução|

- Apenas um entre text ou file_path deve ser fornecido.
- Se ambos forem definidos, o validador interno (validation_models.py) lançará erro.

#### ⚙️ Funcionamento interno
O método `write()` da classe BotActions:
- Verifica se `text` ou `file_path` foi definido;
- Se `file_path` for usado, lê o conteúdo do arquivo via `open_file()`;
- Usa o `JavaScript injetado via Selenium` para inserir o texto diretamente:
    ```python
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
    ```
- Garante compatibilidade tanto com páginas HTML normais quanto com aplicações Flutter Web.

#### 💻 Exemplo 1 — Escrevendo um texto simples
```yaml
- action: FIND
  object_type: TEXT
  click: True
  text: "Name of the module"
- action: WRITE
  text: "Meu primeiro módulo automatizado"
```
O bot encontra o campo com o texto “Name of the module”, clica, e insere o texto.

#### 📁 Exemplo 2 — Escrevendo o conteúdo de um arquivo
```yaml
- action: FIND
  object_type: TEXT
  click: True
  text: "Add file"

- action: WRITE
  file_path: "/home/user/project/scripts/modelling.py"
```
O conteúdo completo do arquivo modelling.py é colado no campo ativo.

#### ⚠️ Cuidados

- O campo de input deve estar ativo (focado) antes de executar WRITE.
- Evite caracteres especiais não suportados no YAML sem aspas.
- Se a aplicação não responder à digitação simulada, WRITE usa injeção direta via JavaScript — mais rápida e confiável.
- Compatível com páginas HTML e Flutter Web.

### 🎹 Ação `RUN_SCRIPT` — Execução de scripts externos
A ação `RUN_SCRIPT` permite executar scripts de terminal (shell scripts) durante a automação.
Ela é útil para integrar operações externas ao navegador, como configurar ambientes, enviar requisições API, gerar arquivos ou atualizar variáveis no fluxo do bot.

#### 🧩 Estrutura geral

```yaml
- action: RUN_SCRIPT
  script_path: "scripts/setup_env.sh"
```
ou, com armazenamento de resultado:
```yaml
- action: RUN_SCRIPT
  script_path: "scripts/fetch_token.sh"
  save_as: "AUTH_TOKEN"
```

#### ⚙️ Parâmetros

| Campo | Tipo | Obrigatorio | Descrição|
|-------|------|-------------|----------|
|script_path  |str |✅| Caminho completo do script .sh a ser executado. |
|save_as| str | ❌ | Nome da variável onde o resultado (stdout) será salvo em data_store.|
|wait| float | ❌ | Tempo de espera (em segundos)|
|helper| str | ❌ | Mensagem Descritiva que aparece no log antes da execução|

#### ⚙️ Funcionamento interno
O método `run_script()` da classe BotActions:
- Valida o caminho do script — lança erro se o arquivo não existir;
- Executa o script usando subprocess.run():
  ```python
  result = subprocess.run(
      ["bash", script_path],
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      text=True,
      check=True
  )
  ```
- Captura o `stdout` (saída do script) e, se definido `save_as`, armazena em `self.data_store[save_as]`

#### 📘 Exemplo 1 — Execução simples de script
```yaml
- action: RUN_SCRIPT
  script_path: "scripts/prepare_dataset.sh"
```
Executa o script prepare_dataset.sh durante o fluxo da pipeline, sem armazenar saída.

#### Exemplo 2 — Capturando o resultado do script
```yaml
- action: RUN_SCRIPT
  script_path: "scripts/get_api_token.sh"
  save_as: "AUTH_TOKEN"
```
O resultado do script (stdout) é salvo na variável $AUTH_TOKEN, podendo ser usado depois:
```yaml
- action: WRITE
  text: "Authorization: Bearer $AUTH_TOKEN"
```

#### ⚠️ Cuidados
- O script deve ser executável e ter permissões adequadas (`chmod +x script.sh`).
- O erro do script é capturado e mostrado no log com o texto Script failed
- A variável `save_as` é salva em `data_store` e pode ser reutilizada em steps posteriores com `$VAR_NAME`.

### 🎹 Ação `STOP_IF` —— Interrupção condicional da pipeline
A ação `STOP_IF` é usada para interromper a execução da pipeline com base em uma condição lógica.
Ela permite inserir verificações dinâmicas durante a automação, evitando que o fluxo continue caso uma variável, resultado de script ou valor lido do sistema não satisfaça uma regra.

#### 🧩 Estrutura geral
```yaml
- action: STOP_IF
  condition: "$AUTH_TOKEN == ''"
```
Se a variável $AUTH_TOKEN estiver vazia, a execução da pipeline será encerrada imediatamente.

#### ⚙️ Parâmetros
| Campo | Tipo | Obrigatorio | Descrição|
|-------|------|-------------|----------|
|condition  |str |✅| Expressão lógica a ser avaliada. Pode conter variáveis do contexto (`data_store`). |
|wait| float | ❌ | Tempo de espera (em segundos)|
|helper| str | ❌ | Mensagem Descritiva que aparece no log antes da execução|

#### ⚙️ Funcionamento interno
O método `stop_if()` da classe BotActions executa os seguintes passos:
- Lê a expressão definida em condition;
- Substitui variáveis do formato `$VAR` pelos valores atuais do data_store;
- Avalia a expressão usando o método `evaluate_condition()` — `retornando True ou False`;
- Se o resultado for True, interrompe imediatamente a execução da pipeline e loga o motivo.

#### 📘 Exemplo 1 — Parar execução se variável estiver vazia
```yaml
- action: STOP_IF
  condition: "$SESSION_ID == ''"
  helper: "Verificando se sessão foi criada"
```
Se a variável `SESSION_ID` não tiver valor, a pipeline será interrompida.

#### 📘 Exemplo 2 — Verificação após script
```yaml
- action: RUN_SCRIPT
  script_path: scripts/get_session_id.sh
  save_as: "SESSION_ID"

- action: STOP_IF
  condition: "$SESSION_ID == ''"
  helper: "Falha ao obter SESSION_ID"
```
Garante que o script anterior realmente retornou um valor antes de continuar.

### 🧰 Ações Disponíveis

| Ação              | Descrição |
|-------------------|-----------|
| **FIND**          | Localiza imagem ou texto na tela (`IMG` ou `TEXT`) |
| **WRITE**         | Digita texto ou escreve conteúdo de arquivo |
| **KEYS_SELECTIONS** | Envia sequência de teclas |
| **RUN_SCRIPT**    | Executa um shell script local |
| **STOP_IF**       | Interrompe execução se condição for verdadeira |
| **FOR_EACH**      | Executa steps dentro de um loop |
| **FIND_TEXT_BY_COLOR** | Extrai texto colorido de uma imagem |
| **UPLOAD_FILE**   | Envia arquivos para campos de upload |

---

## 🧩 Execução

```python
from BotUi.BotUI import BotUI

bot = BotUI(
    yaml_path="examples/spaceflight_module_loop.yaml",
    screenshots_path="examples/screenshots",
    log_file="botui.log"
)

bot.run()
```

---

## 🧠 Estrutura Interna

| Classe | Função |
|--------|--------|
| **BotUI** | Lê e valida o YAML, executa pipelines e steps |
| **BotActions** | Executa as ações (`find`, `write`, `scroll`, etc.) |
| **validation_models** | Define e valida a estrutura do YAML |
| **image_functions** | Manipula e detecta imagens via OpenCV |
| **selenium_functions** | Inicializa o navegador e envia cliques |
| **utils** | Substitui variáveis, abre arquivos, etc. |

---

## 🧾 Logs

O log detalhado é salvo tanto no terminal quanto em arquivo (`botui.log`):

```
2025-11-04 14:32:10 [INFO] 🚀 Pipeline 'login' aberta em URL: http://example.com
2025-11-04 14:32:12 [INFO] 🔹 Step: Digitando usuário
2025-11-04 14:32:15 [DEBUG] ⏱ Aguardando 1.00 segundos
2025-11-04 14:32:16 [INFO] ✅ Todas as pipelines concluídas
```

---

## 🧱 Boas Práticas

- Sempre use caminhos **absolutos ou relativos ao projeto** nas imagens.  
- Coloque as imagens em `examples/images/...` e screenshots em `examples/screenshots/`.  
- Se possível, mantenha um **scroll.png** genérico para todos os módulos.  
- Use `<<: *anchors` para reduzir redundância.  
- Sempre teste o YAML com `bot.validate_config()` antes de executar.  

---

## 🧪 Teste rápido

TODO

---

## 📜 Licença

MIT — livre para uso e modificação.  
Criado por **Gabriel Guimarães** 🧠  
