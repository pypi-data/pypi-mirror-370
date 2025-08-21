"""
Bot Vision Suite - Text Filters

Este módulo contém funções para limpeza e filtragem de texto extraído via OCR.
"""

import re
import logging

logger = logging.getLogger(__name__)


def limpar_texto(texto, filter_type="both"):
    """
    Remove caracteres do texto conforme o filtro desejado.
    
    Args:
        texto (str): Texto a ser limpo
        filter_type (str): Tipo de filtro a ser aplicado:
            - "numbers": remove tudo, exceto dígitos
            - "letters": remove tudo, exceto letras (incluindo acentuadas)
            - "both": remove todos os caracteres que não sejam letras ou dígitos
            - outro: remove apenas caracteres especiais do início e fim
    
    Returns:
        str: Texto limpo conforme o filtro especificado
    
    Examples:
        >>> limpar_texto("  123abc!  ", "numbers")
        "123"
        >>> limpar_texto("  123abc!  ", "letters")
        "abc"
        >>> limpar_texto("  123abc!  ", "both")
        "123abc"
    """
    if not isinstance(texto, str):
        logger.warning(f"Entrada não é string: {type(texto)}")
        return ""
    
    texto = texto.strip()
    
    if filter_type == "numbers":
        texto = re.sub(r"[^\d]", "", texto)
    elif filter_type == "letters":
        texto = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ]", "", texto)
    elif filter_type == "both":
        # Permite letras e números
        texto = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ0-9]", "", texto)
    else:
        # Remove apenas caracteres especiais do início e fim
        texto = re.sub(r'^[\W_]+|[\W_]+$', '', texto)
    
    return texto


def matches_filter(word, filter_type):
    """
    Verifica se a palavra corresponde ao filtro desejado.
    
    Args:
        word (str): Palavra a ser verificada
        filter_type (str): Tipo de filtro:
            - "numbers": apenas dígitos entre 1 e 31
            - "letters": apenas letras (incluindo acentuadas)
            - "both": apenas letras e números
            - outro: retorna True
    
    Returns:
        bool: True se a palavra corresponde ao filtro, False caso contrário
    
    Examples:
        >>> matches_filter("123", "numbers")
        True
        >>> matches_filter("abc", "letters")
        True
        >>> matches_filter("abc123", "both")
        True
        >>> matches_filter("32", "numbers")  # Fora do range 1-31
        False
    """
    if not isinstance(word, str):
        return False
    
    filter_type = filter_type.lower()
    
    if filter_type == "numbers":
        if not re.fullmatch(r"\d+", word):
            return False
        try:
            num = int(word)
            return 1 <= num <= 31
        except ValueError:
            return False
    elif filter_type == "letters":
        return re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ]+", word) is not None
    elif filter_type == "both":
        return re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", word) is not None
    
    return True


def validate_text_input(text, filter_type="both"):
    """
    Valida e limpa um texto de entrada.
    
    Args:
        text (str): Texto a ser validado
        filter_type (str): Tipo de filtro a ser aplicado
    
    Returns:
        str: Texto validado e limpo
    
    Raises:
        ValueError: Se o texto for inválido após limpeza
    """
    if not text:
        raise ValueError("Texto não pode ser vazio")
    
    cleaned_text = limpar_texto(text, filter_type)
    
    if not cleaned_text:
        raise ValueError(f"Texto '{text}' não contém caracteres válidos para filtro '{filter_type}'")
    
    return cleaned_text


def extract_numbers_from_text(text):
    """
    Extrai todos os números de um texto.
    
    Args:
        text (str): Texto de origem
    
    Returns:
        list: Lista de números encontrados como strings
    
    Examples:
        >>> extract_numbers_from_text("Página 5 de 10 itens")
        ["5", "10"]
    """
    if not isinstance(text, str):
        return []
    
    return re.findall(r'\d+', text)


def extract_letters_from_text(text):
    """
    Extrai todas as sequências de letras de um texto.
    
    Args:
        text (str): Texto de origem
    
    Returns:
        list: Lista de sequências de letras encontradas
    
    Examples:
        >>> extract_letters_from_text("Item123abc456def")
        ["Item", "abc", "def"]
    """
    if not isinstance(text, str):
        return []
    
    return re.findall(r'[A-Za-zÀ-ÖØ-öø-ÿ]+', text)
