"""
Bot Vision Suite - Advanced GUI Automation with OCR

Uma biblioteca Python avançada para automação de interface gráfica que combina
reconhecimento óptico de caracteres (OCR) otimizado com detecção de imagens
para executar tarefas automatizadas em aplicações desktop.

⚠️  REQUISITO IMPORTANTE: TESSERACT OCR DEVE ESTAR INSTALADO! ⚠️

📥 INSTALAÇÃO DO TESSERACT:
    1. Baixe: https://github.com/UB-Mannheim/tesseract/wiki
    2. Instale em: C:\\Program Files\\Tesseract-OCR\\
    3. Adicione ao PATH do sistema
    4. Teste: tesseract --version

🚀 FUNCIONALIDADES COMPLETAS - MÉTODOS INDIVIDUAIS E LISTAS 🚀

═══════════════════════════════════════════════════════════════════════════════

🔥 BACKTRACK ENTRE MÉTODOS INDIVIDUAIS (NOVO!):
    
    >>> from bot_vision import BotVision
    >>> 
    >>> bot = BotVision()
    >>> 
    >>> # OPÇÃO 1: Auto-inicia sessão quando backtrack=True
    >>> success1 = bot.click_image('button1.png', backtrack=True)
    >>> success2 = bot.click_text('Save', backtrack=True)  # Se falhar, volta pro button1
    >>> success3 = bot.click_text('Confirm', backtrack=True)  # Se falhar, volta pro Save
    >>> 
    >>> # OPÇÃO 2: Controle manual da sessão
    >>> bot.start_task_session()  # Inicia sessão de backtrack
    >>> bot.click_image('button1.png', backtrack=True)
    >>> bot.click_text('agent', backtrack=True)
    >>> bot.click_text('Claude Sonnet 4', backtrack=True)
    >>> successful, total = bot.end_task_session()  # Finaliza e mostra estatísticas

═══════════════════════════════════════════════════════════════════════════════

📋 EXECUÇÃO DE TAREFAS EM LISTA (Método Original + NOVAS FUNCIONALIDADES):
    
    >>> from bot_vision import BotVision, execute_tasks
    >>> 
    >>> # Tarefas com TODAS as funcionalidades (incluindo NOVAS!)
    >>> tasks = [
    ...     # 1. Busca de imagem tradicional
    ...     {
    ...         'image': 'button.png',
    ...         'region': (100, 100, 200, 50),
    ...         'confidence': 0.9,
    ...         'specific': False,       # Permite variações de escala
    ...         'backtrack': True,       # Retry automático
    ...         'delay': 1,
    ...         'mouse_button': 'left'   # 'left', 'right', 'double', 'move_to'
    ...     },
    ...     # 2. Busca de texto OCR
    ...     {
    ...         'text': 'Login',
    ...         'region': (50, 50, 300, 100),
    ...         'occurrence': 1,         # Primeira ocorrência
    ...         'char_type': 'letters',  # Filtro de caracteres
    ...         'backtrack': True,       # Retry automático
    ...         'delay': 0.5,
    ...         'sendtext': 'usuario123' # Digita após clique
    ...     },
    ...     # 3. NOVO! Busca de imagem relativa (âncora + target)
    ...     {
    ...         'type': 'relative_image',
    ...         'anchor_image': 'warning_icon.png',    # Imagem âncora única
    ...         'target_image': 'ok_button.png',       # Imagem target próxima
    ...         'max_distance': 200,                   # Distância máxima em pixels
    ...         'confidence': 0.9,
    ...         'target_region': (0, 0, 800, 600),     # Região para buscar target (opcional)
    ...         'specific': True,
    ...         'backtrack': True,
    ...         'delay': 1
    ...     },
    ...     # 4. NOVO! Clique em coordenadas específicas
    ...     {
    ...         'type': 'click',
    ...         'x': 500,                              # Coordenada X
    ...         'y': 300,                              # Coordenada Y
    ...         'mouse_button': 'right',               # 'left', 'right', 'double', 'move_to'
    ...         'delay': 0.5,
    ...         'backtrack': False
    ...     },
    ...     # 5. NOVO! Digitação de texto direta
    ...     {
    ...         'type': 'type_text',
    ...         'text': 'Hello World!',               # Texto a digitar
    ...         'interval': 0.05,                     # Intervalo entre caracteres
    ...         'delay': 1
    ...     },
    ...     # 6. NOVO! Comando de teclado
    ...     {
    ...         'type': 'keyboard_command',
    ...         'command': 'Ctrl+S',                  # Comando a executar
    ...         'delay': 1
    ...     }
    ... ]
    >>> 
    >>> # Execução simples
    >>> execute_tasks(tasks)
    >>> 
    >>> # Execução avançada com controle
    >>> bot = BotVision()
    >>> resultados = bot.execute_tasks(tasks)

═══════════════════════════════════════════════════════════════════════════════

🎯 MÉTODOS INDIVIDUAIS COM TODAS AS FUNCIONALIDADES:

📸 BUSCA E CLIQUE EM IMAGENS (DETALHES COMPLETOS):
    
    >>> bot = BotVision()
    >>> 
    >>> # Buscar imagem básica
    >>> location = bot.find_image('button.png', 
    ...                          region=(100, 100, 300, 200),
    ...                          confidence=0.9)
    >>> 
    >>> # Clicar em imagem COM TODOS OS PARÂMETROS:
    >>> success = bot.click_image('element_1_2.png',
    ...                          region=(3, 664, 41, 46),      # x, y, width, height
    ...                          confidence=0.9,               # 0.0 a 1.0 (90% precisão)
    ...                          delay=1,                      # Pausa 1 seg após clique
    ...                          mouse_button='left',          # 'left', 'right', 'double', 'move_to'
    ...                          backtrack=True,               # Retry inteligente
    ...                          specific=False,               # False = permite variações
    ...                          max_attempts=3)               # Máximo 3 tentativas
    >>> 
    >>> # PARÂMETROS DETALHADOS:
    >>> # region:       Define área de busca (x, y, largura, altura)
    >>> # confidence:   Precisão da detecção (0.8=80%, 0.95=95%)
    >>> # delay:        Pausa em segundos após a ação
    >>> # mouse_button: Tipo de clique a executar
    >>> # backtrack:    Se falhar, reexecuta tarefa anterior
    >>> # specific:     True=busca na região, False=busca tela inteira + variações
    >>> # max_attempts: Quantas vezes tentar antes de desistir

📝 BUSCA E CLIQUE EM TEXTO OCR (DETALHES COMPLETOS):
    
    >>> # Buscar texto básico
    >>> location = bot.find_text('Login',
    ...                         region=(0, 0, 800, 600),
    ...                         filter_type='letters',        # 'letters', 'numbers', 'both'
    ...                         confidence_threshold=75.0,
    ...                         occurrence=1)                 # Qual ocorrência
    >>> 
    >>> # Clicar em texto COM TODOS OS PARÂMETROS:
    >>> success = bot.click_text('Claude Sonnet 4',
    ...                         region=(1363, 965, 85, 23),   # x, y, width, height
    ...                         filter_type='letters',        # Só letras (não números)
    ...                         delay=1,                       # Pausa 1 seg após clique
    ...                         mouse_button='left',           # Clique esquerdo
    ...                         occurrence=1,                  # Primeira ocorrência
    ...                         backtrack=True,                # Retry inteligente
    ...                         max_attempts=3,                # Máximo 3 tentativas
    ...                         sendtext=None)                 # Texto para digitar depois
    >>> 
    >>> # PARÂMETROS DETALHADOS:
    >>> # region:               Define área de busca na tela
    >>> # filter_type:          'letters'=só letras, 'numbers'=só números, 'both'=ambos
    >>> # delay:                Pausa após o clique
    >>> # mouse_button:         Tipo de clique ('left', 'right', 'double', 'move_to')
    >>> # occurrence:           Qual ocorrência clicar (1=primeira, 2=segunda, etc.)
    >>> # backtrack:            Retry inteligente que reexecuta tarefas anteriores
    >>> # max_attempts:         Número de tentativas antes de desistir
    >>> # sendtext:             Texto para digitar após o clique (None=não digita)
    >>> # confidence_threshold: Precisão OCR (75.0=75%, 90.0=90%)

🖱️ CLIQUES E AÇÕES (DETALHES COMPLETOS):
    
    >>> # Clique em coordenadas específicas COM TODOS OS PARÂMETROS:
    >>> bot.click_at((100, 200, 50, 30),              # x, y, width, height
    ...              mouse_button='left',              # 'left', 'right', 'double', 'move_to'
    ...              delay=1)                          # Pausa após clique
    >>> 
    >>> # Digitar texto COM COMANDOS ESPECIAIS:
    >>> bot.type_text('Hello World')                   # Texto simples
    >>> bot.type_text('{ctrl}a{del}Novo Texto{enter}') # Comandos especiais
    >>> 
    >>> # COMANDOS ESPECIAIS SUPORTADOS:
    >>> # {ctrl}a     = Ctrl+A (selecionar tudo)
    >>> # {del}       = Delete
    >>> # {tab}       = Tab
    >>> # {enter}     = Enter
    >>> # Texto normal = Digitado usando clipboard para maior confiabilidade

🎯 IMAGENS RELATIVAS (NOVO! - Busca Target próximo a Âncora):
    
    >>> # Localiza uma imagem target próxima a uma imagem âncora específica
    >>> location = bot.find_relative_image(
    ...     anchor_image='menu_button.png',     # Imagem âncora (única na tela)
    ...     target_image='option.png',          # Imagem target (pode ter várias)
    ...     max_distance=150,                   # Distância máxima em pixels
    ...     confidence=0.9,                     # Confiança de detecção
    ...     target_region=(0, 0, 800, 600)      # Região para buscar target (opcional)
    ... )
    >>> 
    >>> # Clique em imagem relativa COM TODOS OS PARÂMETROS:
    >>> success = bot.click_relative_image(
    ...     anchor_image='anchor.png',          # Âncora de referência
    ...     target_image='target.png',          # Target a clicar
    ...     max_distance=200,                   # Máximo 200px da âncora
    ...     confidence=0.9,                     # 90% de precisão
    ...     target_region=None,                 # None = busca tela inteira
    ...     delay=1,                           # Pausa após clique
    ...     mouse_button='left',               # Tipo de clique
    ...     backtrack=True,                    # Retry inteligente
    ...     max_attempts=3                     # Máximo de tentativas
    ... )
    >>> 
    >>> # USO PRÁTICO: Útil quando há múltiplas opções iguais na tela
    >>> # Exemplo: Várias imagens "OK" mas você quer a que está perto do "Warning"

⌨️ COMANDOS DE TECLADO COMPLETOS (NOVO! - Lista Expandida):
    
    >>> # Executa comando de teclado específico
    >>> bot.keyboard_command('Ctrl+S')          # Salvar
    >>> bot.keyboard_command('F7')              # Clear Block (Oracle Forms)
    >>> bot.keyboard_command('Alt+Tab')         # Trocar janela
    >>> 
    >>> # LISTA COMPLETA DE COMANDOS SUPORTADOS:
    >>> # 
    >>> # === COMANDOS DE SISTEMA (Oracle Forms, etc.) ===
    >>> # F5, F6, F7, F8, F12 - Funções específicas
    >>> # Ctrl+S, Ctrl+E, Ctrl+F11 - Commit, Edit, Enter Query
    >>> # Shift+F5, Shift+F6 - Duplicate Field/Record
    >>> # Ctrl+Up, Ctrl+Down - Delete/Insert Record
    >>> # 
    >>> # === COMANDOS GERAIS ===
    >>> # Ctrl+C, Ctrl+V, Ctrl+X - Copy, Paste, Cut
    >>> # Ctrl+A, Ctrl+Z, Ctrl+Y - Select All, Undo, Redo
    >>> # Tab, Enter, Escape, Delete, Backspace
    >>> # Arrow Up/Down/Left/Right, Home, End
    >>> # Page Up, Page Down
    >>> # 
    >>> # === COMANDOS DE NAVEGADOR ===
    >>> # Ctrl+T, Ctrl+W, Ctrl+R - New Tab, Close Tab, Refresh
    >>> # Ctrl+Shift+T - Reopen Closed Tab
    >>> # 
    >>> # === COMANDOS DE SISTEMA ===
    >>> # Alt+Tab, Alt+F4 - Switch/Close Window
    >>> # Windows+D, Windows+L - Desktop, Lock
    >>> # 
    >>> # Veja lista completa com: bot.get_available_keyboard_commands()

📍 CLIQUE EM COORDENADAS ESPECÍFICAS (NOVO!):
    
    >>> # Clique direto em coordenadas (sem buscar imagem ou texto)
    >>> success = bot.click_coordinates(x=100, y=200,
    ...                                delay=1,
    ...                                mouse_button='left',
    ...                                backtrack=False)
    >>> 
    >>> # Útil quando você sabe exatamente onde clicar

═══════════════════════════════════════════════════════════════════════════════

🔧 FUNÇÕES DE CONVENIÊNCIA (Uso Rápido SEM Instanciar Classe):
    
    >>> from bot_vision import (find_text, click_text, find_image, click_image,
    ...                         find_relative_image, click_relative_image,     # NOVO!
    ...                         click_coordinates, type_text_standalone,        # NOVO!
    ...                         keyboard_command_standalone)                    # NOVO!
    >>> 
    >>> # Busca rápida (funções standalone tradicionais)
    >>> location = find_text("Login", region=(100, 100, 500, 300))
    >>> location = find_image("button.png", confidence=0.9)
    >>> 
    >>> # Clique rápido (funções standalone tradicionais)
    >>> success = click_text("Confirmar", region=(200, 200, 600, 400))
    >>> success = click_image("button.png", backtrack=True)
    >>> 
    >>> # NOVAS FUNCIONALIDADES - Standalone
    >>> # Imagem relativa
    >>> location = find_relative_image("anchor.png", "target.png", max_distance=150)
    >>> success = click_relative_image("anchor.png", "target.png", backtrack=True)
    >>> 
    >>> # Coordenadas específicas
    >>> success = click_coordinates(100, 200, delay=1, backtrack=True)
    >>> 
    >>> # Digitação e comandos de teclado
    >>> success = type_text_standalone("Hello World!", backtrack=True)
    >>> success = keyboard_command_standalone("Ctrl+S", delay=1, backtrack=True)
    >>> 
    >>> # Lista de comandos disponíveis
    >>> commands = get_available_keyboard_commands()
    >>> print(f"Total de comandos: {len(commands)}")
    >>> 
    >>> # NOTA: Estas funções criam uma instância temporária do BotVision

═══════════════════════════════════════════════════════════════════════════════

📋 TIPOS DE TAREFA SUPORTADOS (Para uso em listas):

    🔸 TIPO: 'text' (Busca e clique em texto via OCR)
       Campos: text, region, char_type, occurrence, confidence, backtrack, delay, sendtext
       
    🔸 TIPO: 'image' (Busca e clique em imagem)
       Campos: image, region, confidence, specific, backtrack, delay, mouse_button
       
    🔸 TIPO: 'relative_image' (NOVO! - Busca target próximo a âncora)
       Campos: anchor_image, target_image, max_distance, confidence, target_region, 
               specific, backtrack, delay, mouse_button
       
    🔸 TIPO: 'click' (NOVO! - Clique em coordenadas específicas)
       Campos: x, y, mouse_button, delay, backtrack
       
    🔸 TIPO: 'type_text' (NOVO! - Digitação direta de texto)
       Campos: text, interval, delay
       
    🔸 TIPO: 'keyboard_command' (NOVO! - Comando de teclado)
       Campos: command, delay
       
    🔸 TIPO: 'extract_text' (NOVO! - Extração de texto de região específica)
       Campos: region, filter_type, confidence_threshold, return_full_data, backtrack, delay

═══════════════════════════════════════════════════════════════════════════════

⚙️ CONFIGURAÇÃO AVANÇADA (Personalize o Comportamento):
    
    >>> # Configuração personalizada COMPLETA:
    >>> config = {
    ...     "confidence_threshold": 80.0,        # Limiar OCR padrão (75-95)
    ...     "tesseract_lang": "por",             # Idioma: 'eng', 'por', 'spa'
    ...     "tesseract_path": r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    ...     "tessdata_path": r"C:\Program Files\Tesseract-OCR\tessdata",
    ...     "preprocessing_enabled": True,        # Melhora OCR (recomendado)
    ...     "retry_attempts": 5,                 # Tentativas padrão
    ...     "default_delay": 1.5,               # Delay padrão entre ações
    ...     "show_overlay": False,               # Desabilita overlay vermelho globalmente
    ...     "screenshot_delay": 0.1              # Delay para captura de tela
    ... }
    >>> 
    >>> bot = BotVision(config=config)
    >>> 
    >>> # PARÂMETROS DE CONFIGURAÇÃO EXPLICADOS:
    >>> # confidence_threshold: Precisão mínima para reconhecer texto
    >>> # tesseract_lang:       Idioma para OCR ('eng'=inglês, 'por'=português)
    >>> # tesseract_path:       Caminho do executável Tesseract
    >>> # tessdata_path:        Pasta com dados de idiomas
    >>> # preprocessing_enabled: Melhora imagem antes do OCR
    >>> # retry_attempts:       Tentativas padrão quando não especificado
    >>> # default_delay:        Pausa padrão entre ações
    >>> # show_overlay:         Controla exibição da marcação vermelha antes dos cliques

═══════════════════════════════════════════════════════════════════════════════

🌟 FUNCIONALIDADES AVANÇADAS (EXPLICAÇÃO DETALHADA):

✅ BACKTRACK: Sistema inteligente de retry que, quando uma tarefa falha,
              reexecuta a tarefa anterior e tenta novamente. Funciona tanto
              em listas de tarefas quanto entre métodos individuais.

✅ OCCURRENCE: Permite escolher qual ocorrência de texto clicar na tela.
               occurrence=1 = primeira ocorrência encontrada
               occurrence=2 = segunda ocorrência encontrada, etc.

✅ SPECIFIC: Controla onde buscar imagens na tela.
             specific=True  = busca apenas na região definida (mais rápido)
             specific=False = busca na tela inteira + permite variações de escala
                             (ignora região, mais flexível)

✅ FILTER_TYPE/CHAR_TYPE: Filtra caracteres durante OCR.
                          'letters' = só letras (A-Z, a-z)
                          'numbers' = só números (0-9)
                          'both'    = letras e números

✅ SENDTEXT: Digita texto automaticamente após clique bem-sucedido.
             Suporta comandos especiais: {ctrl}a, {del}, {tab}, {enter}
             Usa clipboard para maior confiabilidade.

✅ CONFIDENCE: Controla precisão para OCR e detecção de imagens.
               0.7 = 70% (mais permissivo, pode ter falsos positivos)
               0.9 = 90% (mais rigoroso, menos falsos positivos)
               0.95 = 95% (muito rigoroso, pode perder elementos válidos)

✅ DELAY: Pausas personalizáveis entre ações em segundos.
          Útil para aguardar carregamento de interfaces.
          delay=0.5 = meio segundo, delay=2 = dois segundos

✅ SHOW_OVERLAY: Controla exibição da marcação vermelha antes dos cliques.
                 show_overlay=True  = exibe marcação (padrão, útil para debug)
                 show_overlay=False = sem marcação (mais rápido, para produção)
                 show_overlay=None  = usa configuração global do bot

✅ MOUSE_BUTTON: Suporte completo a diferentes tipos de clique.
                 • "left" - Clique simples esquerdo (padrão)
                 • "right" - Clique direito (menu contextual)
                 • "double" ou "double left" - Clique duplo esquerdo (abrir/executar)
                 • "move_to" - Apenas move o mouse sem clicar (hover)
                 
                 Exemplos de uso:
                 bot.click_image('file.png', mouse_button="double")  # Abrir arquivo
                 bot.click_text('Menu', mouse_button="right")       # Menu contextual
                 bot.click_image('hover_btn.png', mouse_button="move_to")  # Apenas hover
                 bot.click_relative_image('anchor.png', 'target.png', mouse_button="left")

✅ REGION: Define área específica da tela para busca.
           region=(x, y, width, height)
           x, y = coordenadas do canto superior esquerdo
           width, height = largura e altura da área
           Melhora performance e evita falsos positivos.

✅ MAX_ATTEMPTS: Controla quantas tentativas fazer antes de desistir.
                 max_attempts=1 = tenta só uma vez
                 max_attempts=3 = tenta até 3 vezes (padrão)
                 max_attempts=5 = tenta até 5 vezes (mais persistente)

🎯 DICAS DE USO:
   • Use region sempre que possível para melhor performance
   • confidence entre 0.8-0.9 é ideal para a maioria dos casos
   • specific=False busca na tela inteira e permite variações de escala
   • specific=True busca apenas na região definida (mais rápido)
   • backtrack=True é recomendado para automações complexas
   • filter_type='letters' melhora OCR quando você busca só texto
   • delay adequado evita problemas com interfaces lentas

🚨 TROUBLESHOOTING:
   • Elemento não encontrado: Diminua confidence ou aumente region
   • OCR impreciso: Use preprocessing_enabled=True na configuração
   • Clique no lugar errado: Verifique coordinates do region
   • Backtrack não funciona: Certifique-se que backtrack=True em todos os métodos

═══════════════════════════════════════════════════════════════════════════════
"""

