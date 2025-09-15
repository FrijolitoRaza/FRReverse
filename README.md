# Face Recognition Video Analyzer 🎭

Un sistema avanzado de análisis de rostros en videos que permite extraer rostros únicos de videos y posteriormente buscar personas específicas mediante comparación de imágenes.

## 🚀 Características

- **Análisis de video optimizado**: Extrae rostros únicos de videos con filtrado inteligente
- **Detección de calidad**: Filtra rostros borrosos o de baja calidad automáticamente
- **Búsqueda eficiente**: Encuentra personas específicas con algoritmos de comparación facial avanzados
- **Procesamiento en lote**: Analiza múltiples imágenes objetivo simultáneamente
- **Configuración flexible**: Parámetros ajustables via variables de entorno
- **Informes detallados**: Genera reportes JSON con estadísticas y resultados
- **Interfaz CLI intuitiva**: Comandos simples para todas las operaciones
- **Logging completo**: Registro detallado de todas las operaciones

## 📋 Requisitos del sistema

- **Python 3.8+**
- **OpenCV** con soporte para formatos de video comunes
- **4GB+ RAM** recomendado para videos largos
- **Espacio en disco**: Variable según el tamaño del video y número de rostros

### Dependencias principales

- `face_recognition` - Reconocimiento facial basado en dlib
- `opencv-python` - Procesamiento de video e imágenes
- `numpy` - Operaciones numéricas optimizadas
- `Pillow` - Manipulación de imágenes
- `tqdm` - Barras de progreso
- `python-dotenv` - Gestión de variables de entorno

## 🛠️ Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/face-recognition-analyzer.git
cd face-recognition-analyzer
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En macOS/Linux
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar archivo de configuración de ejemplo
cp .env.example .env

# Editar según tus necesidades
nano .env  # o el editor de tu preferencia
```

## ⚙️ Configuración

El sistema utiliza variables de entorno para la configuración. Las principales opciones son:

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `MIN_FACE_SIZE` | 150 | Tamaño mínimo del rostro en píxeles |
| `FRAME_INTERVAL` | 10 | Procesar cada N frames |
| `UNIQUENESS_TOLERANCE` | 0.5 | Tolerancia para considerar rostros únicos |
| `COMPARISON_TOLERANCE` | 0.6 | Tolerancia para comparaciones de búsqueda |
| `OUTPUT_FOLDER` | face_captures | Carpeta para capturas de rostros |
| `MAX_WORKERS` | 4 | Número de hilos para procesamiento |

## 🎯 Uso

### Análisis de video

Extrae todos los rostros únicos de un video:

```bash
python main.py analyze mi_video.mp4
```

**Salida esperada:**
- Carpeta `face_captures/` con imágenes de rostros únicos
- Archivo `face_encodings.json` con codificaciones faciales
- Log detallado del proceso

### Búsqueda de persona

Busca una persona específica en los rostros extraídos:

```bash
python main.py search persona_objetivo.jpg

# Con parámetros personalizados
python main.py search persona.jpg --tolerance 0.5 --max-results 5
```

### Búsqueda en lote

Procesa múltiples imágenes objetivo:

```bash
python main.py batch-search ./imagenes_objetivo/
```

### Información del sistema

Muestra configuración y estado actual:

```bash
python main.py info
```

## 📁 Estructura del proyecto

```
face-recognition-analyzer/
├── main.py                 # Interfaz CLI principal
├── config.py               # Configuración centralizada
├── face_detector.py        # Detector de rostros optimizado
├── face_matcher.py         # Sistema de comparación
├── utils.py                # Utilidades comunes
├── requirements.txt        # Dependencias Python
├── .env.example           # Variables de entorno ejemplo
├── .gitignore             # Archivos ignorados por Git
├── README.md              # Este archivo
└── tests/                 # Tests unitarios (opcional)
    ├── test_detector.py
    ├── test_matcher.py
    └── test_utils.py
