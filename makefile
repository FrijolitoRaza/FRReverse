# Face Recognition Video Analyzer - Makefile
# Automatización de tareas comunes de desarrollo

.PHONY: help install install-dev test lint format clean setup run-example docs

# Variables
PYTHON := python
PIP := pip
VENV := venv
ACTIVATE := $(VENV)/bin/activate
REQUIREMENTS := requirements.txt

# Default target
help: ## Mostrar ayuda
	@echo "Face Recognition Video Analyzer - Comandos disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

install: ## Instalar dependencias básicas
	$(PIP) install -r $(REQUIREMENTS)

install-dev: install ## Instalar dependencias de desarrollo
	$(PIP) install pytest pytest-cov black flake8 mypy
	$(PIP) install -e .

setup: ## Configurar entorno completo
	@echo "🔧 Configurando entorno de desarrollo..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "📦 Creando entorno virtual..."; \
		$(PYTHON) -m venv $(VENV); \
	fi
	@echo "📚 Instalando dependencias..."
	@. $(ACTIVATE) && $(MAKE) install-dev
	@if [ ! -f ".env" ]; then \
		echo "⚙️ Creando archivo de configuración..."; \
		cp .env.example .env; \
	fi
	@echo "✅ Entorno configurado correctamente!"
	@echo "💡 Activa el entorno con: source $(ACTIVATE)"

test: ## Ejecutar tests
	$(PYTHON) -m pytest tests/ -v

test-coverage: ## Ejecutar tests con cobertura
	$(PYTHON) -m pytest tests/ --cov=. --cov-report=html --cov-report=term

lint: ## Verificar estilo de código
	$(PYTHON) -m flake8 *.py --max-line-length=100
	$(PYTHON) -m mypy *.py --ignore-missing-imports

format: ## Formatear código
	$(PYTHON) -m black *.py --line-length=100

clean: ## Limpiar archivos temporales
	@echo "🧹 Limpiando archivos temporales..."
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf face_captures/
	rm -rf logs/
	rm -rf temp/
	rm -f face_encodings.json
	rm -f *_report.json
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	@echo "✅ Limpieza completada"

clean-all: clean ## Limpiar todo incluyendo entorno virtual
	rm -rf $(VENV)/
	rm -f .env

# Ejemplos de uso
run-example: ## Ejecutar ejemplo básico
	@echo "🎬 Ejecutando ejemplo de análisis..."
	@if [ ! -f "example_video.mp4" ]; then \
		echo "❌ No se encontró example_video.mp4"; \
		echo "💡 Coloca un video de ejemplo con ese nombre"; \
		exit 1; \
	fi
	$(PYTHON) main.py analyze example_video.mp4

demo: ## Demostración completa del sistema
	@echo "🎭 Iniciando demostración del sistema..."
	@echo "1️⃣ Mostrando información del sistema:"
	$(PYTHON) main.py info
	@echo ""
	@echo "2️⃣ Para continuar, necesitas:"
	@echo "   - Un archivo de video: example_video.mp4"
	@echo "   - Una imagen objetivo: target_person.jpg"
	@echo ""
	@echo "3️⃣ Ejecuta manualmente:"
	@echo "   make analyze-demo    # Analizar video"
	@echo "   make search-demo     # Buscar persona"

analyze-demo: ## Demo de análisis de video
	@if [ ! -f "example_video.mp4" ]; then \
		echo "❌ Coloca un video llamado 'example_video.mp4'"; \
		exit 1; \
	fi
	$(PYTHON) main.py analyze example_video.mp4

search-demo: ## Demo de búsqueda de persona
	@if [ ! -f "target_person.jpg" ]; then \
		echo "❌ Coloca una imagen llamada 'target_person.jpg'"; \
		exit 1; \
	fi
	$(PYTHON) main.py search target_person.jpg

# Desarrollo y mantenimiento
check: lint test ## Verificar código (lint + tests)

pre-commit: format lint test ## Ejecutar antes de commit
	@echo "✅ Código listo para commit"

build: clean ## Construir paquete para distribución
	$(PYTHON) setup.py sdist bdist_wheel

release: build ## Preparar release (requiere configuración adicional)
	@echo "📦 Paquete construido en dist/"
	@echo "💡 Para publicar: twine upload dist/*"

# Documentación
docs: ## Generar documentación (requiere sphinx)
	@if [ ! -d "docs" ]; then \
		mkdir docs; \
		sphinx-quickstart docs --no-sep --project="Face Recognition Analyzer" \
		--author="Tu Nombre" --release="2.0" --language="es" --makefile --batchfile; \
	fi
	@cd docs && make html
	@echo "📚 Documentación generada en docs/_build/html/"

# Utilidades de desarrollo
install-hooks: ## Instalar git hooks para desarrollo
	@echo "#!/bin/sh" > .git/hooks/pre-commit
	@echo "make pre-commit" >> .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "✅ Git hooks instalados"

profile: ## Perfilar rendimiento (requiere archivo de prueba)
	@if [ ! -f "profile_video.mp4" ]; then \
		echo "❌ Coloca un video llamado 'profile_video.mp4'"; \
		exit 1; \
	fi
	$(PYTHON) -m cProfile -o profile.stats main.py analyze profile_video.mp4
	$(PYTHON) -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"

benchmark: ## Ejecutar benchmarks básicos
	@echo "⏱️ Ejecutando benchmarks..."
	@$(PYTHON) -c "
import time
from face_detector import FaceDetector
from config import Config
print('Tiempo de inicialización:')
start = time.time()
detector = FaceDetector()
print(f'  FaceDetector: {time.time() - start:.3f}s')
"

# Información del sistema
system-info: ## Mostrar información del sistema
	@echo "🖥️ Información del sistema:"
	@echo "  Python: $$($(PYTHON) --version)"
	@echo "  Pip: $$($(PIP) --version | cut -d' ' -f1-2)"
	@echo "  Sistema: $$(uname -s)"
	@echo "  Arquitectura: $$(uname -m)"
	@echo ""
	@echo "📦 Dependencias instaladas:"
	@$(PIP) list | grep -E "(opencv|face-recognition|numpy|PIL)"
	@echo ""
	@echo "💾 Espacio en disco:"
	@df -h . | tail -1

# Instalación específica por SO
install-ubuntu: ## Instalar dependencias en Ubuntu
	sudo apt-get update
	sudo apt-get install -y python3-dev python3-pip cmake
	sudo apt-get install -y libopencv-dev python3-opencv
	$(MAKE) install-dev

install-macos: ## Instalar dependencias en macOS
	brew install cmake
	brew install opencv
	$(MAKE) install-dev

install-windows: ## Instalar dependencias en Windows (requiere chocolatey)
	choco install cmake
	$(MAKE) install-dev