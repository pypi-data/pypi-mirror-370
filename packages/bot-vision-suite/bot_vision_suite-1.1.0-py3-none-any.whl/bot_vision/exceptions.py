"""
Bot Vision Suite - Custom Exceptions

Este módulo define todas as exceções customizadas usadas pela biblioteca.
"""


class BotVisionError(Exception):
    """Exceção base para todos os erros do Bot Vision Suite."""
    pass


class TesseractNotFoundError(BotVisionError):
    """Levantada quando o Tesseract OCR não é encontrado no sistema."""
    pass


class ImageNotFoundError(BotVisionError):
    """Levantada quando uma imagem não é encontrada na tela."""
    pass


class TextNotFoundError(BotVisionError):
    """Levantada quando um texto não é encontrado na região especificada."""
    pass


class InvalidRegionError(BotVisionError):
    """Levantada quando uma região inválida é especificada."""
    pass


class TaskExecutionError(BotVisionError):
    """Levantada quando há erro na execução de uma task."""
    pass


class ConfigurationError(BotVisionError):
    """Levantada quando há erro na configuração da biblioteca."""
    pass


class OCRProcessingError(BotVisionError):
    """Levantada quando há erro no processamento OCR."""
    pass


class ImageProcessingError(BotVisionError):
    """Levantada quando há erro no processamento de imagem."""
    pass
