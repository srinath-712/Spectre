import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

df = pd.read_csv("backend/data/features.csv")

# Check 1 — are features actually different per class?
print("\n--- FEATURE MEANS BY CLASS ---")
print(df.groupby("label").mean().T.to_string())

# Check 2 — correlation matrix (are features redundant?)
print("\n--- FEATURE CORRELATION MATRIX ---")
print(df.drop("label", axis=1).corr().round(2).to_string())

# Check 3 — per-class feature distribution overlap
print("\n--- CLASS SEPARATION (Std of Class Means) ---")
for col in df.columns:
    if col == "label":
        continue
    overlap = df.groupby("label")[col].mean().std()
    print(f"{col}: class separation std = {overlap:.3f}")
