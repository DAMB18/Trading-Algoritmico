import numpy as np
import pandas as pd
import tensorflow as tf
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report

# 1. Cargar datos y modelo
df = pd.read_csv("MASTER_DATA_10Y.csv", parse_dates=['Timestamp']).set_index('Timestamp')
scaler = joblib.load('scaler_deep.pkl')
features = joblib.load('model_features_deep.pkl')
model = tf.keras.models.load_model('model_deep_lstm.keras')

# 2. Preparar el set de prueba (último 20% de los datos)
df['Target'] = (df['Close'].pct_change().shift(-1) > 0.0005).astype(int)
df = df.dropna()
scaled_data = scaler.transform(df[features])

X, y_true = [], []
for i in range(len(scaled_data) - 24):
    X.append(scaled_data[i:i+24])
    y_true.append(df['Target'].values[i+24])

X, y_true = np.array(X), np.array(y_true)

# Tomamos solo el segmento final para la evaluación (Validación Out-of-Sample)
test_size = int(len(X) * 0.2)
X_test = X[-test_size:]
y_test = y_true[-test_size:]

# 3. Predicciones
y_pred_prob = model.predict(X_test)
y_pred = (y_pred_prob > 0.5).astype(int)

# 4. Generar Matriz de Confusión
cm = confusion_matrix(y_test, y_pred)
print("\n--- REPORTE DE CLASIFICACIÓN ---")
print(classification_report(y_test, y_pred, target_names=['No Compra', 'Compra']))

# 5. Visualización
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Pred: No', 'Pred: Si'], yticklabels=['Real: No', 'Real: Si'])
plt.title('Matriz de Confusión - Modelo V5 Attention')
plt.xlabel('Predicción del Modelo')
plt.ylabel('Realidad del Mercado')
plt.show()