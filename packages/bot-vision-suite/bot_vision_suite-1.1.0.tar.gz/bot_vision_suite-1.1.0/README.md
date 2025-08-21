# Bot Vision Suite

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-published-green.svg)
![PyPI](https://img.shields.io/pypi/v/bot-vision-suite.svg)

**Bot Vision Suite** é uma biblioteca Python avançada para automação de interface gráfica que combina **OCR avançado com múltiplas técnicas de processamento de imagem** e **detecção robusta de imagens com variações de escala** para garantir funcionamento independente da resolução da tela.

## 🚀 **CARACTERÍSTICAS DESTACADAS**

### 🔄 **SISTEMA DE BACKTRACK INTELIGENTE** ⭐

- **Backtrack entre métodos individuais**: Se uma ação falhar, automaticamente reexecuta a anterior
- **Backtrack em listas de tarefas**: Navegação inteligente entre tarefas com retry automático
- **Sessões de backtrack**: Controle manual de sessões para automações complexas
- **Configurável por método**: Ative/desative backtrack para cada ação individualmente

### 🖼️ **DETECÇÃO DE IMAGENS ROBUSTA** ⭐

- **Variações de escala automáticas**: Busca imagens em diferentes tamanhos (0.8x a 1.2x)
- **Independência de resolução**: Funciona em qualquer resolução de tela
- **Parâmetro `specific`**:
  - `specific=True`: Busca apenas na região definida (mais rápido)
  - `specific=False`: Busca na tela inteira + variações de escala (mais flexível)
- **Múltiplas tentativas**: Sistema de retry com ajuste automático de confiança

### 🔍 **OCR AVANÇADO COM MÚLTIPLAS TÉCNICAS** ⭐

- **28+ técnicas de pré-processamento** otimizadas para diferentes tipos de texto
- **Processamento HSV**: Melhora detecção em fundos coloridos (62% confiança)
- **Thresholding adaptativo**: Ideal para texto em fundos variados
- **Processamento LAB**: Equalização de luminosidade para melhor contraste
- **Máscaras de cor**: Detecção específica em fundos rosa, cinza, etc.
- **Combinações otimizadas**: Mescla das melhores técnicas para máxima precisão

## 📦 **INSTALAÇÃO**

```bash
pip install bot-vision-suite
```

### **Pré-requisitos - Tesseract OCR**

A biblioteca detecta automaticamente o Tesseract OCR. Se não estiver instalado:

**Windows:**

```bash
# Baixe de: https://github.com/UB-Mannheim/tesseract/wiki
# Instale em: C:\Program Files\Tesseract-OCR\
# Adicione ao PATH do sistema
```

**Linux:**

```bash
sudo apt-get install tesseract-ocr
```

**macOS:**

```bash
brew install tesseract
```

## 🎯 **USO RÁPIDO**

### **Exemplo Básico com Backtrack**

```python
from bot_vision import BotVision

bot = BotVision()

# Backtrack automático entre métodos
success1 = bot.click_image('button1.png', backtrack=True)
success2 = bot.click_text('Save', backtrack=True)      # Se falhar, volta pro button1
success3 = bot.click_text('Confirm', backtrack=True)   # Se falhar, volta pro Save
```

### **Sessão de Backtrack Manual**

```python
bot = BotVision()

# Inicia sessão de backtrack
bot.start_task_session()

bot.click_image('button1.png', backtrack=True)
bot.click_text('agent', backtrack=True)
bot.click_text('Claude Sonnet 4', backtrack=True)

# Finaliza e mostra estatísticas
successful, total = bot.end_task_session()
print(f"Sucesso: {successful}/{total}")
```

## 🔧 **FUNCIONALIDADES COMPLETAS**

### **1. DETECÇÃO DE IMAGENS COM VARIAÇÕES DE ESCALA**

```python
# Busca imagem com variações de tamanho (independente da resolução)
success = bot.click_image('button.png',
                         region=(100, 100, 200, 50),
                         confidence=0.9,
                         specific=False,        # False = permite buscar na tela inteira
                         backtrack=True,        # Volta para a tarefa anterior
                         max_attempts=3)

# Parâmetros explicados:
# specific=False: Busca na tela inteira + variações de escala (0.8x a 1.2x)
# specific=True:  Busca apenas na região definida (mais rápido)
# backtrack=True: Se falhar, reexecuta ação anterior automaticamente
```

### **2. OCR AVANÇADO COM FILTROS**

```python
# Busca texto com filtros específicos
success = bot.click_text('Login',
                         region=(50, 50, 300, 100),
                         filter_type='letters',        # 'letters', 'numbers', 'both'
                         occurrence=1,                 # Primeira ocorrência
                         confidence_threshold=75.0,    # 75% de confiança
                         backtrack=True,
                         sendtext='usuario123')        # Digita após clique

# Comandos especiais em sendtext:
# {ctrl}a{del}Novo texto{enter} = Ctrl+A, Delete, digita texto, Enter
```

### **3. IMAGENS RELATIVAS (ANTI-DUPLICAÇÃO)**

```python
# Busca target próximo a uma âncora específica
success = bot.click_relative_image(
    anchor_image='warning_icon.png',    # Imagem âncora (única na tela)
    target_image='ok_button.png',       # Imagem target (pode ter várias)
    max_distance=200,                   # Máximo 200px da âncora
    confidence=0.9,
    backtrack=True
)

# Útil quando há múltiplas opções iguais na tela
# Exemplo: Várias imagens "OK" mas você quer a que está perto do "Warning"
```

### **4. COMANDOS DE TECLADO COMPLETOS**

```python
# 100+ comandos pré-definidos
bot.keyboard_command('Ctrl+S')          # Salvar
bot.keyboard_command('F7')              # Clear Block (Oracle Forms)
bot.keyboard_command('Alt+Tab')         # Trocar janela

# Lista completa disponível:
commands = bot.get_available_keyboard_commands()
print(f"Total de comandos: {len(commands)}")
```

### **5. FUNÇÕES DE CONVENIÊNCIA**

```python
from bot_vision import (find_text, click_text, click_image, click_at,
                        find_relative_image, click_relative_image,
                        click_coordinates, type_text_standalone,
                        keyboard_command_standalone)

# Uso rápido sem instanciar classe
success = click_text("Confirmar", region=(200, 200, 600, 400), backtrack=True)
success = click_image("button.png", confidence=0.9, backtrack=True)
success = click_relative_image("anchor.png", "target.png", backtrack=True)
```

## 📋 **CONFIGURAÇÃO DE TAREFAS AVANÇADA**

### **Formato Completo de Task**

```python
tasks = [
    # 1. Busca de imagem com variações de escala
    {
        'image': 'button.png',
        'region': (100, 100, 200, 50),
        'confidence': 0.9,
        'specific': False,              # False = permite variações de escala
        'backtrack': True,              # Retry automático
        'delay': 1,
        'mouse_button': 'left'          # 'left', 'right', 'double', 'move_to'
    },

    # 2. Busca de texto OCR avançado
    {
        'text': 'Login',
        'region': (50, 50, 300, 100),
        'occurrence': 1,                # Primeira ocorrência
        'char_type': 'letters',         # Filtro de caracteres
        'backtrack': True,              # Retry automático
        'delay': 0.5,
        'sendtext': 'usuario123'        # Digita após clique
    },

    # 3. Imagem relativa (âncora + target)
    {
        'type': 'relative_image',
        'anchor_image': 'warning_icon.png',    # Imagem âncora única
        'target_image': 'ok_button.png',       # Imagem target próxima
        'max_distance': 200,                   # Distância máxima em pixels
        'confidence': 0.9,
        'target_region': (0, 0, 800, 600),    # Região para buscar target (opcional)
        'specific': True,
        'backtrack': True,
        'delay': 1
    },

    # 4. Clique em coordenadas específicas
    {
        'type': 'click',
        'x': 500,                              # Coordenada X
        'y': 300,                              # Coordenada Y
        'mouse_button': 'right',               # 'left', 'right', 'double', 'move_to'
        'delay': 0.5,
        'backtrack': False
    },

    # 5. Digitação direta de texto
    {
        'type': 'type_text',
        'text': 'Hello World!',               # Texto a digitar
        'interval': 0.05,                     # Intervalo entre caracteres
        'delay': 1
    },

    # 6. Comando de teclado
    {
        'type': 'keyboard_command',
        'command': 'Ctrl+S',                  # Comando a executar
        'delay': 1
    }
]

# Execução simples
from bot_vision import execute_tasks
execute_tasks(tasks)

# Execução avançada com controle
bot = BotVision()
resultados = bot.execute_tasks(tasks)
```

## ⚙️ **CONFIGURAÇÃO AVANÇADA**

### **Configuração Personalizada**

```python
from bot_vision import BotVision

# Configuração completa
config = {
    "confidence_threshold": 80.0,        # Limiar OCR padrão (75-95)
    "tesseract_lang": "por",             # Idioma: 'eng', 'por', 'spa'
    "tesseract_path": r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    "tessdata_path": r"C:\Program Files\Tesseract-OCR\tessdata",
    "preprocessing_enabled": True,        # Melhora OCR (recomendado)
    "retry_attempts": 5,                 # Tentativas padrão
    "default_delay": 1.5,               # Delay padrão entre ações
    "show_overlay": False,               # Desabilita overlay vermelho globalmente
    "screenshot_delay": 0.1              # Delay para captura de tela
}

bot = BotVision(config=config)
```

### **Parâmetros de Métodos Completos**

```python
# click_image com todos os parâmetros
success = bot.click_image('button.png',
                         region=(100, 100, 200, 50),      # x, y, width, height
                         confidence=0.9,                   # 0.0 a 1.0 (90% precisão)
                         delay=1,                          # Pausa 1 seg após clique
                         mouse_button='left',              # 'left', 'right', 'double', 'move_to'
                         backtrack=True,                   # Retry inteligente
                         specific=False,                   # False = permite variações de escala
                         max_attempts=3,                   # Máximo 3 tentativas
                         sendtext=None,                    # Texto para digitar depois
                         show_overlay=True)                # Exibe marcação vermelha

# click_text com todos os parâmetros
success = bot.click_text('Login',
                         region=(50, 50, 300, 100),       # x, y, width, height
                         filter_type='letters',            # 'letters', 'numbers', 'both'
                         delay=1,                          # Pausa após o clique
                         mouse_button='left',              # Tipo de clique
                         occurrence=1,                     # Qual ocorrência clicar
                         backtrack=True,                   # Retry inteligente
                         max_attempts=3,                   # Máximo de tentativas
                         sendtext='usuario123',            # Texto para digitar após clique
                         confidence_threshold=75.0)        # Precisão OCR (75%)
```

## 🔍 **TÉCNICAS DE PROCESSAMENTO DE IMAGEM**

### **28+ Técnicas Implementadas**

```python
from bot_vision import ImageProcessor
from PIL import Image

# Carregue imagem
img = Image.open('documento.png')

# Processe para OCR com todas as técnicas
processor = ImageProcessor(methods='all')
processed_images = processor.preprocess_for_ocr(img)

print(f"Geradas {len(processed_images)} variações para OCR")

# Técnicas principais:
# 1. HSV Enhancement (62% confiança) - Melhor para números em caixas coloridas
# 2. Dark Background (59% confiança) - Texto claro em fundo escuro
# 3. Channel Processing (57% confiança) - Processamento de canais RGB
# 4. Contrast Sharpening (41% confiança) - Alta nitidez e contraste
# 5. Adaptive Threshold - Thresholding adaptativo para fundos variados
# 6. Color Masking - Máscaras específicas para fundos rosa, cinza
# 7. LAB Enhancement - Equalização de luminosidade
# 8. Combinations - Mescla das melhores técnicas
```

### **OCR com Múltiplas Técnicas**

```python
from bot_vision import OCREngine
from PIL import Image

# Carregue uma imagem
img = Image.open('screenshot.png')

# Initialize OCR engine
ocr = OCREngine()

# Extraia todo o texto com todas as técnicas
results = ocr.extract_all_text(img, filter_type='numbers')

for result in results:
    print(f"Texto: {result.text}, Confiança: {result.confidence}")
```

## 🎨 **EXEMPLOS AVANÇADOS**

### **Automação Completa com Backtrack**

```python
from bot_vision import BotVision
import calendar
from datetime import datetime

# Configuração customizada
config = {
    "confidence_threshold": 80.0,
    "retry_attempts": 5,
    "overlay_color": "blue",
    "preprocessing_enabled": True
}

bot = BotVision(config=config)

# Variáveis dinâmicas
primeiro_dia = str(1)
ultimo_dia = str(calendar.monthrange(datetime.now().year, datetime.now().month)[1])

# Tasks complexas com backtrack
tasks = [
    {
        'text': 'Data Inicial',
        'region': (100, 100, 300, 200),
        'char_type': 'letters',
        'sendtext': f'{primeiro_dia}/01/{datetime.now().year}',
        'delay': 1,
        'backtrack': True
    },
    {
        'text': 'Data Final',
        'region': (100, 250, 300, 200),
        'char_type': 'letters',
        'sendtext': f'{ultimo_dia}/12/{datetime.now().year}',
        'delay': 1,
        'backtrack': True
    },
    {
        'image': 'processar.png',
        'confidence': 0.8,
        'specific': False,        # Permite variações de escala
        'delay': 3,
        'backtrack': True
    }
]

# Execute com backtrack automático
bot.execute_tasks(tasks)
```

### **Hover e Navegação Avançada**

```python
# Apenas mover o mouse para elementos (hover)
success = bot.click_text("Menu", mouse_button="move_to", delay=0.5)
success = bot.click_image("button.png", mouse_button="move_to", delay=1.0)
success = bot.click_coordinates(100, 200, mouse_button="move_to", delay=0.5)

# Tasks com hover
hover_tasks = [
    {
        'text': 'Tooltip trigger',
        'mouse_button': 'move_to',  # Apenas posiciona o mouse
        'delay': 2.0                # Espera para tooltip aparecer
    },
    {
        'text': 'Click here',       # Agora clica em outro elemento
        'mouse_button': 'left',
        'delay': 1.0,
        'backtrack': True
    }
]
```

## 🔧 **DESENVOLVIMENTO**

### **Estrutura do Projeto**

```
bot-vision-suite/
├── bot_vision/
│   ├── core/                    # Módulos principais
│   │   ├── image_processing.py  # 28+ técnicas de processamento
│   │   ├── ocr_engine.py        # Engine OCR avançado
│   │   ├── relative_image.py    # Detecção de imagens relativas
│   │   ├── keyboard_commands.py # 100+ comandos de teclado
│   │   ├── task_executor.py     # Executor com backtrack
│   │   └── overlay.py           # Overlay visual
│   ├── utils/                   # Utilitários
│   └── exceptions.py            # Exceções customizadas
├── tests/                       # Testes automatizados
├── docs/                        # Documentação
└── examples/                    # Exemplos de uso
```

### **Executar Testes**

```bash
pip install bot-vision-suite[dev]
pytest tests/
```

## 🤝 **Contribuindo**

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 **Licença**

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 **Suporte**

- **Repo**: [Repositorio Completa](https://github.com/matheuszwilk/bot-vision-suite)
- **Issues**: [GitHub Issues](https://github.com/matheuszwilk/bot-vision-suite/issues)
- **Exemplos**: [Pasta de Exemplos](examples/)

## 🙏 **Agradecimentos**

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) pela engine de OCR
- [PyAutoGUI](https://github.com/asweigart/pyautogui) pela automação de interface
- [OpenCV](https://opencv.org/) pelo processamento de imagem
- [Pillow](https://python-pillow.org/) pela manipulação de imagens

---

**Bot Vision Suite** - Automatize sua interface gráfica com **precisão máxima** e **robustez total**! 🤖✨

### **🎯 DESTAQUES FINAIS**

✅ **Sistema de Backtrack Inteligente** - Retry automático entre ações  
✅ **Variações de Escala Automáticas** - Funciona em qualquer resolução  
✅ **28+ Técnicas de Processamento de Imagem** - OCR com máxima precisão  
✅ **Detecção de Imagens Relativas** - Anti-duplicação inteligente  
✅ **100+ Comandos de Teclado** - Suporte completo a Oracle Forms  
✅ **Configuração Flexível** - Adaptável a qualquer cenário  
✅ **Multiplataforma** - Windows, Linux e macOS
