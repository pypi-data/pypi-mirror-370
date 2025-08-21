"""
🎨 Exemplo de Configuração do Overlay - Bot Vision Suite

Este exemplo demonstra como usar as configurações de overlay.
"""

from bot_vision import BotVision

def exemplo_configuracao_overlay():
    """Demonstra como configurar overlay"""
    print("🎨 EXEMPLO DE CONFIGURAÇÃO DO OVERLAY")
    print("=" * 50)
    
    # Método 1: Configuração via dicionário na inicialização
    print("\n📦 Método 1: Configuração na inicialização")
    config = {
        "confidence_threshold": 85.0,
        "retry_attempts": 3,
        "overlay_duration": 2000,     # 2 segundos
        "overlay_color": "blue",      # Azul
        "overlay_width": 6,           # Linha mais grossa
        "show_overlay": True,         # Habilitado
        "overlay_enabled": True,      # Sistema ativo
        "ocr_languages": ["eng", "por"],
        "log_level": "INFO"
    }
    
    bot1 = BotVision(config)
    print("✅ Bot criado com overlay AZUL, 2 segundos, linha grossa")
    print(f"📊 Configuração: {bot1.get_overlay_config()}")
    
    # Método 2: Configuração depois da inicialização
    print("\n🔧 Método 2: Configuração após inicialização")
    bot2 = BotVision()
    bot2.configure_overlay(
        enabled=True,
        color="green",
        duration=1500,  # 1.5 segundos
        width=8
    )
    print("✅ Bot configurado com overlay VERDE, 1.5 segundos, linha extra grossa")
    print(f"📊 Configuração: {bot2.get_overlay_config()}")
    
    # Método 3: Propriedades individuais
    print("\n⚙️ Método 3: Propriedades individuais")
    bot3 = BotVision()
    bot3.show_overlay = True
    bot3.config.config["overlay_color"] = "purple"
    bot3.config.config["overlay_duration"] = 3000  # 3 segundos
    print("✅ Bot configurado com overlay ROXO, 3 segundos")
    print(f"📊 Configuração: {bot3.get_overlay_config()}")
    
    # Método 4: Desabilitar overlay
    print("\n❌ Método 4: Desabilitar overlay")
    bot4 = BotVision()
    bot4.configure_overlay(enabled=False)
    print("✅ Bot com overlay desabilitado")
    print(f"📊 Configuração: {bot4.get_overlay_config()}")
    
    print("\n" + "=" * 50)
    print("🎯 RESUMO DAS OPÇÕES:")
    print("=" * 50)
    print("🔧 CONFIGURAÇÕES DISPONÍVEIS:")
    print("   • overlay_enabled: True/False - Liga/desliga sistema")
    print("   • show_overlay: True/False - Mostra overlay nos cliques")
    print("   • overlay_color: 'red', 'blue', 'green', 'yellow', etc.")
    print("   • overlay_duration: 1000, 2000, 3000... (milissegundos)")
    print("   • overlay_width: 4, 6, 8... (espessura da linha)")
    
    print("\n🎨 CORES DISPONÍVEIS:")
    print("   • red, blue, green, yellow")
    print("   • purple, orange, cyan, magenta")
    print("   • white, black")
    
    print("\n💡 DICAS:")
    print("   • Para produção: configure overlay_enabled=False")
    print("   • Para debug: use cores vibrantes e duração maior")
    print("   • Para automação rápida: duração menor (500-1000ms)")


def exemplo_uso_pratico():
    """Exemplo prático de uso"""
    print("\n\n🚀 EXEMPLO PRÁTICO")
    print("=" * 50)
    
    # Configuração para desenvolvimento/debug
    config_debug = {
        "overlay_duration": 2000,
        "overlay_color": "blue", 
        "overlay_width": 6,
        "show_overlay": True,
        "log_level": "DEBUG"
    }
    
    bot = BotVision(config_debug)
    
    print("🔍 Bot configurado para debug:")
    print("   • Overlay azul, 2 segundos, linha grossa")
    print("   • Perfeito para ver onde está clicando")
    
    print("\n📝 Exemplo de uso:")
    print("   bot = BotVision(config_debug)")
    print("   bot.click_text('Login')  # Mostrará overlay azul antes do clique")
    print("   bot.click_image('button.png')  # Overlay aparecerá na imagem encontrada")
    
    # Configuração para produção
    print("\n⚡ Para produção (sem overlay):")
    config_prod = {
        "overlay_enabled": False,
        "show_overlay": False,
        "log_level": "ERROR"
    }
    
    print("   bot_prod = BotVision(config_prod)")
    print("   # Execução rápida sem feedback visual")


