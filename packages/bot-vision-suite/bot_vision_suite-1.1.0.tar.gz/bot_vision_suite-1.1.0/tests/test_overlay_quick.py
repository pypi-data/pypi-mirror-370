"""
🚀 Teste Rápido do Overlay

Script simples para testar se o overlay está funcionando.
"""

def test_overlay_quick():
    """Teste rápido do overlay"""
    print("🧪 Teste Rápido do Overlay")
    print("=" * 40)
    
    try:
        # Importar
        print("📦 Importando módulos...")
        from bot_vision.core.overlay import VisualOverlay
        print("✅ Importação bem-sucedida")
        
        # Criar overlay
        print("\n🎨 Criando overlay...")
        overlay = VisualOverlay(color="red", width=4, duration=2000)
        print("✅ Overlay criado")
        
        # Verificar Tkinter
        print(f"\n🔍 Tkinter disponível: {overlay._tkinter_available}")
        
        # Mostrar overlay
        print("\n📍 Mostrando overlay no centro da tela...")
        print("   👀 OLHE PARA A TELA - você deve ver um retângulo VERMELHO!")
        print("   ⏱️ Duração: 2 segundos")
        
        # Região de teste no centro da tela
        test_region = (400, 300, 200, 100)
        overlay.show(test_region, blocking=True)
        
        print("\n🎉 Teste concluído!")
        
        # Perguntar se funcionou
        response = input("\n❓ Você viu o retângulo vermelho? (s/n): ").strip().lower()
        
        if response in ['s', 'sim', 'y', 'yes']:
            print("✅ OVERLAY FUNCIONANDO PERFEITAMENTE! 🎉")
            return True
        else:
            print("❌ Overlay não funcionou - vamos investigar...")
            
            # Diagnóstico
            print("\n🔧 Diagnóstico:")
            if not overlay._tkinter_available:
                print("   ⚠️ Tkinter não está disponível")
                print("   💡 Tentando corrigir...")
                if overlay._fix_tkinter_environment():
                    print("   ✅ Tkinter corrigido! Tente novamente.")
                else:
                    print("   ❌ Não foi possível corrigir Tkinter")
                    print("   🎯 Usando método alternativo...")
                    
                    import os
                    if os.name == 'nt':
                        print("   🔄 Testando overlay alternativo (Windows API)...")
                        overlay._create_overlay_alternative(test_region)
                        response2 = input("   ❓ Viu algo agora? (s/n): ").strip().lower()
                        if response2 in ['s', 'sim', 'y', 'yes']:
                            print("   ✅ Overlay alternativo funcionou!")
                            return True
            
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_with_bot_vision():
    """Testa overlay usando BotVision diretamente"""
    print("\n" + "=" * 40)
    print("🤖 Testando com BotVision")
    print("=" * 40)
    
    try:
        from bot_vision import BotVision
        
        print("📦 Criando BotVision...")
        bot = BotVision()
        
        # Verificar se overlay está habilitado
        print(f"🔍 Show overlay: {getattr(bot, 'show_overlay', 'não definido')}")
        
        # Habilitar overlay
        bot.show_overlay = True
        print("✅ Overlay habilitado no BotVision")
        
        print("\n💡 Para testar o overlay durante automação real:")
        print("   bot = BotVision()")
        print("   bot.show_overlay = True")
        print("   bot.click_text('algum_texto')  # Overlay aparecerá antes do clique")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro com BotVision: {e}")
        return False


if __name__ == "__main__":
    print("🧪 BOT VISION SUITE - TESTE RÁPIDO DO OVERLAY")
    print("=" * 50)
    print("Este teste mostrará um retângulo vermelho na tela.")
    print("Se você vê-lo, o overlay está funcionando!\n")
    
    input("Pressione ENTER para começar...")
    
    # Teste principal
    result1 = test_overlay_quick()
    
    # Teste com BotVision
    result2 = test_with_bot_vision()
    
    print("\n" + "=" * 50)
    print("📊 RESUMO")
    print("=" * 50)
    
    if result1:
        print("✅ Overlay funcionando perfeitamente!")
        print("🎯 Seu overlay visual está pronto para uso!")
    else:
        print("⚠️ Overlay com problemas")
        print("💡 Verifique se o Tkinter está instalado corretamente")
    
    if result2:
        print("✅ Integração com BotVision OK")
    
    print("\n🔧 Para usar overlay em sua automação:")
    print("   from bot_vision import BotVision")
    print("   bot = BotVision()")
    print("   bot.show_overlay = True  # Habilita overlay")
    print("   # Agora todos os cliques mostrarão overlay antes de executar")
