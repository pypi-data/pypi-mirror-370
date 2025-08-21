"""
Guia de Migração - Bot Vision Suite
Novas Funcionalidades Implementadas

Este arquivo mostra como migrar do código antigo para usar as novas funcionalidades
implementadas na biblioteca bot-vision-suite.
"""

# ANTES - Código antigo (bot_vision.py original)
def exemplo_codigo_antigo():
    """Exemplo de como era feito antes das novas funcionalidades."""
    
    from _bot_vision import click_images
    
    # Tarefas limitadas aos tipos básicos
    tasks_antigas = [
        {
            'text': 'Login',
            'region': (100, 100, 500, 300),
            'char_type': 'letters',
            'delay': 1
        },
        {
            'image': 'button.png',
            'confidence': 0.9,
            'delay': 2
        }
    ]
    
    # Executava apenas estes tipos básicos
    click_images(tasks_antigas)


# DEPOIS - Código novo com TODAS as funcionalidades
def exemplo_codigo_novo():
    """Exemplo usando TODAS as novas funcionalidades implementadas."""
    
    from _bot_vision import BotVision, execute_tasks
    
    # Bot com todas as funcionalidades
    bot = BotVision()
    
    # ===== NOVA FUNCIONALIDADE 1: IMAGEM RELATIVA =====
    print("🆕 1. IMAGEM RELATIVA - Busca target próximo a âncora")
    
    # Método individual
    location = bot.find_relative_image(
        anchor_image='warning.png',      # Imagem âncora única
        target_image='ok_button.png',    # Target que pode ter duplicatas
        max_distance=200,                # Máximo 200px de distância
        confidence=0.9
    )
    
    # Clique em imagem relativa
    success = bot.click_relative_image(
        anchor_image='warning.png',
        target_image='ok_button.png',
        max_distance=150,
        backtrack=True                   # Retry inteligente
    )
    
    # ===== NOVA FUNCIONALIDADE 2: CLIQUE EM COORDENADAS =====
    print("🆕 2. CLIQUE EM COORDENADAS ESPECÍFICAS")
    
    success = bot.click_coordinates(
        x=500, y=300,                    # Posição exata
        delay=1,
        mouse_button="right",            # Clique direito
        backtrack=True
    )
    
    # ===== NOVA FUNCIONALIDADE 3: DIGITAÇÃO AVANÇADA =====
    print("🆕 3. DIGITAÇÃO COM COMANDOS ESPECIAIS")
    
    success = bot.type_text(
        text="{ctrl}a{del}Novo texto{tab}Próximo{enter}",
        interval=0.05,
        backtrack=True
    )
    
    # ===== NOVA FUNCIONALIDADE 4: COMANDOS DE TECLADO =====
    print("🆕 4. COMANDOS DE TECLADO EXPANDIDOS")
    
    # Comando específico
    success = bot.keyboard_command("Ctrl+S", delay=1, backtrack=True)
    success = bot.keyboard_command("F7", backtrack=True)     # Oracle Forms
    success = bot.keyboard_command("Alt+Tab", backtrack=True) # Trocar janela
    
    # Ver todos os comandos disponíveis
    commands = bot.get_available_keyboard_commands()
    print(f"Total de comandos: {len(commands)}")
    
    # ===== USANDO TUDO EM LISTA DE TAREFAS =====
    print("🆕 5. TODAS AS FUNCIONALIDADES EM LISTA")
    
    tasks_completas = [
        # Texto tradicional
        {
            'text': 'Login',
            'region': (100, 100, 500, 300),
            'char_type': 'letters',
            'backtrack': True,
            'sendtext': 'admin{tab}password'
        },
        
        # 🆕 IMAGEM RELATIVA
        {
            'type': 'relative_image',
            'anchor_image': 'dialog.png',
            'target_image': 'close.png',
            'max_distance': 200,
            'confidence': 0.9,
            'backtrack': True
        },
        
        # 🆕 CLIQUE EM COORDENADAS
        {
            'type': 'click',
            'x': 400,
            'y': 250,
            'mouse_button': 'left',
            'backtrack': True
        },
        
        # 🆕 DIGITAÇÃO DIRETA
        {
            'type': 'type_text',
            'text': 'Automação avançada!',
            'interval': 0.05
        },
        
        # 🆕 COMANDO DE TECLADO
        {
            'type': 'keyboard_command',
            'command': 'Ctrl+S',
            'delay': 1
        },
        
        # Imagem tradicional
        {
            'image': 'confirm.png',
            'confidence': 0.9,
            'backtrack': True
        }
    ]
    
    # Executa tudo
    results = execute_tasks(tasks_completas)
    
    successful = sum(1 for r in results if r.success)
    print(f"✅ {successful}/{len(results)} tarefas executadas com sucesso")


