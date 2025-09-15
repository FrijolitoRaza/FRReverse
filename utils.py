import logging
import hashlib
from pathlib import Path
from typing import Optional
import cv2
from PIL import Image

from config import Config


def setup_logger(name: str, log_file: Path, level=logging.INFO) -> logging.Logger:
    """Configura un logger con archivo y consola."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    log_file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def calculate_file_hash(file_path: Path, chunk_size: int = 8192) -> str:
    """Calcula el hash MD5 de un archivo."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        raise RuntimeError(f"Error calculando hash del archivo {file_path}: {e}")


def validate_video_file(video_path: Path, config: Config = None) -> bool:
    """Valida que el archivo de video sea accesible y tenga formato válido."""
    config = config or Config()
    
    if not video_path.exists():
        return False
    
    if not config.validate_file_format(video_path, 'video'):
        return False
    
    # Verificar que OpenCV pueda abrir el archivo
    try:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return False
        
        # Verificar que tenga al menos un frame
        ret, _ = cap.read()
        cap.release()
        return ret
    except Exception:
        return False


def validate_image_file(image_path: Path, config: Config = None) -> bool:
    """Valida que el archivo de imagen sea accesible y tenga formato válido."""
    config = config or Config()
    
    if not image_path.exists():
        return False
    
    if not config.validate_file_format(image_path, 'image'):
        return False
    
    # Verificar que se pueda abrir la imagen
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True
    except Exception:
        return False


def format_time(seconds: float) -> str:
    """Formatea segundos a formato HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def format_file_size(size_bytes: int) -> str:
    """Formatea el tamaño de archivo en formato legible."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def create_thumbnail(image_path: Path, output_path: Path, size: tuple = (150, 150)) -> bool:
    """Crea una miniatura de la imagen."""
    try:
        with Image.open(image_path) as img:
            # Mantener proporción
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(output_path, quality=85, optimize=True)
        return True
    except Exception:
        return False


class ProgressReporter:
    """Clase para reportar progreso de operaciones largas."""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.description = description
        self.current = 0
        self.logger = logging.getLogger('progress')
    
    def update(self, increment: int = 1):
        """Actualiza el progreso."""
        self.current += increment
        percentage = (self.current / self.total) * 100
        self.logger.info(f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%)")
    
    def finish(self):
        """Marca como completado."""
        self.logger.info(f"{self.description}: Completado!")


def safe_filename(filename: str) -> str:
    """Convierte un string en un nombre de archivo seguro."""
    import re
    # Remover caracteres no válidos
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limitar longitud
    return safe_name[:100] if len(safe_name) > 100 else safe_name