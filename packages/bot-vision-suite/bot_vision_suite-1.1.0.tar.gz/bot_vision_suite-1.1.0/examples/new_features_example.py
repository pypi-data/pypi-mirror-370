"""
Exemplo Prático - Novas Funcionalidades Bot Vision Suite

Este exemplo demonstra todas as novas funcionalidades implementadas:
1. Imagens relativas (âncora + target)
2. Clique em coordenadas específicas
3. Digitação de texto avançada
4. Comandos de teclado expandidos
"""

from _bot_vision import BotVision, execute_tasks

def exemplo_funcionalidades_novas():
    """Demonstra todas as novas funcionalidades da biblioteca."""
    
    # Inicializa o bot
    bot = BotVision()
    
    print("🚀 Demonstrando NOVAS FUNCIONALIDADES do Bot Vision Suite")
    print("=" * 60)
    
    # 1. IMAGEM RELATIVA - Busca target próximo a âncora
    print("\n1. 🎯 IMAGEM RELATIVA")
    print("   Busca botão 'OK' próximo ao ícone 'Warning'")
    
    # Método individual
    location = bot.find_relative_image(
        anchor_image='images/warning_icon.png',
        target_image='images/ok_button.png',
        max_distance=150,
        confidence=0.9
    )
    
    if location:
        print(f"   ✓ Target encontrado próximo à âncora: {location}")
        success = bot.click_relative_image(
            anchor_image='images/warning_icon.png',
            target_image='images/ok_button.png',
            max_distance=150,
            backtrack=True
        )
        print(f"   ✓ Clique realizado: {success}")
    else:
        print("   ✗ Target não encontrado próximo à âncora")
    
    # 2. CLIQUE EM COORDENADAS ESPECÍFICAS
    print("\n2. 📍 CLIQUE EM COORDENADAS")
    print("   Clique direto na posição (500, 300)")
    
    success = bot.click_coordinates(
        x=500, 
        y=300, 
        delay=1, 
        mouse_button="left", 
        backtrack=True
    )
    print(f"   ✓ Clique em coordenadas realizado: {success}")
    
    # 3. DIGITAÇÃO AVANÇADA DE TEXTO
    print("\n3. ⌨️ DIGITAÇÃO AVANÇADA")
    print("   Texto com comandos especiais")
    
    success = bot.type_text(
        text="{ctrl}a{del}Novo texto aqui!{tab}Próximo campo{enter}",
        interval=0.05,
        backtrack=True
    )
    print(f"   ✓ Texto digitado com comandos: {success}")
    
    # 4. COMANDOS DE TECLADO
    print("\n4. 🎮 COMANDOS DE TECLADO")
    print("   Executando comando Ctrl+S (Salvar)")
    
    success = bot.keyboard_command(
        command="Ctrl+S",
        delay=1,
        backtrack=True
    )
    print(f"   ✓ Comando Ctrl+S executado: {success}")
    
    # Lista todos os comandos disponíveis
    commands = bot.get_available_keyboard_commands()
    print(f"   ✓ Total de comandos disponíveis: {len(commands)}")
    print(f"   ✓ Alguns exemplos: {commands[:10]}")
    
    print("\n" + "=" * 60)
    print("✅ Demonstração das novas funcionalidades concluída!")


