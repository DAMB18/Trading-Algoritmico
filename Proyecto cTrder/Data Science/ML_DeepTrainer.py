import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout, BatchNormalization, MultiHeadAttention, GlobalAveragePooling1D
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from sklearn.utils import class_weight
import statsmodels.api as sm


def calculate_half_life(series):
    # Basado en la metodología de Ernest Chan para reversión a la media
    lag = series.shift(1)
    delta = series - lag
    lag = lag.dropna()
    delta = delta.dropna()
    
    # Regresión lineal para encontrar el coeficiente de lambda
    model = sm.OLS(delta, sm.add_constant(lag))
    res = model.fit()
    
    # Lambda es el coeficiente de la serie retrasada
    lmbda = res.params.iloc[1] # Cambiado de [1] a .iloc[1] para evitar errores de pandas
    
    # Half-life = -ln(2) / lambda
    if lmbda < 0:
        half_life = -np.log(2) / lmbda
        return int(round(half_life))
    else:
        return 24 # Valor por defecto si no hay reversión clara



# --- CONFIGURACIÓN TÉCNICA ---
FEATURES_LIST = ['Close', 'RSI', 'ATR', 'ADX', 'Close_USOIL', 'Close_XAUUSD', 'Close_EURUSD']


def build_attention_model(input_shape):
    inputs = Input(shape=input_shape)
    
    # 1. LSTM con Dropout moderado
    lstm_out = LSTM(128, return_sequences=True)(inputs)
    lstm_out = BatchNormalization()(lstm_out)
    lstm_out = Dropout(0.15)(lstm_out)
    
    # 2. Capa de Atención para enfocar patrones clave
    attn_layer = MultiHeadAttention(num_heads=4, key_dim=128)(lstm_out, lstm_out)
    
    # 3. Procesamiento profundo
    # Usamos GlobalAveragePooling para simplificar la salida de la atención
    avg_pool = GlobalAveragePooling1D()(attn_layer)
    dense = Dense(64, activation='relu')(avg_pool)
    dense = Dropout(0.1)(dense)
    outputs = Dense(1, activation='sigmoid')(dense)
    
    model = Model(inputs, outputs)
    
    # AJUSTE CRÍTICO: Learning Rate más bajo (0.0001) para evitar inestabilidad
    optimizer = Adam(learning_rate=0.0001)
    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
    return model

def train_v5():
    df = pd.read_csv("MASTER_DATA_10Y.csv", parse_dates=['Timestamp']).set_index('Timestamp')

    # 1. Integramos el cálculo de Chan aquí
    dynamic_window = calculate_half_life(df['Close'])

    # Limitamos la ventana para que no sea ni muy pequeña ni muy grande
    dynamic_window = max(12, min(dynamic_window, 48)) 
    
    print(f"Propuesta de Ernest Chan: Window Size ajustado a {dynamic_window} horas.")
    
    # 2. Usamos esta ventana para crear las secuencias X, y
    WINDOW_SIZE = dynamic_window
    
    # Mantenemos tu criterio de 0.05%
    df['Target'] = (df['Close'].pct_change().shift(-1) > 0.0005).astype(int)
    df = df.dropna()

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df[FEATURES_LIST])
    
    X, y = [], []
    for i in range(len(scaled_data) - WINDOW_SIZE):
        X.append(scaled_data[i:i+WINDOW_SIZE])
        y.append(df['Target'].values[i+WINDOW_SIZE])
    
    X, y = np.array(X), np.array(y)

    # --- BALANCEO DE CLASES AUTOMÁTICO ---
    # Esto le dirá a la IA que la Clase 1 es más "valiosa" porque hay menos
    weights = class_weight.compute_class_weight('balanced', classes=np.unique(y), y=y)
    dict_weights = dict(enumerate(weights))

    model = build_attention_model((WINDOW_SIZE, 7))
    
    # CALLBACKS DE RESCATE
    checkpoint = ModelCheckpoint('model_deep_lstm.keras', save_best_only=True, monitor='val_accuracy')
    early_stop = EarlyStopping(monitor='val_loss', patience=12, restore_best_weights=True)
    # Si el modelo se estanca, reduce la velocidad de aprendizaje
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=4, min_lr=0.00001)

    print(f"Iniciando entrenamiento balanceado... Pesos: {dict_weights}")
    model.fit(X, y, epochs=100, batch_size=64, 
              validation_split=0.2, 
              class_weight=dict_weights,
              callbacks=[checkpoint, early_stop, reduce_lr])

if __name__ == "__main__":
    train_v5()