Deep Intelligence Trading System (DITS) - Sniper V6
Este sistema es una arquitectura de ejecución algorítmica de alta fidelidad que integra Deep Learning (Atención Multicabezal) con principios clásicos de la microestructura de mercados y gestión cuantitativa.

🧠 Fundamentos Teóricos Aplicados
La robustez de este sistema no reside solo en su capacidad predictiva, sino en la integración de capas lógicas basadas en literatura financiera de élite:

1. Dinámica de Precios y Ciclos (Wyckoff & DeMark)
Ley de Esfuerzo vs. Resultado: El sistema analiza la relación entre el volumen y el rango de la vela para identificar fases de acumulación o distribución profesional, evitando entrar en zonas de absorción.

Agotamiento de Tendencia: Se integran conteos lógicos basados en el TD Sequential para filtrar señales de la IA en zonas de sobre-extensión, reduciendo significativamente los falsos positivos.

2. Análisis Cuantitativo de Reversión (Ernest Chan)
Cálculo de Half-Life: El motor de inferencia utiliza procesos de Ornstein-Uhlenbeck para determinar la "vida media" de la serie temporal en tiempo real.

Ajuste de Ventana Temporal: El WINDOW_SIZE del modelo se optimiza dinámicamente según la velocidad de reversión a la media detectada, permitiendo que la red neuronal se adapte a diferentes regímenes de volatilidad.

3. Gestión de Capital y Supervivencia (Graham & Axiomas de Zúrich)
Margen de Seguridad: El dimensionamiento de la posición (Position Sizing) se calcula bajo la premisa de Benjamin Graham de preservar el principal mediante un límite de riesgo estricto por operación.

Protección Dinámica: Aplicación del principio de "cortar pérdidas rápido" mediante un Trailing Stop que se activa a Breakeven una vez alcanzado un umbral de beneficio crítico, eliminando el riesgo emocional.

🛠️ Stack Tecnológico
Ejecución: cTrader (C# / .NET) - Cliente de baja latencia.

Motor de IA: Python 3.10+ (TensorFlow/Keras) - Servidor de inferencia.

Comunicación: Sockets TCP/IP asíncronos con manejo de Cultura Invariante.

Modelo: LSTM con Capa de Atención (Multi-Head Attention) para la detección de dependencias temporales complejas.

📊 Métricas de Desempeño (Accuracy & Confusion Matrix)
El sistema ha sido validado mediante un pipeline de Backtesting Out-of-Sample, evaluando no solo el Accuracy global, sino la Precisión y el Recall de las señales de compra, asegurando una ventaja estadística real sobre el azar.