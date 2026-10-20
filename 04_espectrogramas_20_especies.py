# ============================================================
# PASO 1 — Generar espectrogramas (20 especies, ~16,625 audios)
# ============================================================
import os
import numpy as np
import librosa
import matplotlib.pyplot as plt
from google.colab import drive

drive.mount('/content/drive')

RUTA_BASE    = '/content/drive/MyDrive/PROYECTO IA/AUDIOS_MOD_AVES'
RUTA_SPECTRO = '/content/drive/MyDrive/PROYECTO IA/ESPECTROGRAMAS'

SR      = 22050
DURACION= 10
N_MELS  = 128
HOP_LEN = 512
N_FFT   = 2048

os.makedirs(RUTA_SPECTRO, exist_ok=True)

def audio_a_espectrograma(ruta_audio):
    y, sr = librosa.load(ruta_audio, sr=SR, duration=DURACION, mono=True)
    longitud = SR * DURACION
    if len(y) < longitud:
        y = np.pad(y, (0, longitud - len(y)))
    mel      = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=N_MELS, hop_length=HOP_LEN, n_fft=N_FFT)
    mel_db   = librosa.power_to_db(mel, ref=np.max)
    mel_norm = (mel_db - mel_db.min()) / (mel_db.max() - mel_db.min())
    return mel_norm


def guardar_espectrograma(mel_spec, ruta_salida):
    fig, ax = plt.subplots(figsize=(1.28, 1.28), dpi=100)
    ax.imshow(mel_spec, aspect='auto', origin='lower', cmap='viridis')
    ax.axis('off')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(ruta_salida, bbox_inches='tight', pad_inches=0)
    plt.close()

print("Generando espectrogramas...\n")
resumen = {}
total   = 0

for especie in sorted(os.listdir(RUTA_BASE)):
    ruta_especie = os.path.join(RUTA_BASE, especie)
    if not os.path.isdir(ruta_especie):
        continue

    ruta_out = os.path.join(RUTA_SPECTRO, especie)
    os.makedirs(ruta_out, exist_ok=True)

    archivos    = [f for f in os.listdir(ruta_especie) if f.endswith('.wav')]
    procesados  = 0
    saltados    = 0

    for archivo in archivos:
        nombre_png = os.path.splitext(archivo)[0] + '.png'
        ruta_png   = os.path.join(ruta_out, nombre_png)

        if os.path.exists(ruta_png):
            saltados += 1
            procesados += 1
            continue


        try:
            mel = audio_a_espectrograma(os.path.join(ruta_especie, archivo))
            guardar_espectrograma(mel, ruta_png)
            procesados += 1
        except Exception as e:
            print(f"  Error {archivo}: {e}")

    resumen[especie] = procesados
    total += procesados
    print(f"  ✓ {especie:<45} {procesados} espectrogramas ({saltados} ya existían)")

print(f"\n{'='*55}")
print(f"TOTAL: {total} espectrogramas")
print(f"Guardados en: {RUTA_SPECTRO}")