import logging
import time

# Importa classes principais
from .core.task_executor import TaskExecutor, TaskResult, execute_tasks, click_images
from .core.ocr_engine import OCREngine, OCRResult, find_text_with_multiple_preprocessing
from .core.image_processing import ImageProcessor, preprocess_image_for_ocr
from .core.overlay import VisualOverlay, show_overlay
from .core.relative_image import RelativeImageDetector  # NOVA FUNCIONALIDADE
from .core.keyboard_commands import KeyboardCommander  # NOVA FUNCIONALIDADE
from .utils.config import BotVisionConfig, get_default_config
from .utils.text_filters import limpar_texto, matches_filter
from .exceptions import *

# Versão da biblioteca
__version__ = "1.0.0"
__author__ = "Automation Suite Developer"
__email__ = "developer@automation-suite.com"
__license__ = "MIT"

# Configuração de logging padrão
logger = logging.getLogger(__name__)

class BotVision:
    """
    Classe principal do Bot Vision Suite.
    
    Fornece uma interface de alto nível para automação GUI com OCR avançado.
    
    Examples:
        Uso básico:
        >>> bot = BotVision()
        >>> bot.execute_tasks(tasks)
        
        Com configuração customizada:
        >>> config = {"confidence_threshold": 80.0}
        >>> bot = BotVision(config=config)
        >>> bot.execute_tasks(tasks)
    """
    
    def __init__(self, config=None):
        """
        Inicializa o Bot Vision.
        
        Args:
            config (dict or BotVisionConfig, optional): Configurações customizadas
        """
        if isinstance(config, dict):
            self.config = BotVisionConfig(config)
        elif isinstance(config, BotVisionConfig):
            self.config = config
        else:
            self.config = get_default_config()
        
        self.executor = TaskExecutor(self.config)
        self.ocr_engine = OCREngine(self.config)
        self.image_processor = ImageProcessor()
        
        # Configurações de overlay - acessíveis via propriedades
        self._overlay_enabled = self.config.get("overlay_enabled", True)
        self._show_overlay = self.config.get("show_overlay", True)
        
        # Sistema de backtrack para métodos individuais
        self.individual_task_history = []  # Histórico de métodos executados
        self.backtrack_enabled_globally = False  # Se está em modo backtrack
        self.current_task_index = -1  # Índice da tarefa atual
        self.max_backtrack_attempts = 2  # Máximo de tentativas de backtrack por tarefa
        self.task_session_active = False  # Se está em uma sessão de tarefas individuais
    
    def _add_to_task_history(self, method_name, args, kwargs):
        """Adiciona método ao histórico de tarefas individuais."""
        task_info = {
            'method': method_name,
            'args': args,
            'kwargs': kwargs,
            'index': len(self.individual_task_history),
            'success': None,
            'backtrack_attempts': 0,
            'timestamp': time.time()
        }
        self.individual_task_history.append(task_info)
        self.current_task_index = len(self.individual_task_history) - 1
        return self.current_task_index
    
    def start_task_session(self):
        """Inicia uma sessão de tarefas individuais para backtrack."""
        self.task_session_active = True
        self.individual_task_history = []
        self.current_task_index = -1
        logger.info("🚀 Sessão de tarefas individuais iniciada - backtrack habilitado entre métodos")
    
    def end_task_session(self):
        """Finaliza uma sessão de tarefas individuais."""
        self.task_session_active = False
        successful_tasks = sum(1 for task in self.individual_task_history if task.get('success', False))
        total_tasks = len(self.individual_task_history)
        logger.info(f"🏁 Sessão finalizada: {successful_tasks}/{total_tasks} tarefas bem-sucedidas")
        return successful_tasks, total_tasks
    
    # Propriedades de controle do overlay
    @property
    def overlay_enabled(self):
        """Controla se o sistema de overlay está ativo."""
        return self._overlay_enabled
    
    @overlay_enabled.setter
    def overlay_enabled(self, value):
        """Define se o sistema de overlay está ativo."""
        self._overlay_enabled = bool(value)
        # Atualiza também na configuração
        self.config.config["overlay_enabled"] = self._overlay_enabled
    
    @property
    def show_overlay(self):
        """Controla se exibe overlay visual antes dos cliques."""
        return self._show_overlay
    
    @show_overlay.setter
    def show_overlay(self, value):
        """Define se exibe overlay visual antes dos cliques."""
        self._show_overlay = bool(value)
        # Atualiza também na configuração
        self.config.config["show_overlay"] = self._show_overlay
    
    def configure_overlay(self, enabled=None, color=None, duration=None, width=None):
        """
        Configura parâmetros do overlay de forma conveniente.
        
        Args:
            enabled (bool, optional): Se o overlay está habilitado
            color (str, optional): Cor do overlay - opções: 'red', 'blue', 'green', 'yellow', 
                                   'purple', 'orange', 'cyan', 'magenta', 'white', 'black'
            duration (int, optional): Duração em milissegundos (500-5000 recomendado)
            width (int, optional): Largura da linha do overlay (1-10 recomendado)
            
        Examples:
            >>> bot = BotVision()
            >>> bot.configure_overlay(enabled=True, color="blue", duration=2000)
            >>> bot.configure_overlay(color="green", width=6)
            
        Raises:
            ValueError: Se cor inválida for fornecida
        """
        valid_colors = [
            "red", "blue", "green", "yellow", 
            "purple", "orange", "cyan", "magenta", 
            "white", "black"
        ]
        
        if enabled is not None:
            self.overlay_enabled = enabled
            self.show_overlay = enabled
        
        if color is not None:
            if color.lower() not in [c.lower() for c in valid_colors]:
                raise ValueError(f"Cor '{color}' inválida. Cores disponíveis: {', '.join(valid_colors)}")
            self.config.config["overlay_color"] = color.lower()
            
        if duration is not None:
            if not isinstance(duration, (int, float)) or duration <= 0:
                raise ValueError(f"Duração deve ser um número positivo, recebido: {duration}")
            if duration > 10000:
                logger.warning(f"Duração muito alta ({duration}ms). Considere usar menos de 5000ms.")
            self.config.config["overlay_duration"] = int(duration)
            
        if width is not None:
            if not isinstance(width, (int, float)) or width <= 0:
                raise ValueError(f"Largura deve ser um número positivo, recebido: {width}")
            if width > 15:
                logger.warning(f"Largura muito alta ({width}). Considere usar menos de 10.")
            self.config.config["overlay_width"] = int(width)
    
    def get_overlay_config(self):
        """
        Retorna configuração atual do overlay.
        
        Returns:
            dict: Configurações do overlay
        """
        return {
            "enabled": self.overlay_enabled,
            "show_overlay": self.show_overlay,
            "color": self.config.config.get("overlay_color", "red"),
            "duration": self.config.config.get("overlay_duration", 1000),
            "width": self.config.config.get("overlay_width", 4)
        }
    
    @staticmethod
    def get_available_overlay_colors():
        """
        Retorna lista de cores disponíveis para overlay.
        
        Returns:
            list: Lista de cores disponíveis
            
        Examples:
            >>> colors = BotVision.get_available_overlay_colors()
            >>> print("Cores disponíveis:", colors)
        """
        return [
            "red", "blue", "green", "yellow", 
            "purple", "orange", "cyan", "magenta", 
            "white", "black"
        ]
    
    def test_overlay_colors(self, duration=1500):
        """
        Testa todas as cores disponíveis de overlay.
        
        Args:
            duration (int): Duração de cada cor em milissegundos
            
        Examples:
            >>> bot = BotVision()
            >>> bot.test_overlay_colors()  # Mostra cada cor por 1.5 segundos
        """
        from .core.overlay import VisualOverlay
        
        colors = self.get_available_overlay_colors()
        test_region = (400, 300, 200, 100)  # Centro da tela
        
        print("🎨 Testando cores de overlay...")
        print("📍 Olhe para o centro da tela!")
        
        for i, color in enumerate(colors, 1):
            print(f"   {i}. Cor: {color.upper()}")
            overlay = VisualOverlay(color=color, width=6, duration=duration)
            overlay.show(test_region, blocking=True)
            
        print("✅ Teste de cores concluído!")
    
    def _execute_with_individual_backtrack(self, method_name, method_func, *args, **kwargs):
        """
        Executa método individual com capacidade de backtrack.
        
        Args:
            method_name (str): Nome do método ('click_image', 'click_text', etc.)
            method_func (callable): Função do método a ser executada
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            bool: Resultado da execução
        """
        backtrack = kwargs.get('backtrack', False)
        
        # Se backtrack não está habilitado ou não há sessão ativa, executa normalmente
        if not backtrack or not self.task_session_active:
            if backtrack and not self.task_session_active:
                # Auto-inicia sessão se backtrack=True mas sessão não está ativa
                self.start_task_session()
            
            # Remove backtrack dos kwargs para evitar recursão infinita
            execution_kwargs = kwargs.copy()
            execution_kwargs.pop('backtrack', None)
            return method_func(*args, **execution_kwargs)
        
        # Adiciona ao histórico
        task_index = self._add_to_task_history(method_name, args, kwargs)
        
        logger.info(f"🎯 Executando {method_name} (tarefa {task_index + 1}) com backtrack habilitado")
        
        # Remove backtrack dos kwargs para evitar recursão infinita
        execution_kwargs = kwargs.copy()
        execution_kwargs.pop('backtrack', None)
        
        # Tenta executar o método
        success = method_func(*args, **execution_kwargs)
        
        # Atualiza resultado no histórico
        self.individual_task_history[task_index]['success'] = success
        
        if success:
            logger.info(f"✓ {method_name} (tarefa {task_index + 1}) executada com sucesso!")
            return True
        else:
            # Falhou - verifica se pode fazer backtrack
            if task_index > 0:  # Há tarefas anteriores
                current_task = self.individual_task_history[task_index]
                
                if current_task['backtrack_attempts'] < self.max_backtrack_attempts:
                    current_task['backtrack_attempts'] += 1
                    
                    # Executa tarefa anterior
                    prev_task = self.individual_task_history[task_index - 1]
                    logger.info(f"🔄 BACKTRACK: {method_name} (tarefa {task_index + 1}) falhou. "
                              f"Reexecutando tarefa anterior ({prev_task['method']}) e tentando novamente...")
                    
                    # Reexecuta tarefa anterior
                    prev_method_name = prev_task['method']
                    prev_method_func = getattr(self, f"_{prev_method_name}_internal")
                    prev_kwargs = prev_task['kwargs'].copy()
                    prev_kwargs.pop('backtrack', None)  # Remove backtrack para evitar recursão
                    
                    prev_success = prev_method_func(*prev_task['args'], **prev_kwargs)
                    self.individual_task_history[task_index - 1]['success'] = prev_success
                    
                    if prev_success:
                        logger.info(f"✓ Tarefa anterior ({prev_task['method']}) reexecutada com sucesso")
                        
                        # Aguarda um pouco e tenta a tarefa atual novamente
                        time.sleep(0.5)
                        logger.info(f"🔄 Tentando novamente {method_name} (tarefa {task_index + 1}) após backtrack...")
                        
                        retry_success = method_func(*args, **execution_kwargs)
                        self.individual_task_history[task_index]['success'] = retry_success
                        
                        if retry_success:
                            logger.info(f"✓ {method_name} (tarefa {task_index + 1}) bem-sucedida após backtrack!")
                            return True
                        else:
                            logger.warning(f"✗ {method_name} (tarefa {task_index + 1}) ainda falhou após backtrack")
                    else:
                        logger.warning(f"✗ Tarefa anterior ({prev_task['method']}) também falhou na reexecução")
                else:
                    logger.warning(f"✗ {method_name} (tarefa {task_index + 1}) falhou após {self.max_backtrack_attempts} tentativas de backtrack")
            else:
                logger.warning(f"✗ {method_name} (tarefa {task_index + 1}) falhou mas é a primeira tarefa (sem backtrack possível)")
            
            return False

    def execute_tasks(self, tasks):
        """
        Executa uma lista de tarefas sequencialmente.
        
        Args:
            tasks (list): Lista de dicionários com configurações das tarefas
            
        Returns:
            list: Lista de TaskResult com resultados de cada tarefa
            
        Examples:
            >>> # Tarefas básicas
            >>> tasks = [
            ...     {'text': 'Login', 'region': (100, 100, 500, 300)},
            ...     {'image': 'button.png', 'delay': 2}
            ... ]
            >>> 
            >>> # Tarefas avançadas com TODAS as novas funcionalidades:
            >>> advanced_tasks = [
            ...     # 1. Busca de texto OCR
            ...     {
            ...         'text': 'Usuário',
            ...         'region': (100, 100, 500, 300),
            ...         'char_type': 'letters',
            ...         'confidence': 0.8,
            ...         'occurrence': 1,
            ...         'backtrack': True,
            ...         'delay': 1,
            ...         'sendtext': 'admin{tab}password{enter}'
            ...     },
            ...     # 2. Busca de imagem relativa (NOVO!)
            ...     {
            ...         'type': 'relative_image',
            ...         'anchor_image': 'warning_icon.png',
            ...         'target_image': 'ok_button.png',
            ...         'max_distance': 200,
            ...         'confidence': 0.9,
            ...         'target_region': (0, 0, 800, 600),
            ...         'specific': True,
            ...         'backtrack': True,
            ...         'delay': 1
            ...     },
            ...     # 3. Clique em coordenadas específicas (NOVO!)
            ...     {
            ...         'type': 'click',
            ...         'x': 100,
            ...         'y': 200,
            ...         'mouse_button': 'right',
            ...         'delay': 0.5,
            ...         'backtrack': False
            ...     },
            ...     # 4. Digitação de texto (NOVO!)
            ...     {
            ...         'type': 'type_text',
            ...         'text': 'Hello World!',
            ...         'interval': 0.05,
            ...         'delay': 1
            ...     },
            ...     # 5. Comando de teclado (NOVO!)
            ...     {
            ...         'type': 'keyboard_command',
            ...         'command': 'Ctrl+S',
            ...         'delay': 1
            ...     }
            ... ]
            >>> 
            >>> results = bot.execute_tasks(advanced_tasks)
        """
        return self.executor.execute_tasks(tasks)
    
    def find_text(self, text, region=None, filter_type="both", confidence_threshold=75.0, 
                  occurrence=1, max_attempts=3, backtrack=False):
        """
        Encontra texto na tela usando OCR avançado com todas as funcionalidades.
        
        Args:
            text (str): Texto a ser encontrado
            region (tuple, optional): (x, y, width, height) da região de busca
            filter_type (str): Tipo de filtro ("numbers", "letters", "both") - equivale a char_type
            confidence_threshold (float): Limiar de confiança mínimo
            occurrence (int): Qual ocorrência buscar (1 = primeira, 2 = segunda, etc.)
            max_attempts (int): Número máximo de tentativas se backtrack=True
            backtrack (bool): Se deve tentar múltiplas vezes com ajustes
            
        Returns:
            tuple: Coordenadas (x, y, width, height) onde o texto foi encontrado ou None
            
        Examples:
            >>> location = bot.find_text("Confirmar", region=(0, 0, 800, 600), backtrack=True)
            >>> if location:
            ...     print(f"Texto encontrado em: {location}")
        """
        import time
        
        attempts = 0
        while attempts < max_attempts:
            if region is None:
                # Se não especificou região, captura tela inteira
                import pyautogui
                screen = pyautogui.screenshot()
                region = (0, 0, screen.width, screen.height)
                region_img = screen
            else:
                region_img = self.executor._capture_region(region)
            
            found_boxes, confidence_scores, _ = self.ocr_engine.find_text(
                region_img, text, filter_type, confidence_threshold
            )
            
            if found_boxes and len(found_boxes) >= occurrence:
                # Retorna a ocorrência especificada (occurrence-1 pois lista é 0-indexada)
                target_index = occurrence - 1
                if target_index < len(found_boxes):
                    best_box_relative = found_boxes[target_index]
                    
                    # Converte para coordenadas absolutas se necessário
                    if region != (0, 0, region_img.width, region_img.height):
                        return (
                            region[0] + best_box_relative[0],
                            region[1] + best_box_relative[1],
                            best_box_relative[2],
                            best_box_relative[3]
                        )
                    else:
                        return best_box_relative
            
            # Se não encontrou e backtrack está habilitado, tenta novamente
            if backtrack and attempts < max_attempts - 1:
                attempts += 1
                logger.info(f"Tentativa {attempts}/{max_attempts} para encontrar '{text}'")
                
                # Ajusta parâmetros para próxima tentativa
                confidence_threshold = max(60.0, confidence_threshold - 5.0)
                time.sleep(0.5)
            else:
                break
        
        return None
    
    def click_text(self, text, region=None, filter_type="both", delay=0, mouse_button="left", 
                   occurrence=1, backtrack=False, max_attempts=3, sendtext=None, 
                   confidence_threshold=None, show_overlay=None):
        """
        Encontra e clica em texto com funcionalidades avançadas.
        
        Args:
            text (str): Texto a ser clicado
            region (tuple, optional): Região de busca (x, y, width, height)
            filter_type (str): Tipo de filtro ("numbers", "letters", "both")
            delay (float): Delay após o clique em segundos
            mouse_button (str): Tipo de clique do mouse:
                • "left" - Clique simples esquerdo (padrão)
                • "right" - Clique direito
                • "double" ou "double left" - Clique duplo esquerdo
                • "move_to" - Apenas move o mouse sem clicar
            occurrence (int): Qual ocorrência clicar (1=primeira)
            backtrack (bool): Se deve usar backtrack real entre métodos individuais
            max_attempts (int): Número máximo de tentativas
            sendtext (str, optional): Texto para digitar após o clique
            confidence_threshold (float, optional): Limiar de confiança customizado
            show_overlay (bool, optional): Se deve exibir o overlay vermelho antes do clique
                                         Se None, usa a configuração global
            
        Returns:
            bool: True se encontrou e clicou, False caso contrário
        """
        # Usa configuração global se não especificado
        if show_overlay is None:
            show_overlay = self.config.show_overlay
            
        # Se backtrack for True, usa o sistema de backtrack individual
        if backtrack:
            return self._execute_with_individual_backtrack(
                'click_text', self._click_text_internal, text, region, filter_type, 
                delay, mouse_button, occurrence, max_attempts, sendtext, confidence_threshold,
                show_overlay, backtrack=backtrack
            )
        
        # Comportamento original sem backtrack
        return self._click_text_internal(text, region, filter_type, delay, mouse_button, 
                                       occurrence, max_attempts, sendtext, confidence_threshold, show_overlay)
    
    def _click_text_internal(self, text, region=None, filter_type="both", delay=0, mouse_button="left", 
                           occurrence=1, max_attempts=3, sendtext=None, confidence_threshold=None, show_overlay=None):
        """Versão interna do click_text sem backtrack (para uso no sistema de backtrack)."""
        # Usa configuração global se não especificado
        if show_overlay is None:
            show_overlay = self.config.show_overlay
        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            
            try:
                if attempts > 1:
                    logger.info(f"Tentativa {attempts}/{max_attempts} para clicar em '{text}'")
                
                # Usa limiar customizado se fornecido, senão usa da configuração
                threshold = confidence_threshold or self.config.confidence_threshold
                
                location = self.find_text(text, region, filter_type, threshold, occurrence)
                
                if location:
                    # Cria task temporária para usar o executor
                    temp_task = {
                        'mouse_button': mouse_button,
                        'delay': delay,
                        'sendtext': sendtext,
                        'show_overlay': show_overlay
                    }
                    
                    try:
                        self.executor._perform_action(temp_task, location)
                        
                        # Processa sendtext se fornecido
                        if sendtext:
                            self._process_sendtext(sendtext)
                        
                        return True
                    except Exception as e:
                        logger.error(f"Erro ao clicar em texto: {e}")
                        if attempts >= max_attempts:
                            return False
                        time.sleep(0.5)
                else:
                    logger.warning(f"Texto '{text}' não encontrado na tentativa {attempts}")
                    if attempts < max_attempts:
                        time.sleep(0.5)
                        
            except Exception as e:
                logger.error(f"Erro na tentativa {attempts} para '{text}': {e}")
                if attempts >= max_attempts:
                    return False
                time.sleep(0.5)
        
        return False
    
    def _click_image_internal(self, image_path, region=None, confidence=0.9, delay=0, mouse_button="left",
                            max_attempts=3, specific=True, sendtext=None, show_overlay=None):
        """Versão interna do click_image sem backtrack (para uso no sistema de backtrack)."""
        # Usa configuração global se não especificado
        if show_overlay is None:
            show_overlay = self.config.show_overlay
            
        location = self.find_image(image_path, region, confidence, max_attempts, 
                                 False, specific)  # backtrack=False para find_image
        
        if location:
            # Cria task temporária para usar o executor
            temp_task = {
                'mouse_button': mouse_button,
                'delay': delay,
                'sendtext': sendtext,
                'show_overlay': show_overlay
            }
            
            try:
                self.executor._perform_action(temp_task, location)
                
                # Processa sendtext se fornecido
                if sendtext:
                    self._process_sendtext(sendtext)
                
                return True
            except Exception as e:
                logger.error(f"Erro ao clicar em imagem: {e}")
                return False
        
        return False

    def type_text(self, text):
        """
        Digita texto na posição atual do cursor.
        
        Args:
            text (str): Texto a ser digitado (suporta comandos especiais)
            
        Examples:
            >>> bot.type_text("Hello World")
            >>> bot.type_text("{ctrl}a{del}New Text{enter}")
        """
        try:
            self.executor._process_sendtext(text)
            return True
        except Exception as e:
            logger.error(f"Erro ao digitar texto: {e}")
            return False

    def extract_text_from_region(self, region=None, filter_type="both", confidence_threshold=50.0, 
                                 return_full_data=False, max_attempts=3, backtrack=False):
        """
        Extrai todo o texto encontrado em uma região específica da tela.
        
        Args:
            region (tuple, optional): (x, y, width, height) da região para extrair texto.
                                    Se None, extrai da tela inteira
            filter_type (str): Tipo de filtro para o texto:
                • "numbers" - Apenas números
                • "letters" - Apenas letras
                • "both" - Números e letras (padrão)
            confidence_threshold (float): Limiar mínimo de confiança (0-100)
            return_full_data (bool): Se True, retorna dados completos com coordenadas e confiança
            max_attempts (int): Número máximo de tentativas se backtrack=True
            backtrack (bool): Se deve tentar múltiplas vezes com ajustes
            
        Returns:
            Se return_full_data=False:
                list: Lista de strings com todo texto encontrado
            Se return_full_data=True:
                list: Lista de dicionários com:
                    - 'text': Texto encontrado
                    - 'confidence': Nível de confiança (0-100)
                    - 'box': Coordenadas (x, y, width, height)
                    - 'absolute_box': Coordenadas absolutas na tela
            
        Examples:
            Extração simples:
            >>> texts = bot.extract_text_from_region(region=(100, 100, 400, 300))
            >>> print("Textos encontrados:", texts)
            
            Extração com dados completos:
            >>> data = bot.extract_text_from_region(
            ...     region=(100, 100, 400, 300),
            ...     return_full_data=True,
            ...     confidence_threshold=70.0
            ... )
            >>> for item in data:
            ...     print(f"'{item['text']}' - Confiança: {item['confidence']:.1f}% - Posição: {item['absolute_box']}")
            
            Apenas números:
            >>> numbers = bot.extract_text_from_region(
            ...     region=(50, 50, 200, 100),
            ...     filter_type="numbers"
            ... )
        """
        import time
        
        attempts = 0
        while attempts < max_attempts:
            try:
                if region is None:
                    # Se não especificou região, captura tela inteira
                    import pyautogui
                    screen = pyautogui.screenshot()
                    region = (0, 0, screen.width, screen.height)
                    region_img = screen
                else:
                    region_img = self.executor._capture_region(region)
                
                # Usa o método extract_all_text do OCR engine
                ocr_results = self.ocr_engine.extract_all_text(region_img, filter_type)
                
                # Filtra por confiança
                filtered_results = [
                    result for result in ocr_results 
                    if result.confidence >= confidence_threshold
                ]
                
                if not filtered_results and backtrack and attempts < max_attempts - 1:
                    # Se não encontrou nada e backtrack está habilitado, ajusta parâmetros
                    attempts += 1
                    logger.info(f"Tentativa {attempts}/{max_attempts} para extração de texto")
                    confidence_threshold = max(30.0, confidence_threshold - 10.0)
                    time.sleep(0.5)
                    continue
                
                if return_full_data:
                    # Retorna dados completos com coordenadas absolutas
                    full_data = []
                    for result in filtered_results:
                        absolute_box = (
                            region[0] + result.box[0],
                            region[1] + result.box[1],
                            result.box[2],
                            result.box[3]
                        ) if region != (0, 0, region_img.width, region_img.height) else result.box
                        
                        full_data.append({
                            'text': result.text,
                            'confidence': result.confidence,
                            'box': result.box,  # Coordenadas relativas à região
                            'absolute_box': absolute_box  # Coordenadas absolutas na tela
                        })
                    
                    return full_data
                else:
                    # Retorna apenas os textos
                    return [result.text for result in filtered_results]
                    
            except Exception as e:
                logger.error(f"Erro na tentativa {attempts} para extração de texto: {e}")
                if backtrack and attempts < max_attempts - 1:
                    attempts += 1
                    time.sleep(0.5)
                else:
                    break
        
        # Se chegou aqui, falhou
        return [] if not return_full_data else []

    def get_last_extracted_text(self):
        """
        Obtém o último texto extraído quando usado em listas de tarefas.
        
        Returns:
            list: Último resultado de extração de texto, ou None se nenhuma extração foi feita
            
        Examples:
            >>> tasks = [
            ...     {
            ...         'type': 'extract_text',
            ...         'region': (100, 100, 400, 300),
            ...         'filter_type': 'both'
            ...     }
            ... ]
            >>> results = bot.execute_tasks(tasks)
            >>> extracted_texts = bot.get_last_extracted_text()
            >>> print("Textos encontrados:", extracted_texts)
        """
        return getattr(self.executor, 'last_extracted_text', None)
    
    def find_image(self, image_path, region=None, confidence=0.9, max_attempts=3, 
                   backtrack=False, specific=True, scales=None):
        """
        Encontra imagem na tela com todas as funcionalidades avançadas.
        
        Args:
            image_path (str): Caminho para a imagem
            region (tuple, optional): Região de busca
            confidence (float): Nível de confiança
            max_attempts (int): Número máximo de tentativas se backtrack=True
            backtrack (bool): Se deve tentar múltiplas vezes com ajustes
            specific (bool): Se True, busca na região; se False, busca na tela inteira + variações de escala
            scales (list, optional): Lista de escalas para tentar (ex: [1.0, 0.95, 1.05])
            
        Returns:
            tuple: Coordenadas da imagem ou None
        """
        import time
        
        if scales is None:
            scales = [1.0, 0.95, 1.05] if not specific else [1.0]
        
        attempts = 0
        while attempts < max_attempts:
            try:
                # Tenta com diferentes escalas se não for específico
                for scale in scales:
                    try:
                        if scale != 1.0 and not specific:
                            # Implementa redimensionamento da imagem de referência
                            from PIL import Image
                            import os
                            ref_img = Image.open(image_path)
                            new_width = int(ref_img.width * scale)
                            new_height = int(ref_img.height * scale)
                            scaled_img = ref_img.resize((new_width, new_height))
                            
                            # Salva temporariamente
                            temp_path = f"temp_scaled_{scale}_{attempts}.png"
                            scaled_img.save(temp_path)
                            
                            # NOVA LÓGICA: specific controla onde buscar
                            if specific and region:
                                # Se específico E tem região, busca na região
                                location = self.executor._locate_image_with_retry(temp_path, region, confidence)
                            else:
                                # Se não específico OU sem região, busca na tela inteira
                                location = self.executor._locate_image_with_retry(temp_path, None, confidence)
                            
                            # Remove arquivo temporário
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                        else:
                            # NOVA LÓGICA: specific controla onde buscar
                            if specific and region:
                                # Se específico E tem região, busca na região
                                logger.info(f"Buscando imagem na região {region} (specific=True)")
                                location = self.executor._locate_image_with_retry(image_path, region, confidence)
                            else:
                                # Se não específico OU sem região, busca na tela inteira
                                logger.info(f"Buscando imagem em toda a tela (specific=False)")
                                location = self.executor._locate_image_with_retry(image_path, None, confidence)
                        
                        if location:
                            return location
                            
                    except Exception as e:
                        logger.debug(f"Erro ao buscar imagem com escala {scale}: {e}")
                        continue
                # Se não encontrou e backtrack está habilitado, ajusta parâmetros
                if backtrack and attempts < max_attempts - 1:
                    attempts += 1
                    logger.info(f"Tentativa {attempts}/{max_attempts} para encontrar imagem")
                    
                    # Reduz confiança gradualmente
                    confidence = max(0.7, confidence - 0.05)
                    time.sleep(0.5)
                else:
                    break
                    
            except Exception as e:
                logger.error(f"Erro ao buscar imagem: {e}")
                if not backtrack:
                    break
        
        return None
    
    def click_image(self, image_path, region=None, confidence=0.9, delay=0, mouse_button="left",
                    max_attempts=3, backtrack=False, specific=True, sendtext=None, show_overlay=None):
        """
        Encontra e clica em imagem com todas as funcionalidades avançadas.
        
        Args:
            image_path (str): Caminho para a imagem
            region (tuple, optional): Região de busca (x, y, width, height)
            confidence (float): Nível de confiança (0.0-1.0)
            delay (float): Delay após o clique em segundos
            mouse_button (str): Tipo de clique do mouse:
                • "left" - Clique simples esquerdo (padrão)
                • "right" - Clique direito
                • "double" ou "double left" - Clique duplo esquerdo
                • "move_to" - Apenas move o mouse sem clicar
            max_attempts (int): Número máximo de tentativas se backtrack=True
            backtrack (bool): Se deve usar backtrack real entre métodos individuais
            specific (bool): Se True, busca exata; se False, permite variações
            sendtext (str, optional): Texto para digitar após o clique
            show_overlay (bool, optional): Se deve exibir o overlay vermelho antes do clique
                                         Se None, usa a configuração global
            
        Returns:
            bool: True se encontrou e clicou, False caso contrário
        """
        # Usa configuração global se não especificado
        if show_overlay is None:
            show_overlay = self.config.show_overlay
            
        # Se backtrack for True, usa o sistema de backtrack individual
        if backtrack:
            return self._execute_with_individual_backtrack(
                'click_image', self._click_image_internal, image_path, region, confidence, 
                delay, mouse_button, max_attempts, specific, sendtext, show_overlay, backtrack=backtrack
            )
        
        # Comportamento original sem backtrack
        return self._click_image_internal(image_path, region, confidence, delay, mouse_button,
                                        max_attempts, specific, sendtext, show_overlay)

    def click_at(self, location, mouse_button="left", delay=0, show_overlay=None):
        """
        Clica em coordenadas específicas da tela.
        
        Args:
            location (tuple): (x, y, width, height) da localização
            mouse_button (str): Botão do mouse ("left", "right", "double", "move_to")
            delay (float): Delay após o clique
            show_overlay (bool, optional): Se deve exibir o overlay vermelho antes do clique
                                         Se None, usa a configuração global
            
        Returns:
            bool: True se clicou com sucesso
            
        Examples:
            >>> bot.click_at((100, 200, 50, 30), mouse_button='left', delay=1)
        """
        try:
            # Usa configuração global se não especificado
            if show_overlay is None:
                show_overlay = self.config.show_overlay
                
            # Cria task temporária para usar o executor
            temp_task = {
                'mouse_button': mouse_button,
                'delay': delay,
                'show_overlay': show_overlay
            }
            
            self.executor._perform_action(temp_task, location)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao clicar em coordenadas {location}: {e}")
            return False

    def find_relative_image(self, anchor_image, target_image, max_distance=200, 
                           confidence=0.9, target_region=None):
        """
        Encontra uma imagem target próxima a uma imagem anchor.
        
        Args:
            anchor_image (str): Caminho para a imagem âncora (única na tela)
            target_image (str): Caminho para a imagem alvo (pode ter múltiplas)
            max_distance (int): Distância máxima em pixels da âncora ao target
            confidence (float): Nível de confiança para detecção (0.0-1.0)
            target_region (tuple, optional): Região específica para buscar target (x, y, width, height)
            
        Returns:
            tuple: Localização da imagem target mais próxima da anchor ou None
            
        Examples:
            >>> location = bot.find_relative_image('anchor.png', 'target.png', max_distance=150)
            >>> if location:
            ...     print(f"Target encontrado próximo à âncora: {location}")
        """
        try:
            return self.executor.relative_detector.locate_relative_image(
                anchor_image, target_image, confidence, max_distance, target_region
            )
        except Exception as e:
            logger.error(f"Erro na busca de imagem relativa: {e}")
            return None

    def click_relative_image(self, anchor_image, target_image, max_distance=200, 
                           confidence=0.9, target_region=None, delay=0, 
                           mouse_button="left", backtrack=False, max_attempts=3):
        """
        Clica em uma imagem target próxima a uma imagem anchor.
        
        Args:
            anchor_image (str): Caminho para a imagem âncora
            target_image (str): Caminho para a imagem alvo
            max_distance (int): Distância máxima em pixels
            confidence (float): Nível de confiança (0.0-1.0)
            target_region (tuple, optional): Região para buscar target (x, y, width, height)
            delay (float): Delay após o clique em segundos
            mouse_button (str): Tipo de clique do mouse:
                • "left" - Clique simples esquerdo (padrão)
                • "right" - Clique direito  
                • "double" ou "double left" - Clique duplo esquerdo
                • "move_to" - Apenas move o mouse sem clicar
            backtrack (bool): Se deve usar backtrack em caso de falha
            max_attempts (int): Número máximo de tentativas
            
        Returns:
            bool: True se encontrou e clicou, False caso contrário
            
        Examples:
            >>> # Clique simples esquerdo (padrão)
            >>> success = bot.click_relative_image('anchor.png', 'target.png', 
            ...                                  max_distance=150, mouse_button="left")
            
            >>> # Clique direito
            >>> success = bot.click_relative_image('anchor.png', 'target.png',
            ...                                  mouse_button="right", backtrack=True)
            
            >>> # Clique duplo esquerdo
            >>> success = bot.click_relative_image('anchor.png', 'target.png',
            ...                                  mouse_button="double", delay=1.0)
            
            >>> # Apenas mover o mouse para a posição (sem clicar)
            >>> success = bot.click_relative_image('anchor.png', 'target.png',
            ...                                  mouse_button="move_to", delay=0.5)
        """
        if backtrack:
            return self._execute_with_individual_backtrack(
                'click_relative_image', self._click_relative_image_internal,
                anchor_image, target_image, max_distance, confidence, 
                target_region, delay, mouse_button, max_attempts, backtrack=backtrack
            )
        
        return self._click_relative_image_internal(
            anchor_image, target_image, max_distance, confidence, 
            target_region, delay, mouse_button, max_attempts
        )

    def _click_relative_image_internal(self, anchor_image, target_image, max_distance, 
                                     confidence, target_region, delay, mouse_button, max_attempts):
        """Implementação interna do clique em imagem relativa."""
        for attempt in range(max_attempts):
            location = self.find_relative_image(anchor_image, target_image, 
                                              max_distance, confidence, target_region)
            if location:
                temp_task = {
                    'mouse_button': mouse_button,
                    'delay': delay
                }
                self.executor._perform_action(temp_task, location)
                return True
            
            if attempt < max_attempts - 1:
                time.sleep(0.5)
        
        return False

    def click_coordinates(self, x, y, delay=0, mouse_button="left", backtrack=False):
        """
        Clica em coordenadas específicas da tela.
        
        Args:
            x (int): Coordenada X
            y (int): Coordenada Y
            delay (float): Delay após o clique
            mouse_button (str): Botão do mouse ("left", "right", "double", "move_to")
            backtrack (bool): Se deve usar backtrack
            
        Returns:
            bool: True se clicou com sucesso
            
        Examples:
            >>> success = bot.click_coordinates(100, 200, delay=1, backtrack=True)
        """
        if backtrack:
            return self._execute_with_individual_backtrack(
                'click_coordinates', self._click_coordinates_internal,
                x, y, delay, mouse_button, backtrack=backtrack
            )
        
        return self._click_coordinates_internal(x, y, delay, mouse_button)

    def _click_coordinates_internal(self, x, y, delay, mouse_button):
        """Implementação interna do clique em coordenadas."""
        try:
            location = (x, y, 1, 1)  # Cria região pequena
            temp_task = {
                'mouse_button': mouse_button,
                'delay': delay
            }
            self.executor._perform_action(temp_task, location)
            return True
        except Exception as e:
            logger.error(f"Erro ao clicar em coordenadas ({x}, {y}): {e}")
            return False

    def type_text(self, text, interval=0.05, delay=0, backtrack=False):
        """
        Digite texto com intervalo entre caracteres.
        
        Args:
            text (str): Texto a ser digitado
            interval (float): Intervalo entre caracteres em segundos
            delay (float): Delay após digitação
            backtrack (bool): Se deve usar backtrack
            
        Returns:
            bool: True se digitou com sucesso
            
        Examples:
            >>> success = bot.type_text('Hello World!', interval=0.05, backtrack=True)
            >>> success = bot.type_text('{ctrl}a{del}New text', backtrack=True)
        """
        if backtrack:
            return self._execute_with_individual_backtrack(
                'type_text', self._type_text_internal,
                text, interval, delay, backtrack=backtrack
            )
        
        return self._type_text_internal(text, interval, delay)

    def _type_text_internal(self, text, interval, delay):
        """Implementação interna da digitação de texto."""
        try:
            # Verifica se tem comandos especiais
            if any(cmd in text.lower() for cmd in ['{ctrl}', '{del}', '{tab}', '{enter}']):
                self.executor.keyboard_commander.process_sendtext_command(text)
            else:
                self.executor.keyboard_commander.type_text(text, interval)
            
            if delay > 0:
                time.sleep(delay)
            return True
        except Exception as e:
            logger.error(f"Erro ao digitar texto '{text}': {e}")
            return False

    def keyboard_command(self, command, delay=0, backtrack=False):
        """
        Executa um comando de teclado.
        
        Args:
            command (str): Nome do comando a ser executado
            delay (float): Delay após comando
            backtrack (bool): Se deve usar backtrack
            
        Returns:
            bool: True se comando foi executado com sucesso
            
        Examples:
            >>> success = bot.keyboard_command('Ctrl+S', delay=1, backtrack=True)
            >>> success = bot.keyboard_command('F7', backtrack=True)  # Oracle Forms
        """
        if backtrack:
            return self._execute_with_individual_backtrack(
                'keyboard_command', self._keyboard_command_internal,
                command, delay, backtrack=backtrack
            )
        
        return self._keyboard_command_internal(command, delay)

    def _keyboard_command_internal(self, command, delay):
        """Implementação interna do comando de teclado."""
        try:
            success = self.executor.keyboard_commander.execute_command(command)
            if delay > 0:
                time.sleep(delay)
            return success
        except Exception as e:
            logger.error(f"Erro ao executar comando '{command}': {e}")
            return False

    def get_available_keyboard_commands(self):
        """
        Retorna lista de comandos de teclado disponíveis.
        
        Returns:
            list: Lista com todos os comandos disponíveis
            
        Examples:
            >>> commands = bot.get_available_keyboard_commands()
            >>> print(f"Comandos disponíveis: {len(commands)}")
            >>> for cmd in commands[:10]:  # Mostra primeiros 10
            ...     print(f"  - {cmd}")
        """
        return self.executor.keyboard_commander.get_available_commands()

    def _process_sendtext(self, sendtext):
        """
        Processa comandos especiais no sendtext e digita o texto.
        
        Args:
            sendtext (str): Texto com comandos especiais como {ctrl}a, {del}, etc.
        """
        import pyautogui
        import pyperclip
        import time
        
        text_to_write = sendtext
        commands_processed = True
        
        while commands_processed:
            commands_processed = False
            lower_text = text_to_write.lower()
            
            if lower_text.startswith('{ctrl}a'):
                pyautogui.hotkey('ctrl', 'a')
                text_to_write = text_to_write[7:]  # Remove '{ctrl}a'
                commands_processed = True
                time.sleep(0.1)
                
            elif lower_text.startswith('{del}'):
                pyautogui.press('delete')
                text_to_write = text_to_write[5:]  # Remove '{del}'
                commands_processed = True
                time.sleep(0.1)
                
            elif lower_text.startswith('{tab}'):
                pyautogui.press('tab')
                text_to_write = text_to_write[5:]  # Remove '{tab}'
                commands_processed = True
                time.sleep(0.1)
                
            elif lower_text.startswith('{enter}'):
                pyautogui.press('enter')
                text_to_write = text_to_write[7:]  # Remove '{enter}'
                commands_processed = True
                time.sleep(0.1)
        
        # Digita o texto restante usando clipboard para maior confiabilidade
        if text_to_write:
            try:
                pyperclip.copy(text_to_write)
                pyautogui.hotkey('ctrl', 'v')
            except Exception as e:
                # Fallback para digitação direta
                pyautogui.write(text_to_write)
            time.sleep(0.1)

    def execute_with_backtrack_between_tasks(self, tasks_list):
        """
        Executa múltiplas tarefas individuais com backtrack real entre elas.
        
        Quando uma tarefa falha, volta para a anterior, executa-a, 
        e depois retorna para tentar a que falhou novamente.
        
        Args:
            tasks_list (list): Lista de dicionários com configurações de tarefas individuais
                              Cada item deve ter: {'type': 'text'|'image', 'params': {...}}
                              
        Returns:
            list: Lista de resultados booleanos
        """
        if not tasks_list:
            return []
            
        results = []
        i = 0
        backtrack_stack = []
        task_failures = {}
        
        logger.info(f"🚀 Iniciando execução com backtrack entre {len(tasks_list)} tarefas individuais")
        
        while i < len(tasks_list):
            task_config = tasks_list[i]
            task_type = task_config.get('type')
            params = task_config.get('params', {})
            backtrack_enabled = params.get('backtrack', True)
            
            logger.info(f"📋 Executando tarefa {i+1}/{len(tasks_list)} - Tipo: {task_type}")
            
            success = False
            
            try:
                if task_type == 'text':
                    # Remove backtrack dos params para evitar recursão
                    text_params = params.copy()
                    text_params.pop('backtrack', None)
                    success = self.click_text(**text_params)
                    
                elif task_type == 'image':
                    # Remove backtrack dos params para evitar recursão
                    image_params = params.copy()
                    image_params.pop('backtrack', None)
                    success = self.click_image(**image_params)
                    
                else:
                    logger.error(f"Tipo de tarefa desconhecido: {task_type}")
                    success = False
                    
            except Exception as e:
                logger.error(f"Erro ao executar tarefa {i+1}: {e}")
                success = False
            
            # Ajusta lista de resultados
            while len(results) <= i:
                results.append(False)
            results[i] = success
            
            if success:
                logger.info(f"✓ Tarefa {i+1}/{len(tasks_list)} executada com sucesso!")
                
                # Verifica se há backtracks pendentes na pilha
                if backtrack_stack:
                    # Remove o item da pilha e volta para a tarefa original que falhou
                    original_failed_task = backtrack_stack.pop()
                    logger.info(f"🔄 Retornando para a tarefa {original_failed_task+1} que originalmente falhou após backtrack")
                    i = original_failed_task
                    # Reseta as tentativas de falha para a tarefa original
                    if i in task_failures:
                        task_failures[i] = 0
                else:
                    # Comportamento normal: avança para a próxima tarefa
                    i += 1
                    
            else:
                # Tarefa falhou, verifica backtracking
                if backtrack_enabled and i > 0:
                    # Gerencia backtracking
                    task_failures.setdefault(i, 0)
                    task_failures[i] += 1
                    
                    if task_failures[i] <= 2:  # Limita tentativas de backtrack
                        # Adiciona a tarefa atual na pilha de backtrack (para retornar depois)
                        if i not in backtrack_stack:  # Evita duplicatas
                            backtrack_stack.append(i)
                            logger.info(f"📌 Tarefa {i+1} adicionada à pilha de backtrack para reexecução posterior")
                        
                        prev_task_type = tasks_list[i-1].get('type', 'unknown')
                        logger.info(f"✗ Tarefa {i+1}/{len(tasks_list)} ({task_type}) falhou. "
                                  f"BACKTRACKING para tarefa {i}/{len(tasks_list)} ({prev_task_type})")
                        i -= 1  # Volta para tarefa anterior (ESTA É A LINHA CHAVE!)
                    else:
                        logger.info(f"✗ Tarefa {i+1}/{len(tasks_list)} falhou "
                                  f"após múltiplas tentativas de backtracking. Avançando.")
                        # Remove da pilha se estiver lá
                        if i in backtrack_stack:
                            backtrack_stack.remove(i)
                        i += 1
                else:
                    # Sem backtrack ou primeira tarefa
                    if backtrack_enabled:
                        logger.info(f"✗ Tarefa {i+1}/{len(tasks_list)} falhou "
                                  f"mas é a primeira tarefa. Avançando.")
                    else:
                        logger.info(f"✗ Tarefa {i+1}/{len(tasks_list)} falhou "
                                  f"e tem 'backtrack': False. Avançando.")
                    i += 1
        
        successful_tasks = sum(1 for r in results if r)
        logger.info(f"🏁 Execução concluída: {successful_tasks}/{len(results)} tarefas bem-sucedidas")
        
        return results

