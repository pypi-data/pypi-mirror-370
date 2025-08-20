# core_service/run_pipeline.py

from godml.config_service.loader import load_config
from godml.core_service.executors import get_executor
from godml.monitoring_service.logger import godml_logger, PipelineError, ConfigurationError

def run_pipeline(config_path="godml.yml"):
    try:
        godml_logger.info("🚀 Iniciando pipeline...")
        
        # Cargar configuración con manejo de errores
        try:
            config = load_config(config_path)
        except FileNotFoundError:
            raise ConfigurationError(f"Archivo de configuración no encontrado: {config_path}")
        except Exception as e:
            raise ConfigurationError(f"Error cargando configuración: {e}")

        # Obtener executor con manejo de errores
        try:
            executor = get_executor(config.provider)
        except ValueError as e:
            raise ConfigurationError(f"Provider no soportado: {e}")
        except Exception as e:
            raise PipelineError(f"Error obteniendo executor: {e}")

        # Validar configuración
        try:
            executor.validate(config)
        except Exception as e:
            raise PipelineError(f"Error validando configuración: {e}")

        # Ejecutar pipeline
        try:
            executor.run(config)
            godml_logger.info("✅ Pipeline completado exitosamente")
        except Exception as e:
            raise PipelineError(f"Error ejecutando pipeline: {e}")
            
    except (ConfigurationError, PipelineError):
        raise
    except Exception as e:
        raise PipelineError(f"Error inesperado en pipeline: {e}")

