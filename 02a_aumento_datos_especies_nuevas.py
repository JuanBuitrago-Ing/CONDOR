import os
import numpy as np
import librosa
import soundfile as sf

RUTA_BASE = '/content/drive/MyDrive/PROYECTO IA/AUDIOS_MOD_AVES'
SR = 22050

# Solo las 13 nuevas
ESPECIES_NUEVAS = [
    'Bichofué', 'Canario de los llanos', 'Gallito de ciénaga',
    'Garrapatero', 'Gavilán caminero', 'Golondrina común',
    'Loro real', 'Perico aliamarillo', 'Tangara azuleja',
    'Tangara palma', 'Tortolita colorada', 'Trepatroncos', 'Turpial'
]

def augmentar(y, sr):
    return [
        librosa.effects.pitch_shift(y, sr=sr, n_steps=2),
        librosa.effects.pitch_shift(y, sr=sr, n_steps=-2),
        librosa.effects.time_stretch(y, rate=1.1),
        librosa.effects.time_stretch(y, rate=0.9),
        y + 0.005 * np.random.randn(len(y)),
        np.roll(y, sr // 2),
    ]

sufijos = ['ps+2','ps-2','ts+','ts-','noise','shift']

print("Augmentando 13 especies nuevas...\n")
resumen = {}

for especie in ESPECIES_NUEVAS:

    ruta_esp = os.path.join(RUTA_BASE, especie)
    if not os.path.isdir(ruta_esp):
        print(f"  ✗ No encontrada: {especie}")
        continue

    # Solo archivos originales (sin _aug en el nombre)
    originales = [f for f in os.listdir(ruta_esp)
                  if f.endswith('.wav') and '_aug_' not in f]

    generados = 0
    for archivo in originales:
        y, sr = librosa.load(os.path.join(ruta_esp, archivo), sr=SR, mono=True)
        nombre_base = os.path.splitext(archivo)[0]

        for variante, sufijo in zip(augmentar(y, sr), sufijos):
            # Ajustar longitud a 10 segundos
            longitud = SR * 10
            if len(variante) > longitud:
                variante = variante[:longitud]
            elif len(variante) < longitud:
                variante = np.pad(variante, (0, longitud - len(variante)))

            nombre_out = f"{nombre_base}_aug_{sufijo}.wav"
            ruta_out   = os.path.join(ruta_esp, nombre_out)

            if not os.path.exists(ruta_out):
                sf.write(ruta_out, variante, SR)
                generados += 1

    total = len(os.listdir(ruta_esp))
    resumen[especie] = total
    print(f"  ✓ {especie}: {len(originales)} originales → {total} totales")


print(f"\n{'='*55}")
print("RESUMEN:")
for esp, n in resumen.items():
    print(f"  {esp:<40} {n} audios")
print(f"{'='*55}")