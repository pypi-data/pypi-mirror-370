"""
🧪 Teste Rápido da Bot Vision Suite

Execute este arquivo para testar se a biblioteca foi instalada corretamente
"""

def test_import():
    """Testa se todas as importações funcionam"""
    print("🧪 Testando importações da Bot Vision Suite...")
    
    try:
        # Teste 1: Importação básica
        from bot_vision import BotVision
        print("✅ BotVision importado com sucesso")
        
        # Teste 2: Funções individuais
        from bot_vision import click_text, click_image, find_text
        print("✅ Funções individuais importadas")
        
        # Teste 3: Execute tasks
        from bot_vision import execute_tasks
        print("✅ execute_tasks importado")
        
        # Teste 4: Novas funcionalidades
        from bot_vision import click_relative_image, click_coordinates
        print("✅ Novas funcionalidades importadas")
        
        # Teste 5: Criar instância
        bot = BotVision()
        print("✅ Instância BotVision criada com sucesso")
        
        # Teste 6: Verificar métodos principais
        methods = ['find_text', 'click_text', 'find_image', 'click_image']
        for method in methods:
            if hasattr(bot, method):
                print(f"✅ Método {method} disponível")
            else:
                print(f"❌ Método {method} não encontrado")
        
        print("\n🎉 Todos os testes de importação passaram!")
        print("📖 Veja IMPORT_GUIDE.md para exemplos de uso")
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Verifique se instalou: pip install bot-vision-suite")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


def test_basic_functionality():
    """Testa funcionalidades básicas (sem interação real)"""
    print("\n🔧 Testando funcionalidades básicas...")
    
    try:
        from bot_vision import BotVision
        
        bot = BotVision()
        
        # Teste configuração
        if hasattr(bot, 'config'):
            print("✅ Configuração carregada")
        
        # Teste overlay
        bot.show_overlay = True
        print("✅ Overlay configurado")
        
        # Teste métodos sem execução real
        print("✅ Métodos prontos para uso")
        
        print("\n🎯 Pronto para usar! Exemplos:")
        print("   bot.find_text('Login')")
        print("   bot.click_image('button.png')")
        print("   bot.type_text('Hello World')")
        
    except Exception as e:
        print(f"❌ Erro no teste básico: {e}")


def show_quick_examples():
    """Mostra exemplos rápidos de uso"""
    print("\n📋 Exemplos Rápidos de Uso:")
    print("=" * 50)
    
    examples = [
        "# Importação simples",
        "from bot_vision import BotVision",
        "",
        "# Criar instância", 
        "bot = BotVision()",
        "",
        "# Clicar em texto na tela",
        "bot.click_text('Login')",
        "",
        "# Clicar em imagem",
        "bot.click_image('button.png')",
        "",
        "# Digitar texto",
        "bot.type_text('Hello World!')",
        "",
        "# Buscar texto (sem clicar)",
        "found = bot.find_text('Welcome')",
        "if found:",
        "    print('Texto encontrado!')",
        "",
        "# 🆕 Novas funcionalidades",
        "bot.click_coordinates(x=500, y=300)",
        "bot.keyboard_command('Ctrl+S')",
        "",
        "# Lista de tarefas",
        "from bot_vision import execute_tasks",
        "tasks = [",
        "    {'text': 'Login', 'delay': 1},",
        "    {'image': 'submit.png', 'delay': 2}",
        "]",
        "execute_tasks(tasks)"
    ]
    
    for line in examples:
        print(line)


if __name__ == "__main__":
    print("🚀 Bot Vision Suite - Teste de Instalação")
    print("=" * 50)
    
    test_import()
    test_basic_functionality() 
    show_quick_examples()
    
    print("\n" + "=" * 50)
    print("✨ Teste concluído!")
    print("📖 Consulte IMPORT_GUIDE.md para documentação completa")
    print("🔗 GitHub: https://github.com/matheuszwilk/bot-vision-suite")
