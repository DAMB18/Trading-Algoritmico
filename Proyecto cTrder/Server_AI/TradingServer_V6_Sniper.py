import socket
import numpy as np
import pandas as pd
import tensorflow as tf
import joblib
from tensorflow.keras.models import load_model
import statsmodels.api as sm

# --- CONFIGURACIÓN TÉCNICA ---
MODEL_PATH = 'model_deep_lstm.keras'
SCALER_PATH = 'scaler_deep.pkl'
PORT = 5000

# 1. Función de Ernest Chan: Half-Life (Vida Media de la Tendencia)
# Determina si el precio está en una zona de reversión o inercia
def get_half_life(series):
    try:
        lag = series.shift(1)
        delta = series - lag
        lag, delta = lag.dropna(), delta.dropna()
        model = sm.OLS(delta, sm.add_constant(lag))
        res = model.fit()
        lmbda = res.params.iloc[1]
        return int(round(-np.log(2) / lmbda)) if lmbda < 0 else 24
    except:
        return 24

# 2. Carga de Inteligencia Artifical
print("Cargando modelo con Atención y Scaler...")
model = load_model(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', PORT))
    server_socket.listen(1)
    print(f"Servidor Sniper V6 activo en puerto {PORT}...")

    while True:
        conn, addr = server_socket.accept()
        try:
            data = conn.recv(10240).decode('utf-8')
            if not data: continue

            # Procesamiento de datos con Cultura Invariante (Punto decimal)
            raw_values = [float(x) for x in data.split(',')]
            
            # Reestructurar para el modelo (Window_Size=24, Features=7)
            input_data = np.array(raw_values).reshape(1, 24, 7)
            
            # Escalamiento
            input_scaled = np.zeros(input_data.shape)
            for i in range(input_data.shape[0]):
                input_scaled[i] = scaler.transform(input_data[i])

            # 3. Predicción de la IA (Atención)
            prediction = model.predict(input_scaled, verbose=0)[0][0]

            # 4. Filtro de Validación de Chan (Half-Life)
            # Extraemos la serie de precios del US500 del input recibido
            price_series = pd.Series(input_data[0, :, 0])
            h_life = get_half_life(price_series)

            # Si el Half-Life es muy corto, la señal es volátil; si es largo, es tendencial
            # Enviamos la predicción final al cBot
            response = f"{prediction:.4f}".replace(',', '.')
            conn.sendall(response.encode('utf-8'))
            
            print(f"Datos recibidos | Pred: {prediction:.4f} | Half-Life: {h_life}h")

        except Exception as e:
            print(f"Error en servidor: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    start_server()