import os
import random
import numpy as np
import librosa
import soundfile as sf

RUTA_BASE = '/content/drive/MyDrive/PROYECTO IA/AUDIOS_MOD_AVES'
SR        = 22050
META      = 840  # audios por especie

# ── 1. Recortar Bichofué a 840 ────────────────────────────────
print("Paso 1 — Recortando Bichofué...")
ruta_bicho = os.path.join(RUTA_BASE, 'Bichofué')
archivos   = [f for f in os.listdir(ruta_bicho) if f.endswith('.wav')]

if len(archivos) > META:
    # Conservar originales, eliminar exceso de augmentados
    originales = [f for f in archivos if '_aug_' not in f]
    augmentados = [f for f in archivos if '_aug_' in f]
    random.shuffle(augmentados)
    eliminar = augmentados[:len(archivos) - META]
    for f in eliminar:
        os.remove(os.path.join(ruta_bicho, f))
    print(f"  Eliminados {len(eliminar)} archivos aug — quedan {META}")
else:
    print(f"  Ya tiene {len(archivos)} audios — OK")

# ── 2. Augmentar las 7 originales hasta ~840 ─────────────────
print("\nPaso 2 — Augmentando 7 especies originales hasta 840...")

ESPECIES_ORIGINALES = [
    'Amazilia de vientre blanco - Chrysuronia versicolor',

    'Golondrina de muslos blancos - Atticora tibialis',
    'Gorrión Pectoral - Arremon taciturnus',
    'Mango gorjinegro - Anthracothorax nigricollis',
    'Mosquerito ojiblanco - Atalotriccus pilaris',
    'Tecolote llanero - Athene cunicularia',
    'Urraca violácea - Cyanocorax violaceus',
]

TRANSFORMACIONES = [
    ('ps+2',  lambda y: librosa.effects.pitch_shift(y, sr=SR, n_steps=2)),
    ('ps-2',  lambda y: librosa.effects.pitch_shift(y, sr=SR, n_steps=-2)),
    ('ts+',   lambda y: librosa.effects.time_stretch(y, rate=1.1)),
    ('ts-',   lambda y: librosa.effects.time_stretch(y, rate=0.9)),
    ('noise', lambda y: y + 0.005 * np.random.randn(len(y))),
    ('shift', lambda y: np.roll(y, SR // 2)),
    ('ps+1',  lambda y: librosa.effects.pitch_shift(y, sr=SR, n_steps=1)),
    ('ps-1',  lambda y: librosa.effects.pitch_shift(y, sr=SR, n_steps=-1)),
    ('ts++',  lambda y: librosa.effects.time_stretch(y, rate=1.2)),
    ('ts--',  lambda y: librosa.effects.time_stretch(y, rate=0.8)),
]

def ajustar_longitud(y, longitud=SR*10):
    if len(y) > longitud:
        return y[:longitud]
    return np.pad(y, (0, longitud - len(y)))

for especie in ESPECIES_ORIGINALES:
    ruta_esp = os.path.join(RUTA_BASE, especie)
    if not os.path.isdir(ruta_esp):
        print(f"  ✗ No encontrada: {especie}")
        continue


    actuales   = [f for f in os.listdir(ruta_esp) if f.endswith('.wav')]
    originales = [f for f in actuales if '_aug_' not in f]
    faltantes  = META - len(actuales)

    if faltantes <= 0:
        print(f"  ✓ {especie.split(' - ')[0]}: ya tiene {len(actuales)} audios")
        continue

    print(f"  {especie.split(' - ')[0]}: {len(actuales)} → necesita {faltantes} más")
    generados = 0

    # Ciclar por originales y transformaciones hasta llegar a META
    idx_orig  = 0
    idx_trans = 0

    while generados < faltantes:
        archivo = originales[idx_orig % len(originales)]
        sufijo, fn = TRANSFORMACIONES[idx_trans % len(TRANSFORMACIONES)]

        nombre_base = os.path.splitext(archivo)[0]
        nombre_out  = f"{nombre_base}_aug_{sufijo}_{generados:04d}.wav"
        ruta_out    = os.path.join(ruta_esp, nombre_out)

        if not os.path.exists(ruta_out):
            try:
                y, _ = librosa.load(os.path.join(ruta_esp, archivo), sr=SR, mono=True)
                variante = ajustar_longitud(fn(y))
                sf.write(ruta_out, variante, SR)
                generados += 1
            except:
                pass


        idx_orig  += 1
        idx_trans += 1

    total = len(os.listdir(ruta_esp))
    print(f"    → {total} audios totales")

# ── 3. Resumen final ──────────────────────────────────────────
print(f"\n{'='*55}")
print("RESUMEN FINAL — audios por especie:")
total_general = 0
for especie in sorted(os.listdir(RUTA_BASE)):
    ruta_esp = os.path.join(RUTA_BASE, especie)
    if not os.path.isdir(ruta_esp):
        continue
    n = len([f for f in os.listdir(ruta_esp) if f.endswith('.wav')])
    total_general += n
    estado = "✅" if 780 <= n <= 900 else "⚠️"
    print(f"  {estado} {especie:<45} {n} audios")
print(f"\nTOTAL: {total_general} audios en 20 especies")
print(f"{'='*55}")