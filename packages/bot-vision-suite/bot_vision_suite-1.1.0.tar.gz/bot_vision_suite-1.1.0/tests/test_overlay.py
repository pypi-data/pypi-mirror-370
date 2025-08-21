"""
🧪 Teste do Overlay - Bot Vision Suite

Script para testar se o overlay visual está funcionando corretamente.
"""

import time
import sys
import os

def test_overlay_basic():
    """Teste básico do overlay"""
    print("🔍 Testando overlay básico...")
    
    try:
        from bot_vision.core.overlay import VisualOverlay
        
        # Criar overlay
        overlay = VisualOverlay(color="red", width=4, duration=2000)
        
        # Testar região no centro da tela
        print("📍 Mostrando overlay no centro da tela por 2 segundos...")
        print("   (Você deve ver um retângulo vermelho)")
        
        # Região de teste (centro da tela aproximadamente)
        test_region = (400, 300, 200, 100)  # x, y, width, height
        
        overlay.show(test_region, blocking=True)
        
        print("✅ Teste básico concluído")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste básico: {e}")
        return False


def test_overlay_methods():
    """Testa diferentes métodos de overlay"""
    print("\n🔧 Testando métodos de overlay...")
    
    try:
        from bot_vision.core.overlay import VisualOverlay
        
        overlay = VisualOverlay(color="blue", width=6, duration=1500)
        
        # Teste 1: Verificar se Tkinter está disponível
        print(f"   Tkinter disponível: {overlay._tkinter_available}")
        
        # Teste 2: Tentar correção do Tkinter
        if not overlay._tkinter_available:
            print("   🔧 Tentando corrigir Tkinter...")
            fixed = overlay._fix_tkinter_environment()
            print(f"   Correção do Tkinter: {'✅ Sucesso' if fixed else '❌ Falhou'}")
        
        # Teste 3: Overlay em diferentes posições
        positions = [
            (100, 100, 150, 80, "Canto superior esquerdo"),
            (700, 100, 150, 80, "Canto superior direito"),
            (100, 400, 150, 80, "Canto inferior esquerdo"),
            (700, 400, 150, 80, "Canto inferior direito")
        ]
        
        for x, y, w, h, desc in positions:
            print(f"📍 Testando: {desc}")
            overlay.show((x, y, w, h), blocking=True)
            time.sleep(0.5)
        
        print("✅ Teste de métodos concluído")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de métodos: {e}")
        return False


def test_overlay_fallback():
    """Testa métodos de fallback"""
    print("\n🛡️ Testando métodos de fallback...")
    
    try:
        from bot_vision.core.overlay import VisualOverlay
        
        overlay = VisualOverlay(color="green", width=3, duration=2000)
        
        # Forçar uso do método alternativo (Windows)
        if os.name == 'nt':
            print("   🎯 Testando overlay alternativo (Windows API)...")
            overlay._create_overlay_alternative((300, 200, 300, 150))
            print("   ✅ Overlay alternativo testado")
        else:
            print("   ℹ️ Overlay alternativo só funciona no Windows")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de fallback: {e}")
        return False


def test_overlay_with_bot_vision():
    """Testa overlay através da classe BotVision"""
    print("\n🤖 Testando overlay com BotVision...")
    
    try:
        from bot_vision import BotVision
        
        # Criar bot com overlay habilitado
        bot = BotVision()
        bot.show_overlay = True
        
        print("   📍 Criando overlay através do BotVision...")
        print("   (Este teste simula o que acontece durante automação)")
        
        # Simular overlay como seria usado na automação
        if hasattr(bot, 'overlay') or hasattr(bot, '_overlay'):
            # Usar overlay interno do bot
            overlay = getattr(bot, 'overlay', None) or getattr(bot, '_overlay', None)
            if overlay:
                overlay.show((450, 250, 200, 100), blocking=True)
                print("   ✅ Overlay via BotVision funcionou")
            else:
                print("   ⚠️ Bot não tem overlay configurado")
        else:
            # Criar overlay diretamente
            from bot_vision.core.overlay import VisualOverlay
            overlay = VisualOverlay()
            overlay.show((450, 250, 200, 100), blocking=True)
            print("   ✅ Overlay direto funcionou")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste com BotVision: {e}")
        return False


def test_multiple_overlays():
    """Testa múltiplos overlays simultâneos"""
    print("\n🔢 Testando múltiplos overlays...")
    
    try:
        from bot_vision.core.overlay import VisualOverlay
        
        overlay = VisualOverlay(color="purple", width=5, duration=3000)
        
        # Várias regiões
        regions = [
            (200, 150, 100, 60),  # Região 1
            (400, 150, 100, 60),  # Região 2
            (600, 150, 100, 60),  # Região 3
            (300, 300, 200, 80),  # Região central
        ]
        
        print("   📍 Mostrando 4 overlays simultâneos por 3 segundos...")
        overlay.show_multiple(regions, blocking=True)
        
        print("   ✅ Múltiplos overlays testados")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de múltiplos overlays: {e}")
        return False


def test_overlay_functions():
    """Testa funções de conveniência"""
    print("\n🔧 Testando funções de conveniência...")
    
    try:
        from bot_vision.core.overlay import show_overlay, show_overlay_blocking
        
        print("   📍 Testando show_overlay (não bloqueante)...")
        show_overlay((350, 200, 180, 90), duration=1000, color="orange")
        time.sleep(1.2)  # Aguardar terminar
        
        print("   📍 Testando show_overlay_blocking (bloqueante)...")
        show_overlay_blocking((500, 350, 150, 70), duration=1500, color="cyan")
        
        print("   ✅ Funções de conveniência testadas")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de funções: {e}")
        return False


def main():
    """Executa todos os testes"""
    print("🧪 TESTE COMPLETO DO OVERLAY - BOT VISION SUITE")
    print("=" * 60)
    print("Este teste irá mostrar vários retângulos coloridos na sua tela.")
    print("Se você vê-los, o overlay está funcionando corretamente!\n")
    
    # Aguardar confirmação
    input("Pressione ENTER para começar os testes...")
    print()
    
    tests = [
        ("Overlay Básico", test_overlay_basic),
        ("Métodos de Overlay", test_overlay_methods),
        ("Métodos de Fallback", test_overlay_fallback),
        ("Overlay com BotVision", test_overlay_with_bot_vision),
        ("Múltiplos Overlays", test_multiple_overlays),
        ("Funções de Conveniência", test_overlay_functions),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro crítico em {test_name}: {e}")
            results.append((test_name, False))
        
        if test_func != tests[-1][1]:  # Não pausar no último teste
            print(f"\nAguardando 2 segundos antes do próximo teste...")
            time.sleep(2)
    
    # Resumo dos resultados
    print(f"\n{'='*60}")
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultados: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("🎉 OVERLAY FUNCIONANDO PERFEITAMENTE!")
    elif passed > len(results) // 2:
        print("⚠️ Overlay parcialmente funcional")
    else:
        print("❌ Overlay com problemas - verifique configuração")
    
    print("\n💡 Dicas:")
    print("- Se não viu nenhum retângulo: Tkinter não está funcionando")
    print("- Se viu alguns retângulos: Overlay está funcionando!")
    print("- Métodos de fallback são usados quando Tkinter falha")


if __name__ == "__main__":
    main()