```

### Directorios generados

```
face_captures/             # Capturas de rostros únicos
logs/                      # Archivos de log
temp/                      # Archivos temporales
face_encodings.json        # Base de datos de codificaciones
*_report.json             # Reportes de búsqueda
```

## 🔧 Configuración avanzada

### Optimización de rendimiento

Para videos grandes o procesamiento intensivo:

```bash
# .env
MAX_WORKERS=8              # Más hilos si tienes CPU potente
FRAME_INTERVAL=5           # Procesar más frames (más preciso)
MAX_VIDEO_WIDTH=1920       # Resolución máxima
ENABLE_MEMORY_OPTIMIZATION=true
```

### Ajuste de precisión

Para mejorar la precisión de detección:

```bash
MIN_FACE_SIZE=200          # Rostros más grandes
UNIQUENESS_TOLERANCE=0.4   # Más estricto para unicidad
COMPARISON_TOLERANCE=0.5   # Más estricto para búsquedas
MIN_CONTRAST=30            # Mayor calidad mínima
MIN_SHARPNESS=75
```

### GPU acceleration (opcional)

Si tienes CUDA instalado:

```bash
# Instalar versión GPU de dlib
pip uninstall dlib
pip install dlib-gpu

# En .env
USE_GPU=true
```

## 📊 Formatos soportados

### Videos
- `.mp4`, `.avi`, `.mov`, `.mkv`, `.wmv`

### Imágenes
- `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`

## 🐛 Solución de problemas

### Error: "No module named 'face_recognition'"

```bash
# Reinstalar con dependencias del sistema
pip install cmake
pip install dlib
pip install face_recognition
```

### Error: "Could not load image file"

- Verificar que el archivo existe y tiene permisos de lectura
- Confirmar que el formato es soportado
- Comprobar que la imagen no está corrupta

### Rendimiento lento

1. **Reducir resolución**: Ajustar `MAX_VIDEO_WIDTH`
2. **Aumentar intervalo**: Subir `FRAME_INTERVAL`
3. **Optimizar hardware**: Usar SSD, más RAM
4. **GPU**: Instalar versión CUDA si está disponible

### Memoria insuficiente

```bash
# En .env
ENABLE_MEMORY_OPTIMIZATION=true
MAX_MEMORY_MB=1024
BATCH_SIZE=50
```

## 🧪 Testing

```bash
# Instalar dependencias de desarrollo
pip install pytest pytest-cov

# Ejecutar tests
pytest tests/

# Con cobertura
pytest --cov=. tests/
```

## 📈 Optimización y mejores prácticas

### Para videos largos (>30 min)
- Usar `FRAME_INTERVAL=15` o mayor
- Activar `ENABLE_MEMORY_OPTIMIZATION=true`
- Procesar en segmentos si es necesario

### Para alta precisión
- `MIN_FACE_SIZE=200+`
- `UNIQUENESS_TOLERANCE=0.3`
- `COMPARISON_TOLERANCE=0.4`

### Para procesamiento rápido
- `FRAME_INTERVAL=20`
- `MAX_VIDEO_WIDTH=720`
- `MIN_FACE_SIZE=100`

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para nueva característica (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

### Estilo de código

```bash
# Formatear código
black *.py

# Verificar estilo
flake8 *.py

# Type checking
mypy *.py
```

## 📝 Changelog

### v2.0.0 (Actual)
- ✅ Sistema de configuración con variables de entorno
- ✅ Interfaz CLI mejorada con subcomandos
- ✅ Detector de calidad de rostros
- ✅ Sistema de logging completo
- ✅ Búsqueda en lote
- ✅ Reportes JSON detallados
- ✅ Optimizaciones de rendimiento
- ✅ Documentación completa

### v1.0.0 (Original)
- ✅ Detección básica de rostros en video
- ✅ Comparación simple de rostros
- ✅ Scripts independientes

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- [face_recognition](https://github.com/ageitgey/face_recognition) por la librería de reconocimiento facial
- [OpenCV](https://opencv.org/) por las herramientas de procesamiento de video
- [dlib](http://dlib.net/) por los algoritmos de machine learning

## 📞 Soporte

Si encuentras algún problema o tienes preguntas:

1. Revisar la [documentación](#-configuración)
2. Buscar en [Issues](https://github.com/tu-usuario/face-recognition-analyzer/issues)
3. Crear nuevo Issue con:
   - Descripción detallada del problema
   - Pasos para reproducir
   - Información del sistema
   - Logs relevantes

---

**¿Te gustó el proyecto? ¡Dale una ⭐ en GitHub!**