# NOVAS FUNÇÕES DE CONVENIÊNCIA COM BACKTRACK INDIVIDUAL

def start_individual_session(config=None):
    """
    Inicia uma sessão de tarefas individuais com backtrack.
    
    Args:
        config (dict, optional): Configuração customizada
        
    Returns:
        BotVision: Instância configurada para backtrack individual
    """
    bot = BotVision(config)
    bot.start_task_session()
    return bot


def run_individual_tasks_with_backtrack(task_functions, config=None):
    """
    Executa uma lista de funções de tarefas individuais com backtrack automático.
    
    Args:
        task_functions (list): Lista de tuplas (função, args, kwargs)
        config (dict, optional): Configuração customizada
        
    Returns:
        tuple: (sucessos, total, bot_instance)
        
    Examples:
        >>> tasks = [
        ...     (lambda bot: bot.click_image('btn.png', backtrack=True), (), {}),
        ...     (lambda bot: bot.click_text('Save', backtrack=True), (), {}),
        ... ]
        >>> success, total, bot = run_individual_tasks_with_backtrack(tasks)
    """
    bot = BotVision(config)
    bot.start_task_session()
    
    results = []
    for i, (func, args, kwargs) in enumerate(task_functions):
        try:
            result = func(bot, *args, **kwargs)
            results.append(result)
            logger.info(f"Tarefa {i+1}: {'✓ Sucesso' if result else '✗ Falhou'}")
        except Exception as e:
            logger.error(f"Erro na tarefa {i+1}: {e}")
            results.append(False)
    
    successful, total = bot.end_task_session()
    return successful, total, bot