def exemplo_tarefas_em_lista():
    """Exemplo usando todas as novas funcionalidades em lista de tarefas."""
    
    print("\n🚀 Demonstrando NOVAS FUNCIONALIDADES em Lista de Tarefas")
    print("=" * 60)
    
    # Lista com todos os novos tipos de tarefa
    tasks = [
        # 1. Busca de texto tradicional
        {
            'text': 'Login',
            'region': (100, 100, 500, 300),
            'char_type': 'letters',
            'backtrack': True,
            'delay': 1,
            'sendtext': 'admin{tab}password'
        },
        
        # 2. NOVO! Imagem relativa
        {
            'type': 'relative_image',
            'anchor_image': 'images/dialog_header.png',
            'target_image': 'images/close_button.png',
            'max_distance': 200,
            'confidence': 0.9,
            'target_region': (0, 0, 800, 600),
            'specific': True,
            'backtrack': True,
            'delay': 1
        },
        
        # 3. NOVO! Clique em coordenadas
        {
            'type': 'click',
            'x': 400,
            'y': 250,
            'mouse_button': 'right',
            'delay': 0.5,
            'backtrack': False
        },
        
        # 4. NOVO! Digitação de texto
        {
            'type': 'type_text',
            'text': 'Exemplo de automação com Bot Vision Suite!',
            'interval': 0.03,
            'delay': 1
        },
        
        # 5. NOVO! Comando de teclado
        {
            'type': 'keyboard_command',
            'command': 'Ctrl+S',
            'delay': 2
        },
        
        # 6. Busca de imagem tradicional
        {
            'image': 'images/confirm_button.png',
            'confidence': 0.9,
            'specific': False,
            'backtrack': True,
            'delay': 1,
            'mouse_button': 'left'
        }
    ]
    
    # Executa todas as tarefas
    print("Executando lista de tarefas com novas funcionalidades...")
    results = execute_tasks(tasks)
    
    # Mostra resultados
    successful = sum(1 for r in results if r.success)
    print(f"\n✅ Execução concluída: {successful}/{len(results)} tarefas bem-sucedidas")
    
    for i, result in enumerate(results):
        status = "✓" if result.success else "✗"
        print(f"   {status} Tarefa {i+1}: {result.task_name}")


def exemplo_funcoes_standalone():
    """Exemplo usando as funções standalone (sem instanciar classe)."""
    
    print("\n🚀 Demonstrando FUNÇÕES STANDALONE (Novas)")
    print("=" * 60)
    
    from _bot_vision import (
        find_relative_image, click_relative_image,
        click_coordinates, type_text_standalone,
        keyboard_command_standalone, get_available_keyboard_commands
    )
    
    # 1. Busca imagem relativa standalone
    print("\n1. 🎯 Busca imagem relativa standalone")
    location = find_relative_image(
        anchor_image="images/anchor.png",
        target_image="images/target.png",
        max_distance=150
    )
    print(f"   Resultado: {location}")
    
    # 2. Clique em imagem relativa standalone
    print("\n2. 🎯 Clique em imagem relativa standalone")
    success = click_relative_image(
        anchor_image="images/anchor.png",
        target_image="images/target.png",
        backtrack=True
    )
    print(f"   Sucesso: {success}")
    
    # 3. Clique em coordenadas standalone
    print("\n3. 📍 Clique em coordenadas standalone")
    success = click_coordinates(100, 200, delay=1, backtrack=True)
    print(f"   Sucesso: {success}")
    
    # 4. Digitação standalone
    print("\n4. ⌨️ Digitação standalone")
    success = type_text_standalone(
        text="{ctrl}a{del}Texto standalone!{enter}",
        backtrack=True
    )
    print(f"   Sucesso: {success}")
    
    # 5. Comando de teclado standalone
    print("\n5. 🎮 Comando de teclado standalone")
    success = keyboard_command_standalone("F5", delay=1, backtrack=True)
    print(f"   Sucesso: {success}")
    
    # 6. Lista de comandos
    print("\n6. 📋 Lista de comandos disponíveis")
    commands = get_available_keyboard_commands()
    print(f"   Total: {len(commands)} comandos")
    print(f"   Primeiros 15: {commands[:15]}")


if __name__ == "__main__":
    try:
        # Demonstra métodos individuais
        exemplo_funcionalidades_novas()
        
        # Demonstra tarefas em lista
        exemplo_tarefas_em_lista()
        
        # Demonstra funções standalone
        exemplo_funcoes_standalone()
        
        print("\n🎉 Todos os exemplos das novas funcionalidades executados!")
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        print("💡 Verifique se as imagens de exemplo existem na pasta 'images/'")
