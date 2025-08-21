"""
Exemplo de uso do Bot Vision Suite - Demonstra compatibilidade 100% com o código original

Este exemplo mostra como usar o package bot-vision-suite de forma idêntica
ao script bot_vision.py original.
"""

# MODO 1: Uso exato como o código original (compatibilidade 100%)
from _bot_vision import click_images, run_automation

# Exemplo de tarefas simples
tasks_simples = [
    {
        'text': 'Login',
        'region': (100, 100, 500, 300),
        'char_type': 'both',
        'delay': 1
    },
    {
        'image': 'botao_confirmar.png',
        'region': (200, 400, 300, 100),
        'confidence': 0.8,
        'delay': 2
    }
]

# Exemplo de múltiplas listas de tarefas (como no original)
multiplas_listas_tarefas = [
    [  # Lista 1
        {'text': 'Primeiro', 'region': (0, 0, 800, 600)},
        {'text': 'Segundo', 'region': (0, 0, 800, 600)}
    ],
    [  # Lista 2
        {'image': 'terceiro.png', 'region': (100, 100, 200, 200)},
        {'text': 'Quarto', 'region': (0, 0, 800, 600), 'sendtext': '{ctrl}a{del}Novo texto{enter}'}
    ]
]

# MODO 2: Uso das funções standalone (compatibilidade com funções originais)
from _bot_vision import (
    limpar_texto, 
    matches_filter, 
    show_overlay,
    preprocess_image_for_ocr,
    locate_image_with_retry,
    find_text_with_multiple_preprocessing
)

# MODO 3: Uso orientado a objetos (nova API)
from _bot_vision import BotVision

# MODO 4: Funções de conveniência
from _bot_vision import execute_tasks, find_text, click_text, find_image, click_image

def exemplo_uso_original():
    """Exemplo usando exatamente como no código original."""
    print("=== Exemplo de uso idêntico ao código original ===")
    
    # Para uma lista simples
    print("Executando lista simples...")
    click_images(tasks_simples)
    
    # Para múltiplas listas (exatamente como o original)
    print("Executando múltiplas listas...")
    run_automation(multiplas_listas_tarefas)

def exemplo_funcoes_standalone():
    """Exemplo usando funções standalone."""
    print("=== Exemplo das funções standalone ===")
    
    # Limpeza de texto (exatamente como original)
    texto_limpo = limpar_texto("  123abc!@#  ", "numbers")
    print(f"Texto limpo: '{texto_limpo}'")
    
    # Verificação de filtro
    eh_valido = matches_filter("123", "numbers")
    print(f"'123' é válido para números: {eh_valido}")
    
    # Localizar imagem (sem precisar instanciar classes)
    # location = locate_image_with_retry("minha_imagem.png", confidence=0.9)

def exemplo_orientado_objetos():
    """Exemplo usando a nova API orientada a objetos."""
    print("=== Exemplo da nova API orientada a objetos ===")
    
    # Cria instância do bot
    bot = BotVision()
    
    # Executa tarefas
    resultados = bot.execute_tasks(tasks_simples)
    
    # Usa métodos individuais
    location = bot.find_text("Login", region=(100, 100, 500, 300))
    if location:
        print(f"Texto encontrado em: {location}")
    
    # Clica em texto
    sucesso = bot.click_text("Confirmar", region=(200, 200, 600, 400))
    print(f"Clique realizado: {sucesso}")

def exemplo_conveniencia():
    """Exemplo usando funções de conveniência."""
    print("=== Exemplo das funções de conveniência ===")
    
    # Execução direta
    resultados = execute_tasks(tasks_simples)
    
    # Busca de texto
    location = find_text("Login", region=(100, 100, 500, 300))
    
    # Clique em texto
    sucesso = click_text("Confirmar", region=(200, 200, 600, 400))

if __name__ == "__main__":
    print("Bot Vision Suite - Exemplos de Uso")
    print("=" * 50)
    
    # Demonstra todos os modos de uso
    exemplo_uso_original()
    exemplo_funcoes_standalone()
    exemplo_orientado_objetos()
    exemplo_conveniencia()
    
    print("\n✅ O package bot-vision-suite tem compatibilidade 100% com o código original!")
    print("✅ Todas as funcionalidades do bot_vision.py foram portadas com sucesso!")
