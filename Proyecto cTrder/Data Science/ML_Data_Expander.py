import pandas as pd
import glob
import os

def build_master_dataset(path_folder):
    # Definimos las columnas maestras
    main_ticker = "US500"
    secondary_tickers = ["USOIL", "XAUUSD", "EURUSD"]
    
    # 1. Cargar todos los archivos de US500 y unirlos cronológicamente
    us500_files = sorted(glob.glob(os.path.join(path_folder, f"*{main_ticker}*.csv")))
    df_main = pd.concat([pd.read_csv(f, parse_dates=['Timestamp']) for f in us500_files])
    df_main = df_main.drop_duplicates(subset=['Timestamp']).set_index('Timestamp').sort_index()
    
    # Limpiar nombres de columnas (quitar ruidos de exportación)
    df_main.columns = [c.split('(')[0] for c in df_main.columns]
    
    # 2. Unir activos secundarios con sufijos claros
    for ticker in secondary_tickers:
        t_files = sorted(glob.glob(os.path.join(path_folder, f"*{ticker}*.csv")))
        if not t_files: continue
        
        df_sec = pd.concat([pd.read_csv(f, parse_dates=['Timestamp']) for f in t_files])
        df_sec = df_sec.drop_duplicates(subset=['Timestamp']).set_index('Timestamp')
        
        # Unimos solo la columna 'Close' renombrada
        df_main = df_main.join(df_sec[['Close']].rename(columns={'Close': f'Close_{ticker}'}), how='inner')
        print(f"[OK] Sincronizado {ticker} - Filas actuales: {len(df_main)}")

    # 3. Guardar Dataset Maestro
    output_path = "MASTER_DATA_10Y.csv"
    df_main.to_csv(output_path)
    print(f"\n[FINALIZADO] Dataset de largo plazo creado: {output_path}")
    print(f"Rango temporal: {df_main.index.min()} a {df_main.index.max()}")
    return df_main

if __name__ == "__main__":
    PATH = r'C:\Users\alexb\Desktop\Daniel\CTrader\exported'
    build_master_dataset(PATH)