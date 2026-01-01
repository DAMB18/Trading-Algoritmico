import pandas as pd

# Cargar el dataset maestro
df = pd.read_csv("MASTER_DATA_10Y.csv")

# Calcular el target (usando el mismo criterio que el entrenador)
df['Target'] = (df['Close'].pct_change().shift(-1) > 0.0005).astype(int)
df = df.dropna()

# Contar proporciones
counts = df['Target'].value_counts()
percent = df['Target'].value_counts(normalize=True) * 100

print("--- BALANCE DE CLASES DEL DATASET ---")
print(f"Clase 0 (No Compra/Baja): {counts[0]} muestras ({percent[0]:.2f}%)")
print(f"Clase 1 (Compra/Subida):  {counts[1]} muestras ({percent[1]:.2f}%)")

if abs(percent[0] - percent[1]) > 20:
    print("\n⚠️ ALERTA: Dataset desequilibrado. Necesitas ajustar class_weights.")
else:
    print("\n✅ Dataset equilibrado. El problema es la Tasa de Aprendizaje.")