# Face Recognition Video Analyzer - Dockerfile
FROM python:3.10-slim-bullseye

# Metadatos
LABEL maintainer="tu-email@ejemplo.com" \
      description="Face Recognition Video Analyzer" \
      version="2.0.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    # Herramientas básicas
    wget \
    curl \
    git \
    build-essential \
    # OpenCV dependencies
    libopencv-dev \
    python3-opencv \
    # dlib dependencies
    cmake \
    libboost-all-dev \
    libgtk-3-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    gfortran \
    # Utilidades adicionales
    htop \
    vim \
    nano \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear usuario no-root para seguridad
RUN useradd -m -u 1001 -s /bin/bash appuser

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requirements primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p face_captures logs temp && \
    chown -R appuser:appuser /app

# Copiar archivo de configuración si no existe
RUN if [ ! -f .env ]; then cp .env.example .env; fi

# Cambiar a usuario no-root
USER appuser

# Exponer puerto (si en el futuro se añade web interface)
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import face_recognition, cv2; print('OK')" || exit 1

# Comando por defecto
CMD ["python", "main.py", "info"]

# Puntos de montaje recomendados
VOLUME ["/app/face_captures", "/app/logs", "/app/videos", "/app/target_images"]