# Copyright (c) 2024 Arturo Gutierrez Rubio Rojas
# Licensed under the MIT License

import os
import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split
from godml import notebook_api as nb
from godml.core_service.engine import BaseExecutor
from godml.config_service.schema import PipelineDefinition
from godml.model_service.model_loader import load_custom_model_class
from godml.monitoring_service.logger import get_logger
from godml.utils.path_utils import normalize_path
from godml.utils.predict_safely import predict_safely
from godml.utils.log_model_generic import log_model_generic
from godml.monitoring_service.metrics import evaluate_binary_classification
from godml.config_service.schema  import ModelResult
import mlflow.models.signature

logger = get_logger()


class MLflowExecutor(BaseExecutor):
    def __init__(self, tracking_uri: str = None):
        if tracking_uri:
            if tracking_uri.startswith("file:/"):
                local_path = tracking_uri.replace("file:/", "", 1)
                normalized = normalize_path(local_path)
                tracking_uri = f"file://{normalized}"
            mlflow.set_tracking_uri(tracking_uri)
        else:
            mlflow.set_tracking_uri("file:./mlruns")

        mlflow.set_experiment("godml-experiment")

    def preprocess_for_xgboost(self, df, target_col="target"):
        if target_col not in df.columns:
            raise ValueError("El dataset debe contener una columna llamada 'target'.")
        if df[target_col].dtype == object:
            df[target_col] = df[target_col].map({"Yes": 1, "No": 0})

        y = df[target_col]
        X = df.drop(columns=[target_col])

        cat_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
        if cat_cols:
            X = pd.get_dummies(X, columns=cat_cols, drop_first=True)
        return X, y

    def run(self, pipeline: PipelineDefinition):
        logger.info(f"🚀 Entrenando modelo con MLflow: {pipeline.name}")
    
        # -----------------------------
        # 1) Dataset + DataPrep (si existe en YAML)
        # -----------------------------
        ds = pipeline.dataset
        dataset_path = ds.uri  # puede ser relativo
        dataset_path_abs = os.path.abspath(dataset_path)
        
        logger.info(f"ℹ️ CWD = {os.getcwd()}")
        logger.info(f"ℹ️ dataset.uri = {dataset_path} (abs: {dataset_path_abs})")
        logger.info(f"ℹ️ dataset.target = {getattr(ds, 'target', None)}")
        logger.info(f"ℹ️ dataset.dataprep presente? -> {bool(getattr(ds, 'dataprep', None))}")
        
        if str(dataset_path).startswith("s3://"):
            raise ValueError("MLflowExecutor solo soporta datasets locales (CSV).")
        
        # Ejecuta DataPrep embebido si viene `dataset.dataprep` en YAML
        dataprep_payload = getattr(ds, "dataprep", None)
        if dataprep_payload:
            try:
                logger.info("🧪 Ejecutando DataPrep embebido (dataset.dataprep) ...")
                df = nb.dataprep_run_inline(dataprep_payload)
        
                # 💾 Guardar SIEMPRE el limpio en dataset.uri (creando carpeta)
                clean_dir = os.path.dirname(dataset_path_abs)
                logger.info(f"🗂  Creando carpeta para limpio (si no existe): {clean_dir}")
                os.makedirs(clean_dir, exist_ok=True)
        
                logger.info(f"💾 Guardando dataset limpio en: {dataset_path_abs}")
                df.to_csv(dataset_path_abs, index=False)
        
                # 👇 MUY IMPORTANTE: seguimos con df en memoria; NO volvemos a leer del disco
            except Exception as e:
                logger.error(f"❌ Falló DataPrep embebido: {e}")
                raise
        else:
            # Sin dataprep → debemos leer el limpio directamente
            logger.info(f"📥 Cargando dataset limpio desde ruta: {dataset_path_abs}")
            if not os.path.exists(dataset_path_abs):
                # Mensaje de diagnóstico claro si el limpio no existe
                raise FileNotFoundError(
                    f"No existe el archivo limpio en dataset.uri.\n"
                    f"  - dataset.uri: {dataset_path}\n"
                    f"  - abs: {dataset_path_abs}\n"
                    f"  - cwd: {os.getcwd()}\n"
                    f"Sugerencias:\n"
                    f"  * Define 'dataset.dataprep' en el YAML para generarlo automáticamente.\n"
                    f"  * O crea previamente el archivo en esa ruta."
                )
            df = pd.read_csv(dataset_path_abs)
    
        # -----------------------------
        # 2) Target (obligatorio)
        # -----------------------------
        target = getattr(ds, "target", None)
        if not target:
            if "survived" in df.columns:
                target = "survived"
            elif "Survived" in df.columns:
                df = df.rename(columns={"Survived": "survived"})
                target = "survived"
            else:
                raise ValueError(
                    "El dataset debe contener una columna target. "
                    "Define dataset.target en YAML o provee 'survived/Survived'."
                )
    
        if target not in df.columns:
            raise ValueError(f"El dataset no contiene la columna target '{target}'.")
    
        # -----------------------------
        # 3) Split (estratificado si corresponde)
        # -----------------------------
        X = df.drop(columns=[target])
        y = df[target]
    
        is_classif = getattr(y, "nunique", lambda: 2)() <= 20
        strat = y if is_classif else None
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=strat
        )
    
        # -----------------------------
        # 4) Hiperparámetros y carga del modelo
        # -----------------------------
        params = pipeline.model.hyperparameters.model_dump(exclude_none=True)
        model_type = pipeline.model.type.lower()
        project_path = os.getcwd()
    
        max_attempts = 3
        for attempt in range(max_attempts):
            with mlflow.start_run(run_name=pipeline.name):
                # metadatos
                if os.path.exists(dataset_path):
                    mlflow.log_artifact(dataset_path, artifact_path="dataset")
                mlflow.set_tag("dataset.uri", pipeline.dataset.uri)
                mlflow.set_tag("version", pipeline.version)
                mlflow.set_tag("dataset.target", target)
                if getattr(pipeline, "description", None):
                    mlflow.set_tag("description", pipeline.description)
                if getattr(pipeline.governance, "owner", None):
                    mlflow.set_tag("owner", pipeline.governance.owner)
                if getattr(pipeline.governance, "tags", None):
                    for tag_dict in pipeline.governance.tags:
                        for k, v in tag_dict.items():
                            mlflow.set_tag(k, v)
    
                for param_name, param_value in params.items():
                    mlflow.log_param(param_name, param_value)
    
                # Carga dinámica del modelo desde models/
                source = getattr(pipeline.model, "source", "local")
                try:
                    model_instance = load_custom_model_class(project_path, model_type, source)
                except Exception as e:
                    logger.error(f"❌ Error al cargar el modelo '{model_type}': {e}")
                    raise
                
                # -----------------------------
                # 5) Entrenamiento usando tu wrapper
                # -----------------------------
                train_result = model_instance.train(X_train, y_train, X_test, y_test, params)
    
                if isinstance(train_result, tuple):
                    if len(train_result) == 3:
                        model, preds, metrics_dict = train_result
                    elif len(train_result) == 2:
                        model, preds = train_result
                        metrics_dict = evaluate_binary_classification(y_test, preds)
                    else:
                        raise ValueError("❌ El método 'train' retornó una tupla con longitud inesperada.")
                else:
                    raise ValueError("❌ El método 'train' debe retornar al menos (modelo, predicciones).")
    
                # firma para MLflow
                input_example = X_train.iloc[:5]
                output_example = predict_safely(model, input_example)
                signature = mlflow.models.signature.infer_signature(input_example, output_example)
    
                # métricas
                metrics_dict = evaluate_binary_classification(y_test, preds)
                for metric_name, value in metrics_dict.items():
                    mlflow.log_metric(metric_name, value)
    
                logger.info("📊 Métricas:")
                for k, v in metrics_dict.items():
                    logger.info(f" - {k}: {v:.4f}")
                logger.info(f"✅ Entrenamiento finalizado. AUC: {metrics_dict.get('auc', 0):.4f}")
    
                # -----------------------------
                # 6) Gate por umbrales del YAML
                # -----------------------------
                all_metrics_passed = True
                for metric in pipeline.metrics:
                    value = metrics_dict.get(metric.name)
                    if value is None:
                        logger.warning(f"⚠️ Métrica '{metric.name}' no fue calculada.")
                        continue
                    if value < metric.threshold:
                        logger.error(f"🚫 {metric.name.upper()} ({value:.4f}) < {metric.threshold}")
                        all_metrics_passed = False
    
                # -----------------------------
                # 7) Registro del modelo y batch output
                # -----------------------------
                if all_metrics_passed:
                    log_model_generic(
                        model,
                        model_name="model",
                        registered_model_name=f"{pipeline.name}-{model_type}",
                        input_example=input_example,
                        signature=signature,
                    )
    
                    if getattr(pipeline, "deploy", None) and pipeline.deploy.batch_output:
                        output_path = os.path.abspath(pipeline.deploy.batch_output)
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        pd.DataFrame({"prediction": preds}).to_csv(output_path, index=False)
                        logger.info(f"📦 Predicciones guardadas en: {output_path}")
    
                    return ModelResult(
                        model=model,
                        predictions=preds,
                        metrics=metrics_dict,
                        output_path=(
                            os.path.abspath(pipeline.deploy.batch_output)
                            if getattr(pipeline, "deploy", None) and pipeline.deploy.batch_output else None
                        ),
                    )
    
                # —— si no pasó, decide reintentar o rendirte con sugerencias
                if attempt < max_attempts - 1:
                    logger.warning(f"🔁 Reentrenando... (intento {attempt + 2}/{max_attempts})")
                    continue
                else:
                    logger.error("❌ Reentrenamiento fallido. Las métricas no alcanzaron los umbrales esperados.")
                    logger.info("💡 Sugerencias:")
                    logger.info("   - Ajusta los thresholds en godml.yml")
                    logger.info("   - Mejora la calidad del dataset (usa dataset.dataprep)")
                    logger.info("   - Prueba otros hiperparámetros (AutoTuning)")
    
                    raise RuntimeError("❌ Las métricas no alcanzaron los umbrales esperados.")



    def validate(self, pipeline: PipelineDefinition):
        """
        Valida configuración mínima del pipeline antes de ejecutar:
        - dataset: uri / dataprep / target
        - modelo: disponibilidad en registry core/local/adhoc
        - métricas: formato y tipos
        - validaciones adicionales (si existe godml.core_service.validators.validate_pipeline)
        Lanza ValueError si encuentra errores bloqueantes; loguea warnings si solo son advertencias.
        """
        errors = []
        warnings_ = []

        # 0) Validación externa (si existe)
        try:
            from godml.core_service.validators import validate_pipeline
            ext_warns = validate_pipeline(pipeline)
            for w in ext_warns:
                warnings_.append(str(w))
        except Exception:
            # no bloquea si no existe el validador
            pass

        # 1) Dataset & DataPrep
        ds = getattr(pipeline, "dataset", None)
        if ds is None:
            errors.append("dataset: faltante en el pipeline.")
        else:
            uri = getattr(ds, "uri", None)
            dataprep = getattr(ds, "dataprep", None)
            target = getattr(ds, "target", None)

            # Si NO hay dataprep, exigimos un archivo legible local
            if not dataprep:
                if not uri:
                    errors.append("dataset.uri: faltante (o define dataset.dataprep).")
                else:
                    try:
                        uri_str = str(uri)
                        if uri_str.startswith("s3://"):
                            warnings_.append("MLflowExecutor: s3:// no soportado; usa ruta local CSV.")
                        else:
                            from pathlib import Path
                            p = Path(uri_str)
                            if not p.exists():
                                errors.append(f"dataset.uri: archivo no encontrado -> {uri_str}")
                            elif p.suffix.lower() not in {".csv", ".parquet"}:
                                warnings_.append(f"dataset.uri: extensión {p.suffix} no es CSV/Parquet (CSV es la más probada).")
                    except Exception as e:
                        warnings_.append(f"No se pudo validar dataset.uri ('{uri}'): {e}")
            else:
                # Hay DataPrep embebido; validaciones mínimas de esquema
                if not isinstance(dataprep, dict):
                    errors.append("dataset.dataprep debe ser un dict (receta inline).")
                else:
                    if "inputs" not in dataprep:
                        warnings_.append("dataset.dataprep: falta 'inputs' (se intentará ejecutar igual).")
                    if "steps" not in dataprep:
                        warnings_.append("dataset.dataprep: falta 'steps' (se intentará ejecutar igual).")

            # Target
            if not target:
                warnings_.append(
                    "dataset.target no definido. Se aplicará heurística: 'survived'/'Survived' si existen; "
                    "de lo contrario, fallará en run()."
                )

        # 2) Modelo
        model = getattr(pipeline, "model", None)
        if model is None:
            errors.append("model: faltante en el pipeline.")
        else:
            model_type = getattr(model, "type", None)
            source = getattr(model, "source", "core")
            if not model_type or not isinstance(model_type, str):
                errors.append("model.type: faltante o inválido.")
            else:
                # Intento dry‑run de carga del modelo (sin entrenar)
                try:
                    project_path = os.getcwd()
                    _ = load_custom_model_class(project_path, model_type.lower(), source)
                except Exception as e:
                    errors.append(f"model: no se pudo cargar '{model_type}' desde source='{source}': {e}")

            # Hiperparámetros (solo forma)
            hp = getattr(model, "hyperparameters", None)
            if hp is None:
                warnings_.append("model.hyperparameters no definidos (se usarán defaults del wrapper si existen).")
            else:
                try:
                    # pydantic model o dict
                    if hasattr(hp, "model_dump"):
                        _ = hp.model_dump()
                    elif hasattr(hp, "dict"):
                        _ = hp.dict()
                    elif isinstance(hp, dict):
                        pass
                    else:
                        warnings_.append("model.hyperparameters no es dict ni pydantic; se intentará usar igualmente.")
                except Exception as e:
                    warnings_.append(f"No se pudieron inspeccionar hyperparameters: {e}")

        # 3) Métricas
        mets = getattr(pipeline, "metrics", None)
        if not mets or not isinstance(mets, (list, tuple)):
            warnings_.append("metrics: lista vacía o inválida; no habrá gate de umbrales.")
        else:
            for i, m in enumerate(mets):
                name = getattr(m, "name", None)
                thr = getattr(m, "threshold", None)
                if not name:
                    warnings_.append(f"metrics[{i}]: 'name' faltante.")
                if thr is None:
                    warnings_.append(f"metrics[{i}]: 'threshold' faltante.")
                else:
                    try:
                        float(thr)
                    except Exception:
                        warnings_.append(f"metrics[{i}]: threshold no numérico -> {thr!r}")

        # 4) Deploy (opcional)
        dep = getattr(pipeline, "deploy", None)
        if dep and getattr(dep, "batch_output", None):
            try:
                out_dir = os.path.dirname(os.path.abspath(dep.batch_output))
                if out_dir and not os.path.isdir(out_dir):
                    warnings_.append(f"deploy.batch_output: el directorio no existe aún ({out_dir}). Se intentará crearlo en run().")
            except Exception:
                pass

        # 5) Resultado final de validación
        for w in warnings_:
            logger.warning(f"⚠️ {w}")
        if errors:
            msg = " | ".join(errors)
            logger.error(f"❌ Validación de pipeline falló: {msg}")
            raise ValueError(f"Validación de pipeline falló: {msg}")

        logger.info("✅ Validación de pipeline completada sin errores bloqueantes.")
