# ============================================================
# PASO 1 — Generación de Espectrogramas Mel
# ============================================================
import os
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from google.colab import drive

drive.mount('/content/drive')

RUTA_BASE    = '/content/drive/MyDrive/PROYECTO IA/AUDIOS_MOD_AVES'
RUTA_SPECTRO = '/content/drive/MyDrive/PROYECTO IA/ESPECTROGRAMAS'

# ── Parámetros de audio y espectrograma ─────────────────────
SR       = 22050   # frecuencia de muestreo
DURATION = 10      # segundos por muestra
N_MELS   = 128     # bandas Mel (resolución frecuencial)
HOP_LEN  = 512     # salto entre ventanas
N_FFT    = 2048    # tamaño de ventana FFT
IMG_SIZE = (128, 128)  # tamaño final de imagen para la CNN

def audio_a_espectrograma(ruta_audio):
    """
    Convierte un archivo WAV a espectrograma Mel normalizado.
    Retorna array numpy listo para la CNN.
    """
    # Cargar audio
    y, sr = librosa.load(ruta_audio, sr=SR, duration=DURATION, mono=True)

    # Padding si el audio es más corto que DURATION

    longitud_esperada = SR * DURATION
    if len(y) < longitud_esperada:
        y = np.pad(y, (0, longitud_esperada - len(y)), mode='constant')

    # Calcular espectrograma Mel
    mel_spec = librosa.feature.melspectrogram(
        y=y, sr=sr,
        n_mels=N_MELS,
        hop_length=HOP_LEN,
        n_fft=N_FFT
    )

    # Convertir a decibeles (escala logarítmica — más natural para el oído)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

    # Normalizar entre 0 y 1
    mel_spec_norm = (mel_spec_db - mel_spec_db.min()) / (mel_spec_db.max() - mel_spec_db.min())

    return mel_spec_norm

def guardar_espectrograma(mel_spec, ruta_salida):
    """
    Guarda el espectrograma como imagen PNG sin ejes ni bordes.
    """
    fig, ax = plt.subplots(figsize=(IMG_SIZE[1]/100, IMG_SIZE[0]/100), dpi=100)
    ax.imshow(mel_spec, aspect='auto', origin='lower', cmap='viridis')
    ax.axis('off')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(ruta_salida, bbox_inches='tight', pad_inches=0)
    plt.close()

def generar_dataset_espectrogramas(ruta_base, ruta_salida):

    """
    Recorre todas las especies y genera los espectrogramas.
    Estructura de salida:
      ESPECTROGRAMAS/
        Especie_1/
          audio_001.png
          audio_002.png
        Especie_2/
          ...
    """
    os.makedirs(ruta_salida, exist_ok=True)
    resumen = {}

    for especie in sorted(os.listdir(ruta_base)):
        ruta_especie = os.path.join(ruta_base, especie)
        if not os.path.isdir(ruta_especie):
            continue

        ruta_especie_out = os.path.join(ruta_salida, especie)
        os.makedirs(ruta_especie_out, exist_ok=True)

        archivos = [f for f in os.listdir(ruta_especie) if f.endswith('.wav')]
        procesados = 0

        print(f"\nProcesando: {especie} ({len(archivos)} archivos)")

        for archivo in archivos:
            ruta_audio = os.path.join(ruta_especie, archivo)
            nombre_png = os.path.splitext(archivo)[0] + '.png'
            ruta_png   = os.path.join(ruta_especie_out, nombre_png)

            # Saltar si ya existe

            if os.path.exists(ruta_png):
                procesados += 1
                continue

            try:
                mel_spec = audio_a_espectrograma(ruta_audio)
                guardar_espectrograma(mel_spec, ruta_png)
                procesados += 1
            except Exception as e:
                print(f"  Error en {archivo}: {e}")

        resumen[especie] = procesados
        print(f"  ✓ {procesados} espectrogramas generados")

    print(f"\n{'='*50}")
    print("RESUMEN FINAL:")
    total = 0
    for esp, n in resumen.items():
        print(f"  {esp}: {n} imágenes")
        total += n
    print(f"  TOTAL: {total} espectrogramas")
    print(f"  Guardados en: {ruta_salida}")

# ── Visualizar ejemplo ───────────────────────────────────────
def visualizar_ejemplos(ruta_base, n=3):
    """
    Muestra n espectrogramas de ejemplo para verificar que se ven bien.
    """
    fig, axes = plt.subplots(1, n, figsize=(15, 4))
    especies = sorted(os.listdir(ruta_base))[:n]

    for i, especie in enumerate(especies):

        ruta_especie = os.path.join(ruta_base, especie)
        archivos = [f for f in os.listdir(ruta_especie) if f.endswith('.wav')]
        if not archivos:
            continue

        ruta_audio = os.path.join(ruta_especie, archivos[0])
        mel_spec = audio_a_espectrograma(ruta_audio)

        axes[i].imshow(mel_spec, aspect='auto', origin='lower', cmap='viridis')
        axes[i].set_title(especie.split(' - ')[0], fontsize=9)
        axes[i].axis('off')

    plt.suptitle('Espectrogramas Mel — Ejemplos por especie', fontsize=12)
    plt.tight_layout()
    plt.show()

# ── EJECUTAR ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("Verificando ejemplos antes de generar todo...\n")
    visualizar_ejemplos(RUTA_BASE, n=3)

    print("\nGenerando dataset completo de espectrogramas...")
    generar_dataset_espectrogramas(RUTA_BASE, RUTA_SPECTRO)