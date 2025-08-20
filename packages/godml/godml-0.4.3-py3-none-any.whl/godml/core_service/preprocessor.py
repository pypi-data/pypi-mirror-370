# core_service/preprocessor.py

from typing import Optional
import pandas as pd

from godml.compliance_service.compliance_registry import ComplianceRegistry

class ComplianceEngine:
    """
    Lógica para aplicar normativas de cumplimiento antes del entrenamiento.
    """

    @staticmethod
    def apply(df: pd.DataFrame, compliance_type: Optional[str] = None) -> pd.DataFrame:
        if not compliance_type:
            return df

        try:
            compliance = ComplianceRegistry.get_compliance(compliance_type)
            print(f"🔐 Aplicando cumplimiento: {compliance_type}")
            return compliance.apply(df)
        except ValueError as e:
            print(f"⚠️ Error: {e}")
            return df