# Função principal compatível com código legado
def execute_tasks(tasks, config=None):
    """
    Função principal para executar lista de tarefas.
    
    Suporta tanto listas simples quanto listas de listas (múltiplos conjuntos).
    Esta é a função que usuários migrados do código original vão usar.
    
    Args:
        tasks (list): Lista de tarefas de automação ou lista de listas
        config (dict, optional): Configuração customizada
        
    Returns:
        list: Lista de TaskResult ou lista de listas de TaskResult
        
    Examples:
        Lista simples:
        >>> tasks = [{'text': 'Login', 'region': (100, 100, 500, 300)}]
        >>> results = execute_tasks(tasks)
        
        Múltiplas listas:
        >>> task_sets = [
        ...     [{'text': 'Login', 'region': (100, 100, 500, 300)}],
        ...     [{'text': 'Save', 'region': (200, 200, 600, 400)}]
        ... ]
        >>> results = execute_tasks(task_sets)
    """
    if not isinstance(tasks, list):
        logger.error(f"As tarefas devem ser uma lista. Tipo recebido: {type(tasks)}")
        return []
    
    if not tasks:
        logger.info("Lista de tarefas vazia.")
        return []
    
    # Verifica se é lista de listas
    if isinstance(tasks[0], list):
        # Múltiplos conjuntos de tarefas
        logger.info(f"Detectados múltiplos conjuntos de tarefas ({len(tasks)} conjuntos). Executando sequencialmente.")
        
        all_results = []
        for i, task_list in enumerate(tasks):
            if isinstance(task_list, list):
                logger.info(f"--- Iniciando conjunto de tarefas {i+1}/{len(tasks)} ({len(task_list)} tarefas) ---")
                bot = BotVision(config)
                results = bot.execute_tasks(task_list)
                all_results.append(results)
                logger.info(f"--- Finalizado conjunto de tarefas {i+1}/{len(tasks)} ---")
            else:
                logger.warning(f"Item {i} na lista principal não é uma lista de tarefas. Pulando.")
                all_results.append([])
        
        return all_results
    else:
        # Lista simples de tarefas
        bot = BotVision(config)
        return bot.execute_tasks(tasks)