def exemplo_cores_overlay():
    """Demonstra todas as cores disponíveis"""
    print("\n🎨 EXEMPLO DE CORES DO OVERLAY")
    print("=" * 50)
    
    from bot_vision import BotVision
    
    # Listar cores disponíveis
    cores_disponiveis = BotVision.get_available_overlay_colors()
    print("🌈 Cores disponíveis:")
    for i, cor in enumerate(cores_disponiveis, 1):
        print(f"   {i:2d}. {cor}")
    
    # Configurações para cada cor
    print("\n🔧 Exemplos de configuração:")
    
    configuracoes_exemplo = [
        {"color": "red", "desc": "Vermelho - padrão, boa visibilidade"},
        {"color": "blue", "desc": "Azul - profissional, suave"},
        {"color": "green", "desc": "Verde - sucesso, natureza"},
        {"color": "yellow", "desc": "Amarelo - atenção, destaque"},
        {"color": "purple", "desc": "Roxo - criativo, diferenciado"},
        {"color": "orange", "desc": "Laranja - energia, vibrante"},
        {"color": "cyan", "desc": "Ciano - tecnológico, moderno"},
        {"color": "magenta", "desc": "Magenta - forte, chamativo"},
        {"color": "white", "desc": "Branco - minimalista, contraste"},
        {"color": "black", "desc": "Preto - elegante, discreto"}
    ]
    
    for config in configuracoes_exemplo:
        print(f"   • {config['color']:8} - {config['desc']}")
    
    print("\n💡 Exemplo de uso:")
    print("   bot = BotVision()")
    print("   bot.configure_overlay(color='blue', duration=2000)")
    print("   bot.configure_overlay(color='green', width=8)")
    
    # Validação de cores
    print("\n⚠️ Validação automática:")
    try:
        bot = BotVision()
        bot.configure_overlay(color="azul")  # Vai dar erro
    except ValueError as e:
        print(f"   ❌ Erro capturado: {e}")
    
    print("   ✅ Use apenas as cores da lista acima!")


def exemplo_teste_visual():
    """Exemplo para testar cores visualmente"""
    print("\n👁️ TESTE VISUAL DE CORES")
    print("=" * 50)
    
    from bot_vision import BotVision
    
    print("Para testar todas as cores visualmente:")
    print("   bot = BotVision()")
    print("   bot.test_overlay_colors()  # Mostra cada cor por 1.5s")
    print("   bot.test_overlay_colors(duration=3000)  # 3 segundos cada")
    
    print("\nPara testar uma cor específica:")
    print("   bot.configure_overlay(color='blue', duration=2000)")
    print("   # Agora todos os cliques mostrarão overlay azul")


def exemplo_configuracoes_praticas():
    """Exemplos práticos de configuração"""
    print("\n🚀 CONFIGURAÇÕES PRÁTICAS")
    print("=" * 50)
    
    configs = {
        "🔴 Debug Intenso": {
            "overlay_color": "red",
            "overlay_duration": 3000,
            "overlay_width": 8,
            "show_overlay": True,
            "desc": "Para debug detalhado - vermelho, 3s, linha grossa"
        },
        
        "🔵 Desenvolvimento": {
            "overlay_color": "blue", 
            "overlay_duration": 1500,
            "overlay_width": 6,
            "show_overlay": True,
            "desc": "Para desenvolvimento - azul, 1.5s, visível"
        },
        
        "🟢 Teste Rápido": {
            "overlay_color": "green",
            "overlay_duration": 800,
            "overlay_width": 4,
            "show_overlay": True,
            "desc": "Para testes rápidos - verde, 0.8s"
        },
        
        "🟡 Demonstração": {
            "overlay_color": "yellow",
            "overlay_duration": 2500,
            "overlay_width": 10,
            "show_overlay": True,
            "desc": "Para demonstrações - amarelo, 2.5s, bem visível"
        },
        
        "⚫ Produção": {
            "overlay_enabled": False,
            "show_overlay": False,
            "desc": "Para produção - sem overlay, máxima velocidade"
        }
    }
    
    for nome, config in configs.items():
        print(f"\n{nome}:")
        print(f"   {config['desc']}")
        
        # Remover desc para mostrar config limpa
        config_limpa = {k: v for k, v in config.items() if k != 'desc'}
        
        print(f"   Configuração: {config_limpa}")
        print(f"   Uso: bot = BotVision({config_limpa})")


if __name__ == "__main__":
    exemplo_configuracao_overlay()
    exemplo_cores_overlay()
    exemplo_teste_visual() 
    exemplo_configuracoes_praticas()
    exemplo_uso_pratico()
    
    print("\n🎉 RESUMO FINAL")
    print("=" * 50)
    print("✅ 10 cores disponíveis: red, blue, green, yellow, purple, orange, cyan, magenta, white, black")
    print("✅ Validação automática de parâmetros")
    print("✅ Métodos convenientes para configuração")
    print("✅ Função de teste visual: bot.test_overlay_colors()")
    print("✅ Configurações práticas para diferentes cenários")
    
    print("\n🔥 DICA FINAL:")
    print("   Use BotVision.get_available_overlay_colors() para ver todas as opções!")
