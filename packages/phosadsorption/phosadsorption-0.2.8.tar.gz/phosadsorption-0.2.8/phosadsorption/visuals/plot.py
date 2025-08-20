import matplotlib.pyplot as plt

def plot_pfp_vs_applied(df, sample_index=0):
    ppm_levels = [1, 2, 4, 6, 10]
    applied_cols = [f'P_applied_kg_per_ha_at_{ppm}ppm' for ppm in ppm_levels]
    pfp_cols = [f'PFP{ppm}' for ppm in ppm_levels]

    # Validate columns
    missing = [col for col in applied_cols + pfp_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Validate index
    if sample_index < 0 or sample_index >= len(df):
        raise IndexError(f"Sample index {sample_index} is out of bounds for DataFrame with {len(df)} rows.")

    applied = df.loc[sample_index, applied_cols].values
    pfp = df.loc[sample_index, pfp_cols].values

    plt.figure(figsize=(8, 5))
    plt.plot(applied, pfp, marker='o')
    plt.title(f"PFP vs P Applied (Sample {sample_index})")
    plt.xlabel("Phosphorus Applied (kg/ha)")
    plt.ylabel("Percentage Phosphorus Adsorption (%)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
