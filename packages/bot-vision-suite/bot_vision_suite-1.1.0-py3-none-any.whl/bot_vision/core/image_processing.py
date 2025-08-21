"""
Bot Vision Suite - Image Processing

Este módulo contém todas as técnicas de pré-processamento de imagem
otimizadas para melhorar a precisão do OCR.
"""

import logging
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter
from typing import List, Optional, Union

from ..exceptions import ImageProcessingError

logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Classe responsável pelo processamento de imagens para OCR.
    
    Implementa múltiplas técnicas de pré-processamento otimizadas
    com base em testes de performance para diferentes tipos de texto e fundos.
    """
    
    def __init__(self, methods: Union[str, List[str]] = "all"):
        """
        Inicializa o processador de imagens.
        
        Args:
            methods (str or list): Métodos a serem aplicados.
                                 "all" para todos, ou lista específica
        """
        self.methods = methods
        self.available_methods = [
            "hsv_enhancement",      # Método 28 - 62% confiança
            "threshold_variants",   # Variações de threshold
            "dark_background",      # Método 2 - 59% confiança  
            "channel_processing",   # Método 22 - 57% confiança
            "contrast_sharpening",  # Métodos 13 e 27 - 41% confiança
            "adaptive_threshold",   # Threshold adaptativo
            "color_masking",        # Máscaras de cor HSV
            "lab_enhancement",      # Processamento LAB
            "combinations"          # Combinações otimizadas
        ]
    
    def preprocess_for_ocr(self, img: Image.Image) -> List[Image.Image]:
        """
        Aplica técnicas de pré-processamento otimizadas com base nos resultados de execução.
        Foca em métodos que melhor detectaram números e remove métodos ineficazes.
        
        Esta função é uma cópia EXATA da função preprocess_image_for_ocr do bot_vision.py original.
        """
        # Lista para armazenar todas as versões processadas
        processed_images = []
        
        # Converte para array numpy para manipulação
        img_np = np.array(img)
        
        logger.debug(f"🔬 Iniciando processamento de imagem {img.size} com 19 técnicas otimizadas")
        
        # MÉTODO 1 (62% confiança) - Prioridade máxima
        # -----------------------------------------------------------------------------------
        # Versão com melhor detecção de números em caixas coloridas
        # Processamento HSV com ajustes específicos
        img_hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
        
        # Aumenta a saturação para destacar cores
        img_hsv[:,:,1] = np.clip(img_hsv[:,:,1] * 1.4, 0, 255).astype(np.uint8)
        img_enhanced = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2RGB)
        processed_images.append(Image.fromarray(img_enhanced))
        logger.debug("✓ Método 1/19: HSV Enhancement (saturação aumentada) - PRIORITÁRIO (62% eficácia)")
        
        # Versão com threshold específico - variação do método 28
        img_gray = cv2.cvtColor(img_enhanced, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY)
        processed_images.append(Image.fromarray(thresh))
        logger.debug("✓ Método 2/19: HSV Enhancement + Threshold específico")
        
        # MÉTODO 3 (59% confiança) - Segunda prioridade
        # -----------------------------------------------------------------------------------
        # Inversão para texto claro em fundo escuro
        _, dark_bg_thresh = cv2.threshold(np.array(img.convert("L")), 160, 255, cv2.THRESH_BINARY_INV)
        processed_images.append(Image.fromarray(dark_bg_thresh))
        logger.debug("✓ Método 3/19: Inversão texto claro/fundo escuro (59% eficácia)")
        
        # Variação do método 2 com diferentes thresholds
        dark_thresholds = [140, 160, 180]
        for i, thresh_val in enumerate(dark_thresholds):
            _, dark_var = cv2.threshold(np.array(img.convert("L")), thresh_val, 255, cv2.THRESH_BINARY_INV)
            processed_images.append(Image.fromarray(dark_var))
            logger.debug(f"✓ Método {4+i}/19: Inversão com threshold {thresh_val}")
        
        # MÉTODO 7 (57% confiança) - Terceira prioridade
        # -----------------------------------------------------------------------------------
        # Processamento de canais de cor e detecção específica
        r_channel = img_np[:,:,0]
        g_channel = img_np[:,:,1]
        b_channel = img_np[:,:,2]
        
        # Variações de manipulação de canais
        # Detecção de canais com base em diferenças entre R, G, B
        channel_diff = np.absolute(r_channel.astype(np.int16) - b_channel.astype(np.int16))
        channel_diff = np.clip(channel_diff * 2, 0, 255).astype(np.uint8)
        _, channel_thresh = cv2.threshold(channel_diff, 30, 255, cv2.THRESH_BINARY)
        processed_images.append(Image.fromarray(channel_thresh))
        logger.debug("✓ Método 7/19: Processamento canais RGB (diferença R-B) (57% eficácia)")
        
        # MÉTODO 8 (41% confiança) e MÉTODO 9 (41% confiança)
        # -----------------------------------------------------------------------------------
        # Versões com alta nitidez e contraste
        gray = img.convert("L")
        
        # Contraste alto + nitidez (otimizado)
        contrast_sharp = ImageEnhance.Contrast(gray).enhance(2.5).filter(ImageFilter.SHARPEN)
        processed_images.append(contrast_sharp)
        logger.debug("✓ Método 8/19: Contraste alto + nitidez (41% eficácia)")
        
        # Nitidez adicional para melhorar bordas
        extra_sharp = contrast_sharp.filter(ImageFilter.SHARPEN).filter(ImageFilter.SHARPEN)
        processed_images.append(extra_sharp)
        logger.debug("✓ Método 9/19: Nitidez extra (dupla aplicação)")
        
        # TÉCNICAS PARA TEXTO CLARO EM FUNDO ESCURO (cinza, preto)
        # -----------------------------------------------------------------------------------
        # Inversão simples (útil para texto branco em fundo escuro)
        inverted = Image.fromarray(255 - img_np)
        processed_images.append(inverted)
        logger.debug("✓ Método 10/19: Inversão completa da imagem")
        
        # Thresholding adaptativo para texto em fundo escuro
        cv_gray = np.array(gray)
        
        # Adaptativo com diferentes janelas - melhor para números pequenos em fundos variados
        adaptive_thresh1 = cv2.adaptiveThreshold(
            cv_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, 2
        )
        processed_images.append(Image.fromarray(adaptive_thresh1))
        logger.debug("✓ Método 11/19: Threshold adaptativo Gaussiano")
        
        adaptive_thresh2 = cv2.adaptiveThreshold(
            cv_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 3
        )
        processed_images.append(Image.fromarray(adaptive_thresh2))
        logger.debug("✓ Método 12/19: Threshold adaptativo por média")
        
        # MANIPULAÇÃO DE COR PARA FUNDOS COLORIDOS (rosa, cinza)
        # -----------------------------------------------------------------------------------
        # Rosa/roxo claro em HSV com faixas mais precisas
        lower_pink = np.array([140, 50, 150])
        upper_pink = np.array([170, 255, 255])
        pink_mask_hsv = cv2.inRange(img_hsv, lower_pink, upper_pink)
        pink_mask_inv = cv2.bitwise_not(pink_mask_hsv)
        processed_images.append(Image.fromarray(pink_mask_inv))
        logger.debug("✓ Método 13/19: Máscara HSV para fundos rosa/roxo")
        
        # Cinza claro em HSV
        lower_gray = np.array([0, 0, 180])
        upper_gray = np.array([180, 30, 255])
        gray_mask_hsv = cv2.inRange(img_hsv, lower_gray, upper_gray)
        gray_mask_inv = cv2.bitwise_not(gray_mask_hsv)
        processed_images.append(Image.fromarray(gray_mask_inv))
        logger.debug("✓ Método 14/19: Máscara HSV para fundos cinza claro")
        
        # Cinza escuro/preto
        lower_dark_gray = np.array([0, 0, 0])
        upper_dark_gray = np.array([180, 30, 80])
        dark_gray_mask = cv2.inRange(img_hsv, lower_dark_gray, upper_dark_gray)
        dark_gray_mask_inv = cv2.bitwise_not(dark_gray_mask)
        processed_images.append(Image.fromarray(dark_gray_mask_inv))
        logger.debug("✓ Método 15/19: Máscara HSV para fundos cinza escuro/preto")
        
        # EQUALIZAÇÃO E APRIMORAMENTO DE LUMINOSIDADE
        # -----------------------------------------------------------------------------------
        # Lab color space processing - bom para números em fundos coloridos diversos
        lab_img = cv2.cvtColor(img_np, cv2.COLOR_RGB2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab_img)
        
        # Equaliza o canal L (luminosidade) - técnica que foi bem sucedida
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l_channel)
        
        # Recombina os canais
        updated_lab_img = cv2.merge((cl, a_channel, b_channel))
        
        # Converte de volta para RGB e depois para escala de cinza
        enhanced_img = cv2.cvtColor(updated_lab_img, cv2.COLOR_LAB2RGB)
        enhanced_gray = cv2.cvtColor(enhanced_img, cv2.COLOR_RGB2GRAY)
        
        # Aplica thresholding na imagem melhorada
        _, binary_enhanced = cv2.threshold(enhanced_gray, 127, 255, cv2.THRESH_BINARY)
        processed_images.append(Image.fromarray(binary_enhanced))
        logger.debug("✓ Método 16/19: Lab color space + CLAHE")
        
        # Versão invertida para texto claro em fundo escuro
        _, binary_enhanced_inv = cv2.threshold(enhanced_gray, 127, 255, cv2.THRESH_BINARY_INV)
        processed_images.append(Image.fromarray(binary_enhanced_inv))
        logger.debug("✓ Método 17/19: Lab color space + CLAHE invertido")
        
        # COMBINAÇÕES OTIMIZADAS - mescla técnicas bem sucedidas
        # -----------------------------------------------------------------------------------
        
        # Combinação: alta nitidez + contraste elevado
        contrast_highest = ImageEnhance.Contrast(gray).enhance(3.0)
        sharpened_strong = contrast_highest.filter(ImageFilter.SHARPEN).filter(ImageFilter.SHARPEN)
        processed_images.append(sharpened_strong)
        logger.debug("✓ Método 18/19: Contraste máximo + nitidez dupla")
        
        # Mescla lab e hsv para capturar o melhor dos dois mundos
        merged_img = cv2.addWeighted(enhanced_gray, 0.5, img_gray, 0.5, 0)
        _, merged_thresh = cv2.threshold(merged_img, 140, 255, cv2.THRESH_BINARY)
        processed_images.append(Image.fromarray(merged_thresh))
        logger.debug("✓ Método 19/19: Combinação Lab + HSV otimizada")
        
        # Filtra imagens válidas
        valid_images = []
        for img_proc in processed_images:
            try:
                if img_proc.mode in ['RGB', 'L', '1']:
                    valid_images.append(img_proc)
            except Exception as e:
                logger.debug(f"Erro ao processar uma das imagens: {e}")
        
        logger.info(f"🔬 Processamento concluído: {len(valid_images)} variações geradas")
        print(f"Gerando {len(valid_images)} variações otimizadas de pré-processamento para OCR")
        
        return valid_images


# Função standalone para compatibilidade total com o código original
def preprocess_image_for_ocr(img: Image.Image) -> List[Image.Image]:
    """
    Função standalone que replica exatamente a função original do bot_vision.py.
    
    Args:
        img (Image.Image): Imagem a ser processada
        
    Returns:
        List[Image.Image]: Lista de imagens processadas
    """
    processor = ImageProcessor()
    return processor.preprocess_for_ocr(img)


def get_available_methods() -> List[str]:
    """
    Retorna lista de métodos de processamento disponíveis.
    
    Returns:
        list: Lista de métodos disponíveis
    """
    processor = ImageProcessor()
    return processor.available_methods
