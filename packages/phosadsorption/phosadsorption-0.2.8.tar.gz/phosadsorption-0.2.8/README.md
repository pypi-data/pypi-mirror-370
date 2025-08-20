# Phosadsorption

**Phosadsorption** is a Python library for predicting phosphorus (P) adsorption in soils using machine learning. It replaces traditional empirical models like the Langmuir isotherm with a data-driven approach built on XGBoost.

## Why Phosadsorption?

While the Langmuir isotherm has been widely used to model phosphorus adsorption, it often fails to capture the variability seen in real-world soils with diverse physicochemical characteristics. This library introduces a **multioutput XGBoost regressor** trained on soil data to predict phosphorus adsorption across multiple equilibrium concentrations simultaneously.

## Key Features

- 🔬 Predicts phosphorus adsorption at 1, 2, 4, 6, and 10 mg/L equilibrium concentrations.
- 📈 Outperforms traditional models like Langmuir in predictive accuracy.
- 🧪 Built for soil scientists, agronomists, and environmental engineers.
- 📦 Easy to install and use with just a few lines of code.

## Installation

Install from PyPI:

```bash
pip install phosadsorption
```

Or install from TestPyPI for pre-release versions:

```bash
pip install --index-url https://test.pypi.org/simple/ phosadsorption
```

## Example Usage

Input Requirements: The Excel file should include the following soil parameters (all reported in mg/kg of soil unless otherwise noted):

S (Sand %),

C (Clay %),

pH,

EC (Electrical Conductivity, dS/m),

Organic matter (% or equivalent label),

P (Phosphorus),

Mg (Magnesium),

Mn (Manganese),

Cu (Copper)

Note: All nutrient concentrations provided as input should be reported in units of mg/kg of soil to ensure consistent and accurate predictions.

```python
from phosadsorption.phosadsorptionlib import PhosAdsorptionLib
from phosadsorption.visuals import plot_pfp_vs_applied
import pandas as pd

# Load your input data
df = pd.read_excel("your_input.xlsx")

print(df.head(3).to_markdown(index=False))

|   Α.Μ.Δ |   ΒΑΘΟΣ | Soil texture   |   S |   C |     Si  |   pH |    EC |   Organic matter |    CaCO3    |   NO3 |   NO3-N |     P |     K |   Mg | Ca    |     Fe  |   Zn |    Mn |    Cu |    B |
|--------:|--------:|:---------------|----:|----:|--------:|-----:|------:|-----------------:|------------:|------:|--------:|------:|------:|-----:|:------|--------:|-----:|------:|------:|-----:|
|  251001 |     nan | L              |  44 |  22 |      34 | 7    | 0.479 |             3.57 |         0   |  79.4 |   17.92 | 44.85 |   420 | 1001 | 1008  |   53.92 | 5.96 | 10.51 | 63.12 | 1.24 |
|  251002 |     nan | SL             |  54 |  18 |      28 | 5.15 | 0.722 |             3.08 |         0   | 139.2 |   31.44 | 46.05 |   485 |  263 | 1360  |   67.98 | 1.75 | 47.42 | 14.78 | 1.5  |
|  251003 |     nan | CL             |  30 |  30 |      40 | 7.31 | 0.557 |             2.57 |         5.2 |  62   |   14    |  3.94 |   243 |  656 | >2000 |    5.62 | 0.36 |  4.48 |  3.22 | 0.35 |

# Initialize and run the model
model = PhosAdsorptionLib()
result = model.predict(df)



print(result.head(3).to_markdown(index=False))


|   P_applied_kg_per_ha_at_1ppm |   P_applied_kg_per_ha_at_2ppm |   P_applied_kg_per_ha_at_4ppm |   P_applied_kg_per_ha_at_6ppm |   P_applied_kg_per_ha_at_10ppm |   PFP1 |   PFP2 |   PFP4 |   PFP6 |   PFP10 |
|------------------------------:|------------------------------:|------------------------------:|------------------------------:|-------------------------------:|-------:|-------:|-------:|-------:|--------:|
|                          47.3 |                          94.6 |                         189.2 |                         283.8 |                          473   |   61.5 |   76.7 |   70.3 |   81.8 |    78.3 |
|                          49.1 |                          98.2 |                         196.4 |                         294.5 |                          490.9 |   78.6 |   86.3 |   87.7 |   92.4 |    90.7 |
|                          47.7 |                          95.4 |                         190.8 |                         286.2 |                          477   |   89.2 |   87.6 |   91.8 |   90.2 |    85.3 |

#PFP stands for Phosphorus Fraction Percentage and represents the percentage of applied phosphorus that was adsorbed by the soil (expressed as %).

# Plot results for first sample
plot_pfp_vs_applied(result, sample_index=0)

```

## Project Structure

```
phosadsorption/
├── __init__.py
├── phosadsorptionlib/
│   ├── __init__.py
│   ├── model.py
│   ├── utils.py
│   └── multioutput_xgb_model.json
├── visuals/
│   ├── __init__.py
│   └── plot.py
README.md
MANIFEST.in
setup.py
```

## License

MIT License

## Citation

If you use this library in your work, please cite:

> Iatrou, M.; Papadopoulos, A. Machine Learning vs. Langmuir: A Multioutput XGBoost Regressor Better Captures Soil Phosphorus Adsorption Dynamics. Crops 2025, 5, 55. https://doi.org/10.3390/crops5040055
> *GitHub Repository:* [https://github.com/Mil-afk/soil_phosphorus_adsorption_data](https://github.com/Mil-afk/soil_phosphorus_adsorption_data)
