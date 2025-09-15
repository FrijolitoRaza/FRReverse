import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración centralizada para el proyecto de reconocimiento facial."""
    
    # Configuración de video
    MIN_FACE_SIZE = int(os.getenv('MIN_FACE_SIZE', 150))
    FRAME_INTERVAL = int(os.getenv('FRAME_INTERVAL', 10))
    UNIQUENESS_TOLERANCE = float(os.getenv('UNIQUENESS_TOLERANCE', 0.5))
    COMPARISON_TOLERANCE = float(os.getenv('COMPARISON_TOLERANCE', 0.6))
    
    # Directorios
    OUTPUT_FOLDER = Path(os.getenv('OUTPUT_FOLDER', 'face_captures'))
    TEMP_FOLDER = Path(os.getenv('TEMP_FOLDER', 'temp'))
    LOGS_FOLDER = Path(os.getenv('LOGS_FOLDER', 'logs'))
    
    # Archivos
    ENCODINGS_FILE = os.getenv('ENCODINGS_FILE', 'face_encodings.json')
    LOG_FILE = LOGS_FOLDER / 'face_detection.log'
    
    # Configuración de procesamiento
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 4))
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 100))
    
    # Formatos de imagen soportados
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    SUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.wmv'}
    
    @classmethod
    def create_directories(cls):
        """Crea los directorios necesarios si no existen."""
        for folder in [cls.OUTPUT_FOLDER, cls.TEMP_FOLDER, cls.LOGS_FOLDER]:
            folder.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_file_format(cls, file_path: Path, file_type: str = 'image'):
        """Valida el formato de archivo."""
        suffix = file_path.suffix.lower()
        if file_type == 'image':
            return suffix in cls.SUPPORTED_IMAGE_FORMATS
        elif file_type == 'video':
            return suffix in cls.SUPPORTED_VIDEO_FORMATS
        return False