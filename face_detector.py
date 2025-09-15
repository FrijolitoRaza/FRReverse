import face_recognition
import cv2
import json
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import hashlib

from config import Config
from utils import setup_logger, validate_video_file, calculate_file_hash


class FaceDetector:
    """Clase optimizada para detección y extracción de rostros desde videos."""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.config.create_directories()
        self.logger = setup_logger('face_detector', self.config.LOG_FILE)
        self.unique_encodings = []
        self.processed_hashes = set()
        
    def _resize_frame_if_needed(self, frame: np.ndarray, max_width: int = 1280) -> np.ndarray:
        """Redimensiona el frame si es muy grande para optimizar el procesamiento."""
        height, width = frame.shape[:2]
        if width > max_width:
            scale = max_width / width
            new_width = max_width
            new_height = int(height * scale)
            return cv2.resize(frame, (new_width, new_height))
        return frame
    
    def _extract_face_features(self, frame: np.ndarray, face_location: Tuple[int, int, int, int]) -> Optional[Dict]:
        """Extrae características del rostro y valida su calidad."""
        top, right, bottom, left = face_location
        width = right - left
        height = bottom - top
        
        # Validar tamaño mínimo
        if width < self.config.MIN_FACE_SIZE or height < self.config.MIN_FACE_SIZE:
            return None
        
        # Extraer región del rostro
        face_region = frame[top:bottom, left:right]
        
        # Calcular calidad básica (contraste y nitidez)
        gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        contrast = gray_face.std()
        laplacian_var = cv2.Laplacian(gray_face, cv2.CV_64F).var()
        
        # Filtrar rostros de baja calidad
        if contrast < 20 or laplacian_var < 50:
            return None
        
        return {
            'location': face_location,
            'size': (width, height),
            'quality': {
                'contrast': float(contrast),
                'sharpness': float(laplacian_var)
            }
        }
    
    def _is_unique_face(self, face_encoding: np.ndarray) -> bool:
        """Verifica si el rostro es único comparándolo con los ya almacenados."""
        if not self.unique_encodings:
            return True
        
        existing_encodings = [item['encoding_np'] for item in self.unique_encodings]
        matches = face_recognition.compare_faces(
            existing_encodings, 
            face_encoding, 
            tolerance=self.config.UNIQUENESS_TOLERANCE
        )
        return True not in matches
    
    def _save_face_capture(self, frame: np.ndarray, face_info: Dict, frame_number: int) -> str:
        """Guarda la captura del rostro con nombre descriptivo."""
        top, right, bottom, left = face_info['location']
        face_region = frame[top:bottom, left:right]
        
        # Generar nombre único basado en características
        quality_score = int(face_info['quality']['contrast'] + face_info['quality']['sharpness'])
        filename = f"face_f{frame_number:06d}_q{quality_score}_s{face_info['size'][0]}x{face_info['size'][1]}.jpg"
        filepath = self.config.OUTPUT_FOLDER / filename
        
        # Guardar con mayor calidad
        cv2.imwrite(str(filepath), face_region, [cv2.IMWRITE_JPEG_QUALITY, 95])
        return str(filepath)
    
    def process_video(self, video_path: str, progress_callback=None) -> Dict:
        """
        Procesa un video completo extrayendo rostros únicos.
        
        Args:
            video_path: Ruta del archivo de video
            progress_callback: Función opcional para reportar progreso
            
        Returns:
            Diccionario con estadísticas del procesamiento
        """
        video_path = Path(video_path)
        
        # Validaciones iniciales
        if not validate_video_file(video_path):
            raise ValueError(f"Archivo de video inválido: {video_path}")
        
        self.logger.info(f"Iniciando análisis del video: {video_path}")
        
        video_capture = cv2.VideoCapture(str(video_path))
        if not video_capture.isOpened():
            raise RuntimeError(f"No se pudo abrir el video: {video_path}")
        
        # Obtener información del video
        total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        self.logger.info(f"Video cargado - Frames: {total_frames}, FPS: {fps:.2f}, Duración: {duration:.2f}s")
        
        # Estadísticas
        stats = {
            'total_frames': total_frames,
            'processed_frames': 0,
            'faces_detected': 0,
            'unique_faces': 0,
            'captures_saved': 0,
            'processing_time': 0
        }
        
        frame_count = 0
        
        # Barra de progreso
        pbar = tqdm(total=total_frames // self.config.FRAME_INTERVAL, 
                   desc="Procesando frames", unit="frame")
        
        try:
            import time
            start_time = time.time()
            
            while True:
                ret, frame = video_capture.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Procesar solo frames según el intervalo configurado
                if frame_count % self.config.FRAME_INTERVAL == 0:
                    stats['processed_frames'] += 1
                    
                    # Redimensionar frame si es necesario
                    frame = self._resize_frame_if_needed(frame)
                    
                    # Convertir a RGB para face_recognition
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Detectar ubicaciones de rostros
                    face_locations = face_recognition.face_locations(
                        rgb_frame, model='cnn' if cv2.cuda.getCudaEnabledDeviceCount() > 0 else 'hog'
                    )
                    
                    if face_locations:
                        stats['faces_detected'] += len(face_locations)
                        
                        # Obtener codificaciones de rostros
                        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                        
                        for face_location, face_encoding in zip(face_locations, face_encodings):
                            # Extraer y validar características del rostro
                            face_info = self._extract_face_features(frame, face_location)
                            if not face_info:
                                continue
                            
                            # Verificar si es un rostro único
                            if self._is_unique_face(face_encoding):
                                # Guardar captura
                                capture_path = self._save_face_capture(frame, face_info, frame_count)
                                stats['captures_saved'] += 1
                                
                                # Almacenar codificación
                                face_data = {
                                    'id': len(self.unique_encodings) + 1,
                                    'frame': frame_count,
                                    'timestamp': frame_count / fps,
                                    'location': face_info['location'],
                                    'size': face_info['size'],
                                    'quality': face_info['quality'],
                                    'capture_path': capture_path,
                                    'encoding': face_encoding.tolist(),
                                    'encoding_np': face_encoding
                                }
                                
                                self.unique_encodings.append(face_data)
                                stats['unique_faces'] += 1
                    
                    pbar.update(1)
                    
                    # Callback de progreso
                    if progress_callback:
                        progress = frame_count / total_frames
                        progress_callback(progress, stats)
            
            stats['processing_time'] = time.time() - start_time
            
        finally:
            video_capture.release()
            pbar.close()
        
        # Guardar resultados
        self._save_encodings()
        
        self.logger.info(f"Análisis completado - {stats['unique_faces']} rostros únicos encontrados")
        return stats
    
    def _save_encodings(self):
        """Guarda las codificaciones en archivo JSON."""
        # Remover arrays numpy para serialización JSON
        encodings_for_json = []
        for item in self.unique_encodings:
            json_item = item.copy()
            json_item.pop('encoding_np', None)
            encodings_for_json.append(json_item)
        
        encodings_file = Path(self.config.ENCODINGS_FILE)
        with open(encodings_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'total_faces': len(encodings_for_json),
                    'version': '2.0',
                    'config': {
                        'min_face_size': self.config.MIN_FACE_SIZE,
                        'frame_interval': self.config.FRAME_INTERVAL,
                        'uniqueness_tolerance': self.config.UNIQUENESS_TOLERANCE
                    }
                },
                'faces': encodings_for_json
            }, f, indent=2)
        
        self.logger.info(f"Codificaciones guardadas en: {encodings_file}")
    
    def load_encodings(self, encodings_file: str = None) -> bool:
        """Carga codificaciones desde archivo JSON."""
        file_path = Path(encodings_file or self.config.ENCODINGS_FILE)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Compatibilidad con formato anterior
            if 'faces' in data:
                faces_data = data['faces']
            else:
                faces_data = data
            
            self.unique_encodings = []
            for item in faces_data:
                item['encoding_np'] = np.array(item['encoding'])
                self.unique_encodings.append(item)
            
            self.logger.info(f"Cargadas {len(self.unique_encodings)} codificaciones desde {file_path}")
            return True
            
        except FileNotFoundError:
            self.logger.warning(f"Archivo de codificaciones no encontrado: {file_path}")
            return False
        except Exception as e:
            self.logger.error(f"Error cargando codificaciones: {e}")
            return False