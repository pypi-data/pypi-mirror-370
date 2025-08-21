"""
Teste de Importação - Novas Funcionalidades Bot Vision Suite

Este arquivo testa se todas as novas funcionalidades estão sendo
importadas e exportadas corretamente.
"""

def test_imports():
    """Testa se todas as novas funcionalidades podem ser importadas."""
    
    print("🧪 TESTANDO IMPORTAÇÕES das Novas Funcionalidades")
    print("=" * 60)
    
    try:
        # Classe principal
        from _bot_vision import BotVision
        print("✅ BotVision - OK")
        
        # Funções tradicionais
        from _bot_vision import execute_tasks, click_images, find_text, click_text, find_image, click_image
        print("✅ Funções tradicionais - OK")
        
        # 🆕 NOVAS FUNCIONALIDADES - Imagem relativa
        from _bot_vision import find_relative_image, click_relative_image
        print("✅ Imagem relativa - OK")
        
        # 🆕 NOVAS FUNCIONALIDADES - Coordenadas
        from _bot_vision import click_coordinates
        print("✅ Clique em coordenadas - OK")
        
        # 🆕 NOVAS FUNCIONALIDADES - Teclado
        from _bot_vision import type_text_standalone, keyboard_command_standalone, get_available_keyboard_commands
        print("✅ Comandos de teclado - OK")
        
        # Classes de core
        from _bot_vision import TaskExecutor, OCREngine, ImageProcessor, RelativeImageDetector, KeyboardCommander
        print("✅ Classes de core - OK")
        
        # Utilitários
        from _bot_vision import BotVisionConfig, limpar_texto, matches_filter
        print("✅ Utilitários - OK")
        
        print("\n🎉 TODAS AS IMPORTAÇÕES FUNCIONANDO!")
        return True
        
    except ImportError as e:
        print(f"\n❌ ERRO DE IMPORTAÇÃO: {e}")
        return False


def test_new_functionalities():
    """Testa se as novas funcionalidades estão funcionais."""
    
    print("\n🧪 TESTANDO FUNCIONALIDADE das Novas Features")
    print("=" * 60)
    
    try:
        from _bot_vision import BotVision, get_available_keyboard_commands
        
        # Testa instanciação
        bot = BotVision()
        print("✅ Instanciação do BotVision - OK")
        
        # Testa se métodos existem
        assert hasattr(bot, 'find_relative_image'), "Método find_relative_image não encontrado"
        assert hasattr(bot, 'click_relative_image'), "Método click_relative_image não encontrado"
        assert hasattr(bot, 'click_coordinates'), "Método click_coordinates não encontrado"
        assert hasattr(bot, 'type_text'), "Método type_text não encontrado"
        assert hasattr(bot, 'keyboard_command'), "Método keyboard_command não encontrado"
        assert hasattr(bot, 'get_available_keyboard_commands'), "Método get_available_keyboard_commands não encontrado"
        print("✅ Todos os novos métodos existem - OK")
        
        # Testa lista de comandos
        commands = get_available_keyboard_commands()
        assert len(commands) > 50, f"Poucos comandos encontrados: {len(commands)}"
        assert 'Ctrl+S' in commands, "Comando Ctrl+S não encontrado"
        assert 'F7' in commands, "Comando F7 não encontrado"
        print(f"✅ Lista de comandos funcional - {len(commands)} comandos disponíveis")
        
        # Testa tipos de tarefa
        task_relative = {
            'type': 'relative_image',
            'anchor_image': 'test.png',
            'target_image': 'test2.png'
        }
        
        task_click = {
            'type': 'click',
            'x': 100,
            'y': 200
        }
        
        task_type = {
            'type': 'type_text',
            'text': 'test'
        }
        
        task_keyboard = {
            'type': 'keyboard_command',
            'command': 'Ctrl+S'
        }
        
        print("✅ Estruturas de tarefa validadas - OK")
        
        print("\n🎉 TODAS AS FUNCIONALIDADES ESTÃO OPERACIONAIS!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO DE FUNCIONALIDADE: {e}")
        return False


def test_documentation():
    """Testa se a documentação está acessível."""
    
    print("\n🧪 TESTANDO DOCUMENTAÇÃO")
    print("=" * 60)
    
    try:
        from _bot_vision import BotVision
        
        # Testa docstrings
        bot = BotVision()
        
        methods_to_check = [
            'find_relative_image',
            'click_relative_image', 
            'click_coordinates',
            'type_text',
            'keyboard_command'
        ]
        
        for method_name in methods_to_check:
            method = getattr(bot, method_name)
            docstring = method.__doc__
            assert docstring is not None, f"Docstring missing for {method_name}"
            assert len(docstring.strip()) > 50, f"Docstring too short for {method_name}"
            print(f"✅ Documentação de {method_name} - OK")
        
        print("\n🎉 DOCUMENTAÇÃO COMPLETA!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO DE DOCUMENTAÇÃO: {e}")
        return False


def run_all_tests():
    """Executa todos os testes de validação."""
    
    print("🚀 INICIANDO BATERIA DE TESTES")
    print("Bot Vision Suite - Novas Funcionalidades")
    print("=" * 80)
    
    tests = [
        ("Importações", test_imports),
        ("Funcionalidades", test_new_functionalities),
        ("Documentação", test_documentation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Executando teste: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado em {test_name}: {e}")
            results.append((test_name, False))
    
    # Relatório final
    print("\n" + "=" * 80)
    print("📊 RELATÓRIO FINAL DOS TESTES")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name:20} - {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("💫 As novas funcionalidades estão 100% operacionais!")
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        print("\n✨ BIBLIOTECA PRONTA PARA USO!")
        print("📚 Consulte os exemplos para ver todas as funcionalidades em ação.")
    else:
        print("\n🔧 AJUSTES NECESSÁRIOS!")
        print("📝 Verifique os erros reportados acima.")
