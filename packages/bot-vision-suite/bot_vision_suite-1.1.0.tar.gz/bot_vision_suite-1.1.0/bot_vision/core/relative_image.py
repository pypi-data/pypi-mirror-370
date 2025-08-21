"""
Bot Vision Suite - Relative Image Detection

Este módulo implementa a detecção de imagens relativas (âncora + target),
permitindo localizar uma imagem target próxima a uma imagem âncora.
"""

import logging
import pyautogui
from typing import Optional, Tuple, List
from ..exceptions import ImageNotFoundError

logger = logging.getLogger(__name__)


class RelativeImageDetector:
    """
    Detector de imagens relativas.
    
    Permite localizar uma imagem target próxima a uma imagem âncora,
    útil quando há múltiplas ocorrências da imagem target na tela.
    """
    
    def __init__(self):
        """Inicializa o detector de imagens relativas."""
        pass
    
    def locate_relative_image(self, anchor_image_path: str, target_image_path: str, 
                            confidence: float = 0.9, max_distance: int = 200, 
                            target_region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple]:
        """
        Localiza uma imagem target próxima a uma imagem anchor.
        
        Args:
            anchor_image_path: Caminho para a imagem âncora (única na tela)
            target_image_path: Caminho para a imagem alvo (pode ter múltiplas)
            confidence: Nível de confiança para detecção (0.0-1.0)
            max_distance: Distância máxima em pixels da âncora ao target
            target_region: Região específica para buscar a target image (x, y, width, height)
        
        Returns:
            Localização da imagem target mais próxima da anchor ou None
            
        Raises:
            ImageNotFoundError: Se a imagem âncora não for encontrada
        """
        try:
            # Primeiro, localiza a imagem âncora (sempre na tela inteira)
            logger.info(f"Procurando imagem âncora: {anchor_image_path}")
            anchor_location = pyautogui.locateOnScreen(anchor_image_path, confidence=confidence)
            
            if not anchor_location:
                raise ImageNotFoundError(f"Imagem âncora não encontrada: {anchor_image_path}")
            
            logger.info(f"Imagem âncora encontrada em: {anchor_location}")
            anchor_center = pyautogui.center(anchor_location)
            
            # Agora procura todas as ocorrências da imagem target
            logger.info(f"Procurando imagem target: {target_image_path}")
            
            # Se target_region foi especificada, busca apenas nessa região
            if target_region:
                logger.info(f"Buscando target na região específica: {target_region}")
                target_locations = list(pyautogui.locateAllOnScreen(
                    target_image_path, region=target_region, confidence=confidence))
            else:
                # Busca na tela inteira
                target_locations = list(pyautogui.locateAllOnScreen(
                    target_image_path, confidence=confidence))
            
            if not target_locations:
                region_info = f"na região {target_region}" if target_region else "na tela inteira"
                logger.warning(f"Imagem target não encontrada {region_info}: {target_image_path}")
                return None
            
            logger.info(f"Encontradas {len(target_locations)} ocorrências da imagem target")
            
            # Calcula a distância de cada target à âncora e encontra o mais próximo
            closest_target = None
            min_distance = float('inf')
            
            for target_location in target_locations:
                target_center = pyautogui.center(target_location)
                
                # Calcula distância euclidiana
                distance = ((target_center.x - anchor_center.x) ** 2 + 
                           (target_center.y - anchor_center.y) ** 2) ** 0.5
                
                logger.info(f"Target em {target_location} está a {distance:.1f}px da âncora")
                
                # Verifica se está dentro da distância máxima e é o mais próximo
                if distance <= max_distance and distance < min_distance:
                    min_distance = distance
                    closest_target = target_location
            
            if closest_target:
                logger.info(f"Target mais próximo selecionado: {closest_target} "
                           f"(distância: {min_distance:.1f}px)")
                return closest_target
            else:
                logger.warning(f"Nenhuma imagem target encontrada dentro de "
                              f"{max_distance}px da âncora")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao localizar imagem relativa: {e}")
            raise ImageNotFoundError(f"Erro na detecção de imagem relativa: {e}")
    
    def locate_image_with_retry(self, image_path: str, region: Optional[Tuple] = None, 
                              confidence: float = 0.9, max_attempts: int = 3, 
                              scales: Optional[List[float]] = None) -> Optional[Tuple]:
        """
        Tenta localizar uma imagem com diferentes escalas e níveis de confiança.
        
        Args:
            image_path: Caminho para a imagem
            region: Região para buscar (x, y, width, height)
            confidence: Nível de confiança inicial
            max_attempts: Número máximo de tentativas
            scales: Lista de escalas a testar (None para usar padrão)
            
        Returns:
            Localização da imagem ou None se não encontrada
        """
        import os
        from PIL import Image
        
        if scales is None:
            scales = [1.0, 0.95, 1.05]  # Tenta com escala original e ±5%
        
        for attempt in range(max_attempts):
            # Tenta localizar com diferentes escalas
            for scale in scales:
                try:
                    if scale != 1.0:
                        # Carrega e redimensiona a imagem de referência
                        ref_img = Image.open(image_path)
                        new_width = int(ref_img.width * scale)
                        new_height = int(ref_img.height * scale)
                        scaled_img = ref_img.resize((new_width, new_height))
                        
                        # Salva temporariamente para usar com pyautogui
                        temp_path = f"temp_scaled_{scale}.png"
                        scaled_img.save(temp_path)
                        
                        if region:
                            location = pyautogui.locateOnScreen(temp_path, region=region, confidence=confidence)
                        else:
                            location = pyautogui.locateOnScreen(temp_path, confidence=confidence)
                        
                        os.remove(temp_path)  # Limpa arquivo temporário
                    else:
                        if region:
                            location = pyautogui.locateOnScreen(image_path, region=region, confidence=confidence)
                        else:
                            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
                    
                    if location:
                        return location
                except Exception as e:
                    logger.debug(f"Erro ao buscar imagem com escala {scale}: {e}")
                    continue
            
            # Se a escala não funcionou, tente reduzir a confiança
            adjusted_confidence = max(0.7, confidence - 0.05 * (attempt + 1))
            logger.debug(f"Ajustando confiança para {adjusted_confidence}")
            
            try:
                if region:
                    location = pyautogui.locateOnScreen(image_path, region=region, confidence=adjusted_confidence)
                else:
                    location = pyautogui.locateOnScreen(image_path, confidence=adjusted_confidence)
                
                if location:
                    return location
            except Exception as e:
                logger.debug(f"Erro ao buscar imagem com confiança ajustada: {e}")
            
            # Pequena pausa entre tentativas
            import time
            time.sleep(0.5)
        
        return None
