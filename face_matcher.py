import face_recognition
import cv2
import json
import numpy as np
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from config import Config
from utils import setup_logger, validate_image_file


@dataclass
class MatchResult:
    """Resultado de una coincidencia de rostro."""
    face_id: int
    frame: int
    timestamp: float
    confidence: float
    location: Tuple[int, int, int, int]
    quality: Dict[str, float]
    capture_path: str


class FaceMatcher:
    """Clase optimizada para comparación de rostros."""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.logger = setup_logger('face_matcher', self.config.LOG_FILE)
        self.known_encodings = []
        self.face_data = []
        
    def load_encodings(self, encodings_file: str = None) -> bool:
        """Carga las codificaciones de rostros desde archivo JSON."""
        file_path = Path(encodings_file or self.config.ENCODINGS_FILE)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Compatibilidad con diferentes versiones del formato
            if 'faces' in data:
                faces_data = data['faces']
                metadata = data.get('metadata', {})
                self.logger.info(f"Formato v2.0 detectado - {metadata.get('total_faces', 0)} rostros")
            else:
                faces_data = data
                self.logger.info("Formato v1.0 detectado - convirtiendo...")
            
            self.known_encodings = []
            self.face_data = []
            
            for item in faces_data:
                encoding = np.array(item['encoding'])
                self.known_encodings.append(encoding)
                self.face_data.append(item)
            
            self.logger.info(f"Cargadas {len(self.known_encodings)} codificaciones desde {file_path}")
            return True
            
        except FileNotFoundError:
            self.logger.error(f"Archivo de codificaciones no encontrado: {file_path}")
            return False
        except Exception as e:
            self.logger.error(f"Error cargando codificaciones: {e}")
            return False
    
    def _extract_face_encoding(self, image_path: str) -> Optional[np.ndarray]:
        """Extrae la codificación del rostro de una imagen."""
        if not validate_image_file(Path(image_path)):
            raise ValueError(f"Archivo de imagen inválido: {image_path}")
        
        try:
            # Cargar imagen
            image = face_recognition.load_image_file(image_path)
            
            # Detectar rostros
            face_locations = face_recognition.face_locations(image, model='hog')
            
            if not face_locations:
                self.logger.warning("No se detectaron rostros en la imagen")
                return None
            
            if len(face_locations) > 1:
                self.logger.warning(f"Se detectaron {len(face_locations)} rostros. Usando el más grande.")
                # Seleccionar el rostro más grande
                largest_face = max(face_locations, key=lambda loc: (loc[2] - loc[0]) * (loc[1] - loc[3]))
                face_locations = [largest_face]
            
            # Obtener codificación
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            if face_encodings:
                return face_encodings[0]
            else:
                self.logger.error("No se pudo generar codificación del rostro")
                return None
                
        except Exception as e:
            self.logger.error(f"Error procesando imagen {image_path}: {e}")
            return None
    
    def find_matches(self, target_image_path: str, 
                    tolerance: float = None,
                    max_results: int = 10,
                    min_confidence: float = 0.3) -> List[MatchResult]:
        """
        Busca coincidencias del rostro objetivo en el conjunto de rostros conocidos.
        
        Args:
            target_image_path: Ruta de la imagen del rostro objetivo
            tolerance: Tolerancia para la comparación (menor = más estricto)
            max_results: Número máximo de resultados a retornar
            min_confidence: Confianza mínima para considerar una coincidencia
            
        Returns:
            Lista de MatchResult ordenada por confianza
        """
        if not self.known_encodings:
            if not self.load_encodings():
                raise RuntimeError("No se pudieron cargar las codificaciones de rostros")
        
        # Extraer codificación del rostro objetivo
        target_encoding = self._extract_face_encoding(target_image_path)
        if target_encoding is None:
            raise ValueError("No se pudo procesar la imagen objetivo")
        
        tolerance = tolerance or self.config.COMPARISON_TOLERANCE
        self.logger.info(f"Buscando coincidencias con tolerancia: {tolerance}")
        
        # Calcular distancias con todos los rostros conocidos
        distances = face_recognition.face_distance(self.known_encodings, target_encoding)
        
        # Crear resultados con confianza (1 - distancia normalizada)
        results = []
        for i, (distance, face_info) in enumerate(zip(distances, self.face_data)):
            if distance <= tolerance:
                # Calcular confianza normalizada
                confidence = max(0.0, 1.0 - (distance / tolerance))
                
                if confidence >= min_confidence:
                    result = MatchResult(
                        face_id=face_info.get('id', i + 1),
                        frame=face_info['frame'],
                        timestamp=face_info.get('timestamp', 0),
                        confidence=confidence,
                        location=tuple(face_info['location']),
                        quality=face_info.get('quality', {}),
                        capture_path=face_info.get('capture_path', '')
                    )
                    results.append(result)
        
        # Ordenar por confianza (descendente)
        results.sort(key=lambda x: x.confidence, reverse=True)
        
        # Limitar resultados
        results = results[:max_results]
        
        self.logger.info(f"Encontradas {len(results)} coincidencias")
        return results
    
    def find_best_match(self, target_image_path: str, 
                       tolerance: float = None) -> Optional[MatchResult]:
        """Encuentra la mejor coincidencia para el rostro objetivo."""
        matches = self.find_matches(target_image_path, tolerance, max_results=1)
        return matches[0] if matches else None
    
    def batch_compare(self, target_images: List[str], 
                     tolerance: float = None) -> Dict[str, List[MatchResult]]:
        """
        Compara múltiples imágenes objetivo contra el conjunto de rostros conocidos.
        
        Args:
            target_images: Lista de rutas de imágenes objetivo
            tolerance: Tolerancia para la comparación
            
        Returns:
            Diccionario con resultados por imagen
        """
        results = {}
        tolerance = tolerance or self.config.COMPARISON_TOLERANCE
        
        for image_path in target_images:
            self.logger.info(f"Procesando: {image_path}")
            try:
                matches = self.find_matches(image_path, tolerance)
                results[image_path] = matches
            except Exception as e:
                self.logger.error(f"Error procesando {image_path}: {e}")
                results[image_path] = []
        
        return results
    
    def generate_match_report(self, matches: List[MatchResult], 
                            target_image_path: str) -> Dict:
        """Genera un reporte detallado de las coincidencias."""
        if not matches:
            return {
                'target_image': target_image_path,
                'total_matches': 0,
                'matches': [],
                'summary': 'No se encontraron coincidencias'
            }
        
        best_match = matches[0]
        avg_confidence = sum(m.confidence for m in matches) / len(matches)
        
        report = {
            'target_image': target_image_path,
            'total_matches': len(matches),
            'best_match': {
                'face_id': best_match.face_id,
                'frame': best_match.frame,
                'confidence': round(best_match.confidence * 100, 2),
                'timestamp': f"{best_match.timestamp:.2f}s"
            },
            'average_confidence': round(avg_confidence * 100, 2),
            'matches': [
                {
                    'face_id': m.face_id,
                    'frame': m.frame,
                    'confidence': round(m.confidence * 100, 2),
                    'timestamp': f"{m.timestamp:.2f}s",
                    'quality_score': sum(m.quality.values()) if m.quality else 0
                }
                for m in matches
            ],
            'summary': f"Se encontraron {len(matches)} coincidencias. "
                      f"La mejor coincidencia tiene {best_match.confidence * 100:.1f}% de confianza "
                      f"en el frame {best_match.frame}."
        }
        
        return report