# Função adicional para compatibilidade total com click_images original
def click_images(tasks, default_confidence=0.9, default_margin=50):
    """
    Função para compatibilidade total com código legado.
    
    Esta função replica exatamente o comportamento da função click_images
    do bot_vision.py original, incluindo suporte a listas de listas.
    
    Args:
        tasks: Lista de tarefas ou lista de listas de tarefas
        default_confidence (float): Confiança padrão para detecção de imagens
        default_margin (int): Margem padrão (mantido para compatibilidade)
        
    Returns:
        list: Lista de resultados
    """
    # Cria configuração com valores padrão compatíveis
    config = {
        'default_confidence': default_confidence,
        'default_margin': default_margin,
        'tesseract_path': r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        'tessdata_path': r"C:\Program Files\Tesseract-OCR\tessdata"
    }
    
    return execute_tasks(tasks, config)


# Funções standalone para compatibilidade 100% com o código original
def locate_image_with_retry(image_path: str, region=None, confidence=0.9, max_attempts=3, scales=None):
    """
    Função standalone que replica exatamente a função original do bot_vision.py.
    Tenta localizar uma imagem com diferentes escalas e níveis de confiança.
    """
    executor = TaskExecutor()
    return executor._locate_image_with_retry(image_path, region, confidence, max_attempts, scales)


