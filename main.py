#!/usr/bin/env python3
"""
Face Recognition Video Analyzer
Sistema de análisis de rostros en videos y comparación con imágenes objetivo.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

from config import Config
from face_detector import FaceDetector
from face_matcher import FaceMatcher
from utils import setup_logger, format_time, format_file_size


def analyze_video(video_path: str, config: Config) -> bool:
    """Analiza un video y extrae rostros únicos."""
    print(f"🎬 Analizando video: {video_path}")
    
    detector = FaceDetector(config)
    
    def progress_callback(progress, stats):
        print(f"  Progreso: {progress*100:.1f}% - "
              f"Rostros únicos: {stats['unique_faces']}")
    
    try:
        stats = detector.process_video(video_path, progress_callback)
        
        print("\n✅ Análisis completado!")
        print(f"  📊 Estadísticas:")
        print(f"    - Frames procesados: {stats['processed_frames']:,}")
        print(f"    - Rostros detectados: {stats['faces_detected']:,}")
        print(f"    - Rostros únicos: {stats['unique_faces']:,}")
        print(f"    - Capturas guardadas: {stats['captures_saved']:,}")
        print(f"    - Tiempo de procesamiento: {format_time(stats['processing_time'])}")
        print(f"  📁 Resultados guardados en:")
        print(f"    - Capturas: {config.OUTPUT_FOLDER}")
        print(f"    - Codificaciones: {config.ENCODINGS_FILE}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        return False


def find_person(target_image: str, config: Config, 
               tolerance: float = None, max_results: int = 10) -> bool:
    """Busca una persona en el conjunto de rostros extraídos."""
    print(f"🔍 Buscando coincidencias para: {target_image}")
    
    matcher = FaceMatcher(config)
    
    try:
        matches = matcher.find_matches(
            target_image, 
            tolerance=tolerance, 
            max_results=max_results
        )
        
        if not matches:
            print("😞 No se encontraron coincidencias")
            return True
        
        print(f"\n🎯 Encontradas {len(matches)} coincidencias:")
        
        for i, match in enumerate(matches, 1):
            confidence_pct = match.confidence * 100
            print(f"\n  {i}. Coincidencia #{match.face_id}")
            print(f"     🎬 Frame: {match.frame} (tiempo: {match.timestamp:.2f}s)")
            print(f"     📊 Confianza: {confidence_pct:.1f}%")
            print(f"     📷 Captura: {match.capture_path}")
            
            if match.quality:
                quality_score = sum(match.quality.values())
                print(f"     ⭐ Calidad: {quality_score:.1f}")
        
        # Generar reporte detallado
        report = matcher.generate_match_report(matches, target_image)
        report_file = Path("match_report.json")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Reporte detallado guardado en: {report_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la búsqueda: {e}")
        return False


def batch_search(target_folder: str, config: Config, tolerance: float = None) -> bool:
    """Busca múltiples personas en lote."""
    target_path = Path(target_folder)
    if not target_path.exists() or not target_path.is_dir():
        print(f"❌ Carpeta no válida: {target_folder}")
        return False
    
    # Buscar imágenes en la carpeta
    image_files = []
    for ext in config.SUPPORTED_IMAGE_FORMATS:
        image_files.extend(target_path.glob(f"*{ext}"))
        image_files.extend(target_path.glob(f"*{ext.upper()}"))
    
    if not image_files:
        print(f"❌ No se encontraron imágenes en: {target_folder}")
        return False
    
    print(f"🔍 Búsqueda en lote - {len(image_files)} imágenes")
    
    matcher = FaceMatcher(config)
    
    try:
        results = matcher.batch_compare([str(img) for img in image_files], tolerance)
        
        total_matches = sum(len(matches) for matches in results.values())
        print(f"\n📊 Resultados de búsqueda en lote:")
        print(f"  - Imágenes procesadas: {len(image_files)}")
        print(f"  - Total de coincidencias: {total_matches}")
        
        # Guardar resultados detallados
        batch_report = {
            'summary': {
                'images_processed': len(image_files),
                'total_matches': total_matches,
                'tolerance_used': tolerance or config.COMPARISON_TOLERANCE
            },
            'results': {}
        }
        
        for image_path, matches in results.items():
            image_name = Path(image_path).name
            if matches:
                print(f"\n  🎯 {image_name}: {len(matches)} coincidencias")
                best_match = matches[0]
                print(f"    Mejor: Frame {best_match.frame} ({best_match.confidence*100:.1f}%)")
            else:
                print(f"\n  😞 {image_name}: Sin coincidencias")
            
            batch_report['results'][image_name] = [
                {
                    'face_id': m.face_id,
                    'frame': m.frame,
                    'confidence': round(m.confidence * 100, 2),
                    'timestamp': m.timestamp
                } for m in matches
            ]
        
        # Guardar reporte
        report_file = Path("batch_search_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(batch_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Reporte de búsqueda en lote guardado en: {report_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la búsqueda en lote: {e}")
        return False


def show_info(config: Config) -> None:
    """Muestra información del sistema y configuración."""
    print("📋 Información del sistema:")
    print(f"  🔧 Configuración:")
    print(f"    - Tamaño mínimo de rostro: {config.MIN_FACE_SIZE}px")
    print(f"    - Intervalo de frames: {config.FRAME_INTERVAL}")
    print(f"    - Tolerancia de unicidad: {config.UNIQUENESS_TOLERANCE}")
    print(f"    - Tolerancia de comparación: {config.COMPARISON_TOLERANCE}")
    
    print(f"  📁 Directorios:")
    print(f"    - Capturas: {config.OUTPUT_FOLDER}")
    print(f"    - Logs: {config.LOGS_FOLDER}")
    print(f"    - Temporal: {config.TEMP_FOLDER}")
    
    # Verificar si existen archivos de codificaciones
    encodings_file = Path(config.ENCODINGS_FILE)
    if encodings_file.exists():
        try:
            with open(encodings_file, 'r') as f:
                data = json.load(f)
            
            if 'faces' in data:
                face_count = len(data['faces'])
                metadata = data.get('metadata', {})
                print(f"\n  💾 Base de datos de rostros:")
                print(f"    - Archivo: {encodings_file}")
                print(f"    - Rostros almacenados: {face_count}")
                print(f"    - Versión: {metadata.get('version', 'v1.0')}")
                print(f"    - Tamaño: {format_file_size(encodings_file.stat().st_size)}")
            else:
                face_count = len(data)
                print(f"\n  💾 Base de datos de rostros (formato v1.0):")
                print(f"    - Archivo: {encodings_file}")
                print(f"    - Rostros almacenados: {face_count}")
                print(f"    - Tamaño: {format_file_size(encodings_file.stat().st_size)}")
        except Exception as e:
            print(f"  ⚠️  Error leyendo base de datos: {e}")
    else:
        print(f"\n  💾 Base de datos de rostros: No encontrada")
        print(f"    Ejecuta el análisis de video primero")


def main():
    """Función principal del CLI."""
    parser = argparse.ArgumentParser(
        description="Face Recognition Video Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  
  # Analizar un video
  python main.py analyze video.mp4
  
  # Buscar una persona
  python main.py search person.jpg
  
  # Búsqueda en lote
  python main.py batch-search ./target_images/
  
  # Mostrar información del sistema
  python main.py info
        """
    )
    
    parser.add_argument('--version', action='version', version='Face Analyzer v2.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando: analyze
    analyze_parser = subparsers.add_parser('analyze', help='Analizar video y extraer rostros')
    analyze_parser.add_argument('video', help='Ruta del archivo de video')
    
    # Comando: search
    search_parser = subparsers.add_parser('search', help='Buscar persona en rostros extraídos')
    search_parser.add_argument('image', help='Ruta de la imagen objetivo')
    search_parser.add_argument('--tolerance', type=float, help='Tolerancia de comparación (0.0-1.0)')
    search_parser.add_argument('--max-results', type=int, default=10, help='Máximo número de resultados')
    
    # Comando: batch-search
    batch_parser = subparsers.add_parser('batch-search', help='Búsqueda en lote')
    batch_parser.add_argument('folder', help='Carpeta con imágenes objetivo')
    batch_parser.add_argument('--tolerance', type=float, help='Tolerancia de comparación (0.0-1.0)')
    
    # Comando: info
    subparsers.add_parser('info', help='Mostrar información del sistema')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Cargar configuración
    config = Config()
    config.create_directories()
    
    # Configurar logger principal
    logger = setup_logger('main', config.LOG_FILE)
    logger.info(f"Ejecutando comando: {args.command}")
    
    try:
        if args.command == 'analyze':
            success = analyze_video(args.video, config)
            return 0 if success else 1
            
        elif args.command == 'search':
            success = find_person(args.image, config, args.tolerance, args.max_results)
            return 0 if success else 1
            
        elif args.command == 'batch-search':
            success = batch_search(args.folder, config, args.tolerance)
            return 0 if success else 1
            
        elif args.command == 'info':
            show_info(config)
            return 0
            
    except KeyboardInterrupt:
        print("\n⏸️  Operación cancelada por el usuario")
        return 130
    except Exception as e:
        logger.error(f"Error no manejado: {e}", exc_info=True)
        print(f"💥 Error inesperado: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())