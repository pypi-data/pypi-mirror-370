"""
Bot Vision Suite - Keyboard Commands

Este módulo implementa uma lista completa de comandos de teclado
para automação, incluindo comandos específicos do sistema e gerais.
"""

import logging
import pyautogui
from typing import Dict, Callable
from ..exceptions import TaskExecutionError

logger = logging.getLogger(__name__)


class KeyboardCommander:
    """
    Executor de comandos de teclado.
    
    Fornece uma interface unificada para executar diferentes tipos
    de comandos de teclado, incluindo teclas especiais e combinações.
    """
    
    def __init__(self):
        """Inicializa o comandante de teclado."""
        self._setup_command_mapping()
    
    def _setup_command_mapping(self) -> None:
        """Configura o mapeamento de comandos para funções do pyautogui."""
        self.command_mapping: Dict[str, Callable] = {
            # Comandos específicos do sistema (Oracle Forms, etc.)
            'F7': lambda: pyautogui.press('f7'),  # Clear Block
            'F5': lambda: pyautogui.press('f5'),  # Clear Field
            'F8': lambda: pyautogui.press('f8'),  # Clear Form
            'F6': lambda: pyautogui.press('f6'),  # Clear Record
            'Ctrl+S': lambda: pyautogui.hotkey('ctrl', 's'),  # Commit
            'F12': lambda: pyautogui.press('f12'),  # Count Query
            'Ctrl+Up': lambda: pyautogui.hotkey('ctrl', 'up'),  # Delete Record
            'Shift+Ctrl+E': lambda: pyautogui.hotkey('shift', 'ctrl', 'e'),  # Display Error
            'Down': lambda: pyautogui.press('down'),  # Down
            'Shift+F5': lambda: pyautogui.hotkey('shift', 'f5'),  # Duplicate Field
            'Shift+F6': lambda: pyautogui.hotkey('shift', 'f6'),  # Duplicate Record
            'Ctrl+E': lambda: pyautogui.hotkey('ctrl', 'e'),  # Edit
            'Ctrl+F11': lambda: pyautogui.hotkey('ctrl', 'f11'),  # Enter Query
            'F4': lambda: pyautogui.press('f4'),  # Exit
            'Shift+Ctrl+F10': lambda: pyautogui.hotkey('shift', 'ctrl', 'f10'),  # Function 0
            'Shift+Ctrl+F1': lambda: pyautogui.hotkey('shift', 'ctrl', 'f1'),  # Function 1
            'Shift+Ctrl+F2': lambda: pyautogui.hotkey('shift', 'ctrl', 'f2'),  # Function 2
            'Shift+Ctrl+F3': lambda: pyautogui.hotkey('shift', 'ctrl', 'f3'),  # Function 3
            'Shift+Ctrl+F4': lambda: pyautogui.hotkey('shift', 'ctrl', 'f4'),  # Function 4
            'Shift+Ctrl+F5': lambda: pyautogui.hotkey('shift', 'ctrl', 'f5'),  # Function 5
            'Shift+Ctrl+F6': lambda: pyautogui.hotkey('shift', 'ctrl', 'f6'),  # Function 6
            'Shift+Ctrl+F7': lambda: pyautogui.hotkey('shift', 'ctrl', 'f7'),  # Function 7
            'Ctrl+H': lambda: pyautogui.hotkey('ctrl', 'h'),  # Help
            'Ctrl+Down': lambda: pyautogui.hotkey('ctrl', 'down'),  # Insert Record
            'Ctrl+L': lambda: pyautogui.hotkey('ctrl', 'l'),  # List of Values
            'F2': lambda: pyautogui.press('f2'),  # List Tab Pages
            'Shift+PageDown': lambda: pyautogui.hotkey('shift', 'pagedown'),  # Next Block
            'Tab': lambda: pyautogui.press('tab'),  # Next Field
            'Shift+F7': lambda: pyautogui.hotkey('shift', 'f7'),  # Next Primary Key
            'Shift+F8': lambda: pyautogui.hotkey('shift', 'f8'),  # Next Set of Records
            'Shift+PageUp': lambda: pyautogui.hotkey('shift', 'pageup'),  # Previous Block
            'Shift+Tab': lambda: pyautogui.hotkey('shift', 'tab'),  # Previous Field
            'Up': lambda: pyautogui.press('up'),  # Previous Record
            'Ctrl+P': lambda: pyautogui.hotkey('ctrl', 'p'),  # Print
            'Shift+Ctrl+F9': lambda: pyautogui.hotkey('shift', 'ctrl', 'f9'),  # Prompt/Value LOV
            'Return': lambda: pyautogui.press('enter'),  # Return
            'PageDown': lambda: pyautogui.press('pagedown'),  # Scroll Down
            'PageUp': lambda: pyautogui.press('pageup'),  # Scroll Up
            'Ctrl+K': lambda: pyautogui.hotkey('ctrl', 'k'),  # Show Keys
            'Ctrl+U': lambda: pyautogui.hotkey('ctrl', 'u'),  # Update Record
            
            # Comandos gerais de edição
            'Ctrl+C': lambda: pyautogui.hotkey('ctrl', 'c'),  # Copy
            'Ctrl+V': lambda: pyautogui.hotkey('ctrl', 'v'),  # Paste
            'Ctrl+X': lambda: pyautogui.hotkey('ctrl', 'x'),  # Cut
            'Ctrl+A': lambda: pyautogui.hotkey('ctrl', 'a'),  # Select All
            'Ctrl+Z': lambda: pyautogui.hotkey('ctrl', 'z'),  # Undo
            'Ctrl+Y': lambda: pyautogui.hotkey('ctrl', 'y'),  # Redo
            'Ctrl+F': lambda: pyautogui.hotkey('ctrl', 'f'),  # Find
            'Ctrl+N': lambda: pyautogui.hotkey('ctrl', 'n'),  # New
            'Ctrl+O': lambda: pyautogui.hotkey('ctrl', 'o'),  # Open
            
            # Teclas de navegação
            'Enter': lambda: pyautogui.press('enter'),
            'Escape': lambda: pyautogui.press('escape'),
            'Delete': lambda: pyautogui.press('delete'),
            'Backspace': lambda: pyautogui.press('backspace'),
            'Home': lambda: pyautogui.press('home'),
            'End': lambda: pyautogui.press('end'),
            'Page Up': lambda: pyautogui.press('pageup'),
            'Page Down': lambda: pyautogui.press('pagedown'),
            'Arrow Up': lambda: pyautogui.press('up'),
            'Arrow Down': lambda: pyautogui.press('down'),
            'Arrow Left': lambda: pyautogui.press('left'),
            'Arrow Right': lambda: pyautogui.press('right'),
            
            # Teclas de função
            'F1': lambda: pyautogui.press('f1'),
            'F3': lambda: pyautogui.press('f3'),
            'F9': lambda: pyautogui.press('f9'),
            'F10': lambda: pyautogui.press('f10'),
            'F11': lambda: pyautogui.press('f11'),
            
            # Comandos de sistema
            'Alt+Tab': lambda: pyautogui.hotkey('alt', 'tab'),  # Switch windows
            'Alt+F4': lambda: pyautogui.hotkey('alt', 'f4'),  # Close window
            'Windows+D': lambda: pyautogui.hotkey('win', 'd'),  # Show desktop
            'Windows+L': lambda: pyautogui.hotkey('win', 'l'),  # Lock screen
            'Windows+R': lambda: pyautogui.hotkey('win', 'r'),  # Run dialog
            
            # Comandos adicionais de navegação
            'Ctrl+Home': lambda: pyautogui.hotkey('ctrl', 'home'),  # Start of document
            'Ctrl+End': lambda: pyautogui.hotkey('ctrl', 'end'),  # End of document
            'Shift+Home': lambda: pyautogui.hotkey('shift', 'home'),  # Select to start of line
            'Shift+End': lambda: pyautogui.hotkey('shift', 'end'),  # Select to end of line
            'Ctrl+Left': lambda: pyautogui.hotkey('ctrl', 'left'),  # Word left
            'Ctrl+Right': lambda: pyautogui.hotkey('ctrl', 'right'),  # Word right
            'Shift+Ctrl+Left': lambda: pyautogui.hotkey('shift', 'ctrl', 'left'),  # Select word left
            'Shift+Ctrl+Right': lambda: pyautogui.hotkey('shift', 'ctrl', 'right'),  # Select word right
            
            # Comandos de formatação
            'Ctrl+B': lambda: pyautogui.hotkey('ctrl', 'b'),  # Bold
            'Ctrl+I': lambda: pyautogui.hotkey('ctrl', 'i'),  # Italic
            'Ctrl+U': lambda: pyautogui.hotkey('ctrl', 'u'),  # Underline
            
            # Comandos específicos de navegador
            'Ctrl+T': lambda: pyautogui.hotkey('ctrl', 't'),  # New tab
            'Ctrl+W': lambda: pyautogui.hotkey('ctrl', 'w'),  # Close tab
            'Ctrl+R': lambda: pyautogui.hotkey('ctrl', 'r'),  # Refresh
            'Ctrl+Shift+T': lambda: pyautogui.hotkey('ctrl', 'shift', 't'),  # Reopen closed tab
            'F5': lambda: pyautogui.press('f5'),  # Refresh
            'Ctrl+D': lambda: pyautogui.hotkey('ctrl', 'd'),  # Bookmark
            'Ctrl+J': lambda: pyautogui.hotkey('ctrl', 'j'),  # Downloads
            'Ctrl+Shift+N': lambda: pyautogui.hotkey('ctrl', 'shift', 'n'),  # New incognito window
            
            # Comandos de volume e mídia
            'Volume Up': lambda: pyautogui.press('volumeup'),
            'Volume Down': lambda: pyautogui.press('volumedown'),
            'Volume Mute': lambda: pyautogui.press('volumemute'),
            'Play/Pause': lambda: pyautogui.press('playpause'),
            'Next Track': lambda: pyautogui.press('nexttrack'),
            'Previous Track': lambda: pyautogui.press('prevtrack'),
            
            # Comandos de captura de tela
            'Print Screen': lambda: pyautogui.press('printscreen'),
            'Alt+Print Screen': lambda: pyautogui.hotkey('alt', 'printscreen'),
            'Windows+Shift+S': lambda: pyautogui.hotkey('win', 'shift', 's'),  # Snipping tool
        }
    
    def execute_command(self, command: str) -> bool:
        """
        Executa um comando de teclado.
        
        Args:
            command (str): Nome do comando a ser executado
            
        Returns:
            bool: True se o comando foi executado com sucesso, False caso contrário
            
        Raises:
            TaskExecutionError: Se houver erro na execução do comando
        """
        try:
            if command in self.command_mapping:
                logger.info(f"Executando comando de teclado: '{command}'")
                self.command_mapping[command]()
                logger.info(f"Comando '{command}' executado com sucesso")
                return True
            else:
                logger.warning(f"Comando '{command}' não reconhecido")
                return False
        except Exception as e:
            error_msg = f"Erro ao executar comando '{command}': {e}"
            logger.error(error_msg)
            raise TaskExecutionError(error_msg)
    
    def get_available_commands(self) -> list:
        """
        Retorna lista de comandos disponíveis.
        
        Returns:
            list: Lista com todos os comandos disponíveis
        """
        return list(self.command_mapping.keys())
    
    def type_text(self, text: str, interval: float = 0.05) -> None:
        """
        Digite texto com intervalo entre caracteres.
        
        Args:
            text (str): Texto a ser digitado
            interval (float): Intervalo entre caracteres em segundos
            
        Raises:
            TaskExecutionError: Se houver erro na digitação
        """
        try:
            logger.info(f"Digitando texto: '{text}'")
            pyautogui.typewrite(text, interval=interval)
            logger.info("Texto digitado com sucesso")
        except Exception as e:
            error_msg = f"Erro ao digitar texto '{text}': {e}"
            logger.error(error_msg)
            raise TaskExecutionError(error_msg)
    
    def process_sendtext_command(self, full_text_command: str) -> None:
        """
        Processa comandos especiais no sendtext.
        
        Args:
            full_text_command (str): Comando completo com texto e comandos especiais
            
        Raises:
            TaskExecutionError: Se houver erro no processamento
        """
        import pyperclip
        import time
        
        try:
            logger.info(f"Processando sendtext: '{full_text_command}'")

            # Processa comandos especiais no início da string
            text_to_write = full_text_command
            commands_processed = True
            
            while commands_processed:
                commands_processed = False
                # Padroniza para minúsculas para facilitar a correspondência
                lower_text = text_to_write.lower() 
                
                if lower_text.startswith('{ctrl}a'):
                    logger.info("Executando comando: CTRL+A (Selecionar Tudo)")
                    pyautogui.hotkey('ctrl', 'a')
                    text_to_write = text_to_write[len('{ctrl}a'):]
                    commands_processed = True
                    time.sleep(0.1)
                elif lower_text.startswith('{del}'):
                    logger.info("Executando comando: DEL (Deletar)")
                    pyautogui.press('delete')
                    text_to_write = text_to_write[len('{del}'):]
                    commands_processed = True
                    time.sleep(0.1)
                elif lower_text.startswith('{tab}'):
                    logger.info("Executando comando: TAB")
                    pyautogui.press('tab')
                    text_to_write = text_to_write[len('{tab}'):]
                    commands_processed = True
                    time.sleep(0.1)
                elif lower_text.startswith('{enter}'):
                    logger.info("Executando comando: ENTER")
                    pyautogui.press('enter')
                    text_to_write = text_to_write[len('{enter}'):]
                    commands_processed = True
                    time.sleep(0.1)
                elif lower_text.startswith('{backspace}'):
                    logger.info("Executando comando: BACKSPACE")
                    pyautogui.press('backspace')
                    text_to_write = text_to_write[len('{backspace}'):]
                    commands_processed = True
                    time.sleep(0.1)
                elif lower_text.startswith('{escape}'):
                    logger.info("Executando comando: ESCAPE")
                    pyautogui.press('escape')
                    text_to_write = text_to_write[len('{escape}'):]
                    commands_processed = True
                    time.sleep(0.1)

            # Digita o texto restante usando clipboard para melhor compatibilidade
            if text_to_write:
                logger.info(f"Colando texto restante: '{text_to_write}'")
                pyperclip.copy(text_to_write) 
                pyautogui.hotkey('ctrl', 'v') 
            
            time.sleep(0.5)  # Pequena pausa após processar sendtext
            
        except Exception as e:
            error_msg = f"Erro ao processar sendtext '{full_text_command}': {e}"
            logger.error(error_msg)
            raise TaskExecutionError(error_msg)