# Funções de conveniência standalone - NOVAS FUNCIONALIDADES
def find_relative_image(anchor_image, target_image, max_distance=200, confidence=0.9, target_region=None):
    """
    Função standalone para encontrar imagem relativa.
    
    Args:
        anchor_image (str): Caminho para imagem âncora
        target_image (str): Caminho para imagem target
        max_distance (int): Distância máxima em pixels
        confidence (float): Nível de confiança
        target_region (tuple, optional): Região para buscar target
        
    Returns:
        tuple: Localização da imagem ou None
        
    Examples:
        >>> location = find_relative_image('anchor.png', 'target.png')
    """
    bot = BotVision()
    return bot.find_relative_image(anchor_image, target_image, max_distance, confidence, target_region)


def click_relative_image(anchor_image, target_image, max_distance=200, confidence=0.9, 
                        target_region=None, delay=0, mouse_button="left", backtrack=False):
    """
    Função standalone para clicar em imagem relativa.
    
    Args:
        anchor_image (str): Caminho para imagem âncora
        target_image (str): Caminho para imagem target  
        max_distance (int): Distância máxima em pixels
        confidence (float): Nível de confiança (0.0-1.0)
        target_region (tuple, optional): Região para buscar target (x, y, width, height)
        delay (float): Delay após clique em segundos
        mouse_button (str): Tipo de clique do mouse:
            • "left" - Clique simples esquerdo (padrão)
            • "right" - Clique direito
            • "double" ou "double left" - Clique duplo esquerdo
            • "move_to" - Apenas move o mouse sem clicar
        backtrack (bool): Se deve usar backtrack em caso de falha
        
    Returns:
        bool: True se clicou com sucesso, False caso contrário
        
    Examples:
        >>> # Clique simples esquerdo
        >>> success = click_relative_image('anchor.png', 'target.png')
        
        >>> # Clique direito
        >>> success = click_relative_image('anchor.png', 'target.png', 
        ...                              mouse_button="right", backtrack=True)
        
        >>> # Clique duplo esquerdo  
        >>> success = click_relative_image('anchor.png', 'target.png',
        ...                              mouse_button="double", delay=1.0)
        
        >>> # Apenas move o mouse para a posição (sem clicar)
        >>> success = click_relative_image('anchor.png', 'target.png',
        ...                              mouse_button="move_to", delay=0.5)
    """
    bot = BotVision()
    return bot.click_relative_image(anchor_image, target_image, max_distance, confidence, 
                                   target_region, delay, mouse_button, backtrack)


