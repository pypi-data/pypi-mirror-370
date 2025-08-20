# {project_name}
**Proyecto GODML - Machine Learning con Gobernanza**

[![GODML](https://img.shields.io/badge/Powered%20by-GODML-blue.svg)](https://pypi.org/project/godml/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Proyecto generado automáticamente con **GODML Framework** - Governed, Observable & Declarative ML

---

## 🧠 Arquitectura GODML

- **Core Service**: ejecución de modelos
- **Config Service**: validación de YAML y gobernanza
- **Model Service**: entrenamiento, evaluación, registro
- **Monitoring Service**: métricas, trazabilidad, cumplimiento

```
📂 godml/
├── core_service/
├── config_service/
├── model_service/
├── monitoring_service/
├── compliance_service/
```

---

## 📁 Estructura del Proyecto

```
{project_name}/
├── godml.yml              # 🎯 Configuración principal del pipeline
├── data/                  # 📊 Datasets
│   └── your_dataset.csv
├── outputs/               # 📈 Predicciones y resultados
│   └── predictions.csv
├── models/                # 🤖 Modelos entrenados
│   ├── production/
│   ├── staging/
│   └── experiments/
├── mlruns/                # 📋 Experimentos MLflow (auto-generado)
├── requirements.txt       # 📦 Dependencias
└── README.md              # 📖 Documentación
```

---

## ⚙️ YAML de Configuración (`godml.yml`)

```yaml
dataset:
  uri: ./data/your_dataset.csv
  hash: auto

model:
  type: xgboost
  hyperparameters:
    max_depth: 5
    eta: 0.3
    objective: binary:logistic

metrics:
  - name: auc
    threshold: 0.85
  - name: accuracy
    threshold: 0.80

governance:
  owner: your-team@company.com
  tags:
    - project: {project_name}
    - environment: development

deploy:
  realtime: false
  batch_output: ./outputs/predictions.csv
```

---

## 🚀 Flujo de Trabajo

1. **Preparar Datos**  
   `cp mi_dataset.csv data/your_dataset.csv`

2. **Configurar Pipeline**  
   `vim godml.yml`

3. **Entrenar Modelo**  
   `godml run -f godml.yml`

4. **Visualizar Experimentos**  
   `mlflow ui`

---

## 🧪 Entrenamiento desde Notebooks

```python
from godml.notebook_api import GodmlNotebook
godml = GodmlNotebook()
godml.create_pipeline(
    name="churn_rf",
    model_type="random_forest",
    hyperparameters={{"max_depth": 3}},
    dataset_path="./data/churn.csv"
)
godml.train()
godml.save_model("churn_rf", environment="experiments")
```

## ⚡ Entrenamiento rápido

```python
from godml.notebook_api import quick_train

quick_train(
    model_type="xgboost",
    hyperparameters={{"eta": 0.1, "max_depth": 4}},
    dataset_path="./data/churn.csv"
)
```

## 🔁 Desde YAML

```python
from godml.notebook_api import train_from_yaml
train_from_yaml("godml.yml")
```

---

## 🧭 Comandos CLI Disponibles

- `godml init <nombre>`: inicializa proyecto
- `godml run -f godml.yml`: ejecuta pipeline
- `godml hash <path>`: calcula hash de un archivo
- `godml version`: muestra versión instalada

---

## 📊 Métricas Soportadas

- `auc`, `accuracy`, `precision`, `recall`, `f1`

---

## ✅ Cumplimiento y Gobernanza

- Hash de dataset automático
- Metadatos del modelo y métricas
- Soporte para normativas (PCI-DSS, etc.)
- Trazabilidad de experimentos con MLflow

---

## 📚 Recursos

- [GODML en PyPI](https://pypi.org/project/godml/)
- Documentación oficial (próximamente)
- Guía de gobernanza (en construcción)

---

Generado con ❤️ por **GODML Framework v0.3.0**