def exemplo_funcoes_standalone():
    """Funcões standalone - uso rápido sem instanciar classe."""
    
    print("🆕 6. FUNÇÕES STANDALONE (SEM INSTANCIAR CLASSE)")
    
    from _bot_vision import (
        # Tradicionais
        find_text, click_text, find_image, click_image,
        # 🆕 NOVAS
        find_relative_image, click_relative_image,
        click_coordinates, type_text_standalone,
        keyboard_command_standalone, get_available_keyboard_commands
    )
    
    # Uso rápido das novas funcionalidades
    location = find_relative_image("anchor.png", "target.png")
    success = click_relative_image("anchor.png", "target.png", backtrack=True)
    success = click_coordinates(100, 200, backtrack=True)
    success = type_text_standalone("{ctrl}a{del}Teste", backtrack=True)
    success = keyboard_command_standalone("Ctrl+S", backtrack=True)
    
    commands = get_available_keyboard_commands()
    print(f"Comandos disponíveis: {len(commands)}")


def exemplo_backtrack_melhorado():
    """Sistema de backtrack melhorado entre métodos individuais."""
    
    print("🆕 7. BACKTRACK INTELIGENTE ENTRE MÉTODOS")
    
    from _bot_vision import BotVision
    
    bot = BotVision()
    
    # Opção 1: Backtrack automático
    success1 = bot.click_image('step1.png', backtrack=True)
    success2 = bot.click_text('Next', backtrack=True)      # Se falhar, volta ao step1
    success3 = bot.click_coordinates(100, 200, backtrack=True)  # Se falhar, volta ao Next
    
    # Opção 2: Controle manual de sessão
    bot.start_task_session()
    
    bot.click_image('login.png', backtrack=True)
    bot.type_text('username{tab}password', backtrack=True)
    bot.keyboard_command('Enter', backtrack=True)
    bot.click_relative_image('dialog.png', 'ok.png', backtrack=True)
    
    successful, total = bot.end_task_session()
    print(f"Sessão finalizada: {successful}/{total} sucessos")


def comparacao_antes_depois():
    """Comparação direta: antes vs depois das novas funcionalidades."""
    
    print("\n" + "=" * 80)
    print("📊 COMPARAÇÃO: ANTES vs DEPOIS das Novas Funcionalidades")
    print("=" * 80)
    
    print("\n❌ ANTES (Limitações):")
    print("   • Apenas texto e imagem básica")
    print("   • Sem imagem relativa (problemas com duplicatas)")
    print("   • Sem clique em coordenadas específicas")
    print("   • Comandos de teclado limitados")
    print("   • Sem digitação com comandos especiais")
    print("   • Backtrack apenas em listas")
    
    print("\n✅ DEPOIS (Novas Funcionalidades):")
    print("   • ✨ Imagem relativa (âncora + target)")
    print("   • ✨ Clique em coordenadas específicas")
    print("   • ✨ 100+ comandos de teclado pré-definidos")
    print("   • ✨ Digitação com comandos especiais {ctrl}a{del}texto{enter}")
    print("   • ✨ Backtrack entre métodos individuais")
    print("   • ✨ Funções standalone para uso rápido")
    print("   • ✨ 6 tipos de tarefa diferentes")
    print("   • ✨ Compatibilidade 100% com código antigo")
    
    print("\n🎯 CASOS DE USO RESOLVIDOS:")
    print("   1. Múltiplos botões 'OK' → Imagem relativa resolve!")
    print("   2. Clique em posição fixa → Coordenadas específicas!")
    print("   3. Comandos F1-F12, Ctrl+S → Lista expandida!")
    print("   4. Selecionar tudo e digitar → {ctrl}a{del}texto!")
    print("   5. Retry inteligente → Backtrack individual!")


if __name__ == "__main__":
    print("🚀 GUIA DE MIGRAÇÃO - Bot Vision Suite")
    print("Demonstrando TODAS as novas funcionalidades implementadas")
    print("=" * 80)
    
    try:
        # Mostra o código novo
        exemplo_codigo_novo()
        
        # Funções standalone
        exemplo_funcoes_standalone()
        
        # Backtrack melhorado
        exemplo_backtrack_melhorado()
        
        # Comparação
        comparacao_antes_depois()
        
        print("\n🎉 MIGRAÇÃO CONCLUÍDA!")
        print("💡 Agora você tem acesso a TODAS as funcionalidades avançadas!")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("💡 Este é apenas um exemplo de migração. Adapte para suas necessidades.")