def click_coordinates(x, y, delay=0, mouse_button="left", backtrack=False):
    """
    Função standalone para clicar em coordenadas específicas.
    
    Args:
        x (int): Coordenada X
        y (int): Coordenada Y
        delay (float): Delay após clique em segundos
        mouse_button (str): Tipo de clique do mouse:
            • "left" - Clique simples esquerdo (padrão)
            • "right" - Clique direito
            • "double" ou "double left" - Clique duplo esquerdo
            • "move_to" - Apenas move o mouse sem clicar
        backtrack (bool): Se deve usar backtrack em caso de falha
        
    Returns:
        bool: True se clicou com sucesso, False caso contrário
        
    Examples:
        >>> # Clique simples
        >>> success = click_coordinates(100, 200, delay=1)
        
        >>> # Clique direito
        >>> success = click_coordinates(100, 200, mouse_button="right", backtrack=True)
        
        >>> # Apenas move o mouse para a posição (sem clicar)
        >>> success = click_coordinates(100, 200, mouse_button="move_to", delay=0.5)
    """
    bot = BotVision()
    return bot.click_coordinates(x, y, delay, mouse_button, backtrack)


def type_text_standalone(text, interval=0.05, delay=0, backtrack=False):
    """
    Função standalone para digitar texto.
    
    Args:
        text (str): Texto a digitar
        interval (float): Intervalo entre caracteres
        delay (float): Delay após digitação
        backtrack (bool): Se deve usar backtrack
        
    Returns:
        bool: True se digitou com sucesso
        
    Examples:
        >>> success = type_text_standalone('Hello World!', backtrack=True)
        >>> success = type_text_standalone('{ctrl}a{del}New text', backtrack=True)
    """
    bot = BotVision()
    return bot.type_text(text, interval, delay, backtrack)


def keyboard_command_standalone(command, delay=0, backtrack=False):
    """
    Função standalone para executar comando de teclado.
    
    Args:
        command (str): Comando a executar
        delay (float): Delay após comando
        backtrack (bool): Se deve usar backtrack
        
    Returns:
        bool: True se executou com sucesso
        
    Examples:
        >>> success = keyboard_command_standalone('Ctrl+S', delay=1, backtrack=True)
        >>> success = keyboard_command_standalone('F7', backtrack=True)
    """
    bot = BotVision()
    return bot.keyboard_command(command, delay, backtrack)


def get_available_keyboard_commands():
    """
    Função standalone para obter comandos de teclado disponíveis.
    
    Returns:
        list: Lista de comandos disponíveis
        
    Examples:
        >>> commands = get_available_keyboard_commands()
        >>> print(f"Total de comandos: {len(commands)}")
    """
    bot = BotVision()
    return bot.get_available_keyboard_commands()


def extract_text_from_region_standalone(region=None, filter_type="both", confidence_threshold=50.0, 
                                        return_full_data=False, max_attempts=3, backtrack=False, config=None):
    """
    Função standalone para extrair texto de uma região específica da tela.
    
    Args:
        region (tuple, optional): (x, y, width, height) da região para extrair texto.
                                Se None, extrai da tela inteira
        filter_type (str): Tipo de filtro ("numbers", "letters", "both")
        confidence_threshold (float): Limiar mínimo de confiança (0-100)
        return_full_data (bool): Se True, retorna dados completos com coordenadas
        max_attempts (int): Número máximo de tentativas se backtrack=True
        backtrack (bool): Se deve tentar múltiplas vezes com ajustes
        config (dict or BotVisionConfig, optional): Configuração customizada
        
    Returns:
        Se return_full_data=False:
            list: Lista de strings com todo texto encontrado
        Se return_full_data=True:
            list: Lista de dicionários com dados completos
            
    Examples:
        Extração simples:
        >>> texts = extract_text_from_region_standalone(region=(100, 100, 400, 300))
        >>> print("Textos encontrados:", texts)
        
        Extração com dados completos:
        >>> data = extract_text_from_region_standalone(
        ...     region=(100, 100, 400, 300),
        ...     return_full_data=True,
        ...     confidence_threshold=70.0,
        ...     backtrack=True
        ... )
        >>> for item in data:
        ...     print(f"'{item['text']}' - Confiança: {item['confidence']:.1f}%")
        
        Apenas números:
        >>> numbers = extract_text_from_region_standalone(
        ...     region=(50, 50, 200, 100),
        ...     filter_type="numbers"
        ... )
    """
    bot = BotVision(config=config)
    return bot.extract_text_from_region(
        region=region,
        filter_type=filter_type,
        confidence_threshold=confidence_threshold,
        return_full_data=return_full_data,
        max_attempts=max_attempts,
        backtrack=backtrack
    )


