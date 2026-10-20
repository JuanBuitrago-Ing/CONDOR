# CÓNDOR: identificación de aves por su canto con inteligencia artificial

Sistema embebido que escucha el ambiente, detecta cuándo canta un ave e identifica la especie en tiempo real. Funciona en una Raspberry Pi 4 con batería y sin internet, para que biólogos puedan monitorear la biodiversidad de un ecosistema directamente en campo.

**Universidad de los Llanos · Villavicencio, Colombia · 2026**

## Cómo funciona

```
Micrófono USB → Raspberry Pi 4 → detección de canto → 2 modelos de IA → SQLite → interfaz web (celular)
```

1. La Raspberry graba el ambiente con un micrófono USB y detecta cuándo hay un sonido por encima del ruido de fondo.
2. Cada fragmento se clasifica con dos modelos en paralelo: un Random Forest y una red neuronal convolucional.
3. Cada detección se guarda con fecha, hora, especie y nivel de confianza.
4. La Raspberry crea su propia red WiFi. Desde el celular se abre la interfaz CÓNDOR con la detección en vivo, el historial y las fichas de las especies.

## Datos

- Audios de cantos tomados de [Xeno-Canto](https://xeno-canto.org) y [Macaulay Library](https://www.macaulaylibrary.org), recolectados en equipo.
- Procesamiento automatizado con scripts en Python: verificación de la duración de cada audio, división de grabaciones largas en partes de un minuto, corte en segmentos de 10 s y normalización a mono de 22.050 Hz.
- Aumento de datos (cambio de tono y velocidad, ruido, desplazamiento temporal) para balancear el dataset: **20 especies de los Llanos Orientales, 840 audios por especie.**

## Modelos

| Modelo | Entrada | Resultado |
| --- | --- | --- |
| Random Forest | 70 características acústicas (MFCC, chroma, contraste espectral, ZCR, rolloff, energía RMS) | 95,9 % en validación cruzada de 5 folds (7 especies) |
| CNN con transfer learning (MobileNetV2) | Espectrogramas Mel de 128 × 128 | 94,5 % en el conjunto de prueba (7 especies) |

Las cifras corresponden a la primera versión del dataset (7 especies, audios originales), evaluada sin aumento de datos. El modelo actual de 20 especies se entrenó con el dataset aumentado.

## Estructura del repositorio

```
colab/                       Entrenamiento en Google Colab
  01_procesar_audios.py        Corte en segmentos de 10 s y normalización
  02a_aumento_datos_...py      Aumento de datos para las especies nuevas
  02b_balancear_840_...py      Balanceo a 840 audios por especie
  03_renombrar_carpetas_...py  Ajuste de nombres de carpetas en Google Drive
  04_espectrogramas_...py      Generación de espectrogramas Mel
  05_random_forest_...py       Entrenamiento del Random Forest (20 especies)
  06_cnn_transfer_...py        Entrenamiento de la CNN con MobileNetV2
  07_demo_gradio.py            Demo web tipo "Shazam" para probar los modelos
raspberry/                   Sistema en campo
  inferencia.py                Captura, detección, clasificación y registro en SQLite
  app.py                       Servidor Flask con la interfaz CÓNDOR
  descargar_fotos.py           Descarga de fotos para las fichas de especies
versiones_anteriores/        Primeras versiones con 7 especies
```

## Hardware

- Raspberry Pi 4 Model B (4 GB)
- Micrófono USB (cámara Logitech C920)
- Powerbank como fuente de energía

## Cómo ejecutarlo en la Raspberry

```bash
pip install -r requirements.txt
python3 raspberry/inferencia.py   # terminal 1: escucha y clasifica
python3 raspberry/app.py          # terminal 2: interfaz web en el puerto 5000
```

Los modelos entrenados (`.joblib` y `.keras`) se generan con los scripts de `colab/` y se copian a la Raspberry.

## Tecnologías

Python · TensorFlow/Keras · scikit-learn · librosa · Flask · SQLite · Google Colab · Raspberry Pi OS

## Autor

**Juan Camilo Céspedes Buitrago**, estudiante de Ingeniería Electrónica, Universidad de los Llanos.
