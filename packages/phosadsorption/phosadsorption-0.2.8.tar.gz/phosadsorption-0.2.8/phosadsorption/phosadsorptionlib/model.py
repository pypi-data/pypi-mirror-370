
import pandas as pd
import numpy as np
import xgboost as xgb
from pathlib import Path
from phosadsorption.phosadsorptionlib.utils import preprocess_dataframe

class PhosAdsorptionLib:
    def __init__(self):
        model_path = Path(__file__).parent / "multioutput_xgb_model.json"
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        self.booster = xgb.Booster()
        self.booster.load_model(str(model_path))

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        df_expanded = preprocess_dataframe(df.copy())
        feature_cols = ['S', 'C', 'pH', 'EC', 'Organic matter', 'P', 'Mg', 'Mn', 'Cu']
        X_input = df_expanded[feature_cols]
        dmatrix = xgb.DMatrix(X_input)
        y_pred = self.booster.predict(dmatrix)

        ppm_levels = [1, 2, 4, 6, 10]
        for i, ppm in enumerate(ppm_levels):
            df_expanded[f'XGBoost_{ppm}ppm_adsorbed'] = y_pred[:, i]

        S = df_expanded['S'] / 100
        C = df_expanded['C'] / 100
        OM = df_expanded['Organic matter']

        partA = 0.278*S + 0.034*C + 0.022*OM - 0.018*S*OM - 0.027*C*OM - 0.584*S*C + 0.078
        partB = partA + 0.636 * partA - 0.107
        partC = -0.251*S + 0.195*C + 0.011*OM + 0.006*S*OM - 0.027*C*OM + 0.452*S*C + 0.299
        partD = partC + 1.283 * partC**2 - 0.374 * partC - 0.015
        partE = partD + partB - 0.097 * S + 0.043
        df_expanded['FEB'] = (1 - partE) * 2.65

        for ppm in ppm_levels:
            applied_kg = 30*(ppm/1000)*(1000/3)*2.29*(1000*0.15*df_expanded['FEB']*1000/1000000)
            applied_mgkg = (applied_kg * 0.4364 * 1_000_000) / (df_expanded['FEB'] * 15 * 10_000)
            applied_mgkg_ha = 10 * applied_mgkg

            df_expanded[f'{ppm}ppm_applied'] = applied_mgkg_ha
            df_expanded[f'PFP{ppm}'] = round(
                df_expanded[f'XGBoost_{ppm}ppm_adsorbed'] * 100 / applied_mgkg_ha, 1)
            df_expanded[f'P_applied_kg_per_ha_at_{ppm}ppm'] = round(applied_kg * 10, 1)

        output_cols = [f'P_applied_kg_per_ha_at_{ppm}ppm' for ppm in ppm_levels] + \
                      [f'PFP{ppm}' for ppm in ppm_levels]
        return df_expanded[output_cols]