# Função para compatibilidade total - execução de tarefas com suporte a listas múltiplas
def run_automation(tasks, default_confidence=0.9, default_margin=50):
    """
    Função que replica o comportamento exato do if __name__ == '__main__' do bot_vision.py original.
    Suporta tanto lista simples quanto lista de listas (múltiplos conjuntos de tarefas).
    
    Args:
        tasks: Lista de tarefas ou lista de listas de tarefas (como no original)
        default_confidence (float): Confiança padrão
        default_margin (int): Margem padrão
    """
    import logging
    
    # Verifica se tasks é uma lista e não está vazia
    if isinstance(tasks, list) and tasks:
        # Verifica se o primeiro elemento também é uma lista (indicando lista de listas)
        if isinstance(tasks[0], list):
            logging.info(f"Detected multiple task lists ({len(tasks)} lists). Executing sequentially.")
            # Itera através de cada lista de tarefas
            for i, task_list in enumerate(tasks):
                if isinstance(task_list, list):
                    logging.info(f"--- Starting task list {i+1}/{len(tasks)} ({len(task_list)} tasks) ---")
                    click_images(task_list, default_confidence, default_margin)  # Passa a lista individual para a função
                    logging.info(f"--- Finished task list {i+1}/{len(tasks)} ---")
                else:
                    logging.warning(f"Item {i} in the main list is not a list of tasks. Skipping.")
        else:
            # Assume que é uma única lista plana de tarefas
            logging.info("Detected a single task list. Executing.")
            click_images(tasks, default_confidence, default_margin)
    elif isinstance(tasks, list) and not tasks:
        logging.info("The imported 'tasks' list is empty. Nothing to execute.")
    else:
        logging.error(f"The imported 'tasks' is not a list. Type: {type(tasks)}. Cannot execute.")

# Lista de símbolos exportados
__all__ = [
    # Classe principal
    "BotVision",
    
    # Funções principais de execução
    "execute_tasks",
    "run_automation",
    "click_images",  # Compatibilidade com código legado
    
    # Funções de backtrack individual (NOVO!)
    "start_individual_session",
    "run_individual_tasks_with_backtrack",
    
    # Funções básicas de conveniência
    "find_text",
    "click_text", 
    "find_image",
    "click_image",
    "type_text",
    "click_at",
    
    # Funções avançadas de conveniência (com todas as funcionalidades)
    "click_text_advanced",
    "click_image_advanced", 
    "find_text_advanced",
    "find_image_advanced",
    
    # Classes core
    "TaskExecutor",
    "TaskResult", 
    "OCREngine",
    "OCRResult",
    "ImageProcessor",
    "VisualOverlay",
    "BotVisionConfig",
    
    # Funções auxiliares
    "show_overlay",
    "limpar_texto",
    "matches_filter",
    "get_default_config",
    
    # Funções standalone para compatibilidade 100%
    "locate_image_with_retry",
    "preprocess_image_for_ocr", 
    "find_text_with_multiple_preprocessing",
    
    # Exceções
    "BotVisionError",
    "TesseractNotFoundError", 
    "ImageNotFoundError",
    "TextNotFoundError",
    "TaskExecutionError",
    "ConfigurationError",
    "OCRProcessingError",
    "ImageProcessingError",
]

# Configuração inicial da biblioteca
def _setup_library():
    """Configuração inicial da biblioteca."""
    try:
        # Configura logging se não estiver configurado
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=logging.INFO,
                format="[%(levelname)s] %(name)s: %(message)s"
            )
        
        # Tenta configurar a biblioteca com configuração padrão
        config = get_default_config()
        logger.info(f"Bot Vision Suite v{__version__} inicializada")
        
    except Exception as e:
        logger.warning(f"Aviso na inicialização da biblioteca: {e}")

# Executa configuração inicial
_setup_library()

# Funções standalone de conveniência (criam instância temporária do BotVision)
def find_text(text, region=None, filter_type="both", confidence_threshold=75.0, 
              occurrence=1, max_attempts=3, config=None):
    """
    Busca texto na tela usando uma instância temporária do BotVision.
    
    Args:
        text (str): Texto a ser encontrado
        region (tuple, optional): Região de busca (x, y, width, height)
        filter_type (str): Tipo de filtro ("letters", "numbers", "both")
        confidence_threshold (float): Limiar de confiança OCR
        occurrence (int): Qual ocorrência buscar (1=primeira)
        max_attempts (int): Número máximo de tentativas
        config (dict, optional): Configuração personalizada
        
    Returns:
        tuple: Coordenadas encontradas ou None
    """
    bot = BotVision(config)
    return bot.find_text(text, region, filter_type, confidence_threshold, occurrence, max_attempts)


def click_text(text, region=None, filter_type="both", delay=0, mouse_button="left",
               occurrence=1, max_attempts=3, sendtext=None, confidence_threshold=None,
               show_overlay=True, config=None):
    """
    Clica em texto usando uma instância temporária do BotVision.
    
    Args:
        text (str): Texto a ser clicado
        region (tuple, optional): Região de busca (x, y, width, height)
        filter_type (str): Tipo de filtro ("letters", "numbers", "both")
        delay (float): Delay após o clique em segundos
        mouse_button (str): Tipo de clique do mouse:
            • "left" - Clique simples esquerdo (padrão)
            • "right" - Clique direito
            • "double" ou "double left" - Clique duplo esquerdo
            • "move_to" - Apenas move o mouse sem clicar
        occurrence (int): Qual ocorrência clicar (1=primeira)
        max_attempts (int): Número máximo de tentativas
        sendtext (str, optional): Texto para digitar após o clique
        confidence_threshold (float, optional): Limiar de confiança customizado
        show_overlay (bool): Se deve exibir o overlay vermelho antes do clique
        config (dict, optional): Configuração personalizada
        
    Returns:
        bool: True se encontrou e clicou, False caso contrário
    """
    bot = BotVision(config)
    return bot.click_text(text, region, filter_type, delay, mouse_button, occurrence,
                         False, max_attempts, sendtext, confidence_threshold, show_overlay)


def find_image(image_path, region=None, confidence=0.9, max_attempts=3, 
               specific=True, scales=None, config=None):
    """
    Busca imagem na tela usando uma instância temporária do BotVision.
    
    Args:
        image_path (str): Caminho para a imagem
        region (tuple, optional): Região de busca
        confidence (float): Nível de confiança
        max_attempts (int): Número máximo de tentativas
        specific (bool): Se True, busca na região; se False, busca na tela inteira + variações
        scales (list, optional): Lista de escalas para tentar
        config (dict, optional): Configuração personalizada
        
    Returns:
        tuple: Coordenadas da imagem ou None
    """
    bot = BotVision(config)
    return bot.find_image(image_path, region, confidence, max_attempts, False, specific, scales)


def click_image(image_path, region=None, confidence=0.9, delay=0, mouse_button="left",
                max_attempts=3, specific=True, sendtext=None, show_overlay=True, config=None):
    """
    Clica em imagem usando uma instância temporária do BotVision.
    
    Args:
        image_path (str): Caminho para a imagem
        region (tuple, optional): Região de busca (x, y, width, height)
        confidence (float): Nível de confiança (0.0-1.0)
        delay (float): Delay após o clique em segundos
        mouse_button (str): Tipo de clique do mouse:
            • "left" - Clique simples esquerdo (padrão)
            • "right" - Clique direito
            • "double" ou "double left" - Clique duplo esquerdo
            • "move_to" - Apenas move o mouse sem clicar
        max_attempts (int): Número máximo de tentativas
        specific (bool): Se True, busca na região; se False, busca na tela inteira + variações
        sendtext (str, optional): Texto para digitar após o clique
        show_overlay (bool): Se deve exibir o overlay vermelho antes do clique
        config (dict, optional): Configuração personalizada
        
    Returns:
        bool: True se encontrou e clicou, False caso contrário
    """
    bot = BotVision(config)
    return bot.click_image(image_path, region, confidence, delay, mouse_button,
                          max_attempts, False, specific, sendtext, show_overlay)


def click_at(location, mouse_button="left", delay=0, show_overlay=True, config=None):
    """
    Clica em coordenadas específicas usando uma instância temporária do BotVision.
    
    Args:
        location (tuple): (x, y, width, height) da localização
        mouse_button (str): Botão do mouse ("left", "right", "double", "move_to")
        delay (float): Delay após o clique
        show_overlay (bool): Se deve exibir o overlay vermelho antes do clique
        config (dict, optional): Configuração personalizada
        
    Returns:
        bool: True se clicou com sucesso
    """
    bot = BotVision(config)
    return bot.click_at(location, mouse_button, delay, show_overlay)


def type_text(text, config=None):
    """
    Digita texto usando uma instância temporária do BotVision.
    
    Args:
        text (str): Texto a ser digitado (suporta comandos especiais)
        config (dict, optional): Configuração personalizada
        
    Returns:
        bool: True se digitou com sucesso
    """
    bot = BotVision(config)
    return bot.type_text(text)


# EXPORTAÇÕES PRINCIPAIS
__all__ = [
    # Classe principal
    "BotVision",
    
    # Funções de execução de tarefas
    "execute_tasks",
    "click_images",  # Compatibilidade total com código legado
    "run_automation",  # Compatibilidade com if __name__ == '__main__'
    
    # Funções de conveniência básicas
    "find_text",
    "click_text", 
    "find_image",
    "click_image",
    "click_at",
    "type_text",
    
    # NOVAS FUNCIONALIDADES - Funções de conveniência para imagem relativa
    "find_relative_image",
    "click_relative_image",
    
    # NOVAS FUNCIONALIDADES - Funções de conveniência para coordenadas
    "click_coordinates",
    
    # NOVAS FUNCIONALIDADES - Funções de conveniência para teclado
    "type_text_standalone", 
    "keyboard_command_standalone",
    "get_available_keyboard_commands",
    
    # NOVA FUNCIONALIDADE - Extração de texto
    "extract_text_from_region_standalone",
    
    # Funções de backtrack individual
    "start_individual_session",
    "run_individual_tasks_with_backtrack",
    
    # Classes de core (para uso avançado)
    "TaskExecutor",
    "TaskResult", 
    "OCREngine",
    "OCRResult",
    "ImageProcessor",
    "VisualOverlay",
    "RelativeImageDetector",  # NOVA
    "KeyboardCommander",      # NOVA
    
    # Utilitários
    "BotVisionConfig",
    "get_default_config",
    "limpar_texto",
    "matches_filter",
    
    # Funções de processamento standalone (compatibilidade)
    "preprocess_image_for_ocr",
    "find_text_with_multiple_preprocessing",
    "show_overlay",
    "locate_image_with_retry",
    
    # Exceções
    "BotVisionError",
    "ImageNotFoundError", 
    "TextNotFoundError",
    "TaskExecutionError",
    "ImageProcessingError",
    "OCRError",
    "ConfigurationError",
    
    # Informações da biblioteca
    "__version__",
    "__author__",
    "__email__",
    "__license__"
]
