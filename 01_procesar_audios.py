import os
import librosa
import soundfile as sf
import numpy as np

RUTA_ENTRADA = '/content/drive/MyDrive/PROYECTO IA/SONIDOS_AVES'
RUTA_SALIDA  = '/content/drive/MyDrive/PROYECTO IA/AUDIOS_MOD_AVES'
SR           = 22050
DURACION     = 10

def normalizar(audio):
    maximo = np.abs(audio).max()
    if maximo > 0:
        return audio * (0.708 / maximo)
    return audio

def procesar_especie(ruta_especie, nombre_especie):
    ruta_out = os.path.join(RUTA_SALIDA, nombre_especie)
    os.makedirs(ruta_out, exist_ok=True)

    archivos = [f for f in os.listdir(ruta_especie)
                if f.lower().endswith(('.wav','.mp3','.flac','.ogg'))]

    print(f"\n{nombre_especie}: {len(archivos)} archivos")
    segmentos_total = 0

    for archivo in archivos:
        ruta_archivo = os.path.join(ruta_especie, archivo)
        try:
            y, sr = librosa.load(ruta_archivo, sr=SR, mono=True)
            duracion_total = len(y) / SR
            n_segmentos    = int(duracion_total // DURACION)


            print(f"  {archivo}: {duracion_total:.1f}s → {n_segmentos} segmentos")

            for i in range(n_segmentos):
                inicio   = i * DURACION * SR
                fin      = inicio + DURACION * SR
                segmento = y[int(inicio):int(fin)]

                if np.abs(segmento).max() < 0.01:
                    continue

                segmento     = normalizar(segmento)
                nombre_base  = os.path.splitext(archivo)[0]
                nombre_out   = f"{nombre_base}_seg{i+1:03d}.wav"
                ruta_destino = os.path.join(ruta_out, nombre_out)

                # Saltar si ya existe
                if os.path.exists(ruta_destino):
                    segmentos_total += 1
                    continue

                sf.write(ruta_destino, segmento, SR)
                segmentos_total += 1

        except Exception as e:
            print(f"  Error en {archivo}: {e}")

    print(f"  Segmentos generados: {segmentos_total}")
    return segmentos_total

# ── EJECUTAR ──────────────────────────────────────────────────
print("="*55)

print("Procesando audios...")
print("="*55)

total_general = 0
resumen = {}

for especie in sorted(os.listdir(RUTA_ENTRADA)):
    ruta_especie = os.path.join(RUTA_ENTRADA, especie)
    if not os.path.isdir(ruta_especie):
        continue
    n = procesar_especie(ruta_especie, especie)
    resumen[especie] = n
    total_general += n

print(f"\n{'='*55}")
print("RESUMEN FINAL:")
for esp, n in resumen.items():
    print(f"  {esp:<45} {n} segmentos")
print(f"\nTOTAL AUDIOS GENERADOS: {total_general}")