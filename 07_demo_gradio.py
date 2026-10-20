# ============================================================
# DEMO — Interfaz Gradio tipo Shazam
# ============================================================
!pip install gradio -q

import gradio as gr
import numpy as np
import librosa
import joblib
import io
import matplotlib.pyplot as plt
from PIL import Image
from tensorflow import keras

# ── Cargar modelos ───────────────────────────────────────────
RUTA_CNN = '/content/drive/MyDrive/PROYECTO IA/MODELO_CNN'
RUTA_RF  = '/content/drive/MyDrive/PROYECTO IA/MODELO_3'

print("Cargando modelos...")
modelo_cnn = keras.models.load_model(f'{RUTA_CNN}/modelo_cnn.keras')
le_cnn     = joblib.load(f'{RUTA_CNN}/label_encoder_cnn.joblib')

modelo_rf  = joblib.load(f'{RUTA_RF}/modelo.joblib')
scaler_rf  = joblib.load(f'{RUTA_RF}/scaler.joblib')
le_rf      = joblib.load(f'{RUTA_RF}/label_encoder.joblib')
print("✓ Modelos cargados correctamente\n")

# ── Procesamiento de audio ───────────────────────────────────
SR       = 22050
DURATION = 10

def audio_a_espectrograma_array(ruta_audio):

    y, sr = librosa.load(ruta_audio, sr=SR, duration=DURATION, mono=True)
    longitud = SR * DURATION
    if len(y) < longitud:
        y = np.pad(y, (0, longitud - len(y)))

    mel = librosa.feature.melspectrogram(
        y=y, sr=sr, n_mels=128, hop_length=512, n_fft=2048
    )
    mel_db   = librosa.power_to_db(mel, ref=np.max)
    mel_norm = (mel_db - mel_db.min()) / (mel_db.max() - mel_db.min())

    fig, ax = plt.subplots(figsize=(1.28, 1.28), dpi=100)
    ax.imshow(mel_norm, aspect='auto', origin='lower', cmap='viridis')
    ax.axis('off')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    buf.seek(0)

    img = Image.open(buf).convert('RGB').resize((128, 128))
    return np.array(img) / 255.0

def audio_a_features_rf(ruta_audio):
    y, sr = librosa.load(ruta_audio, sr=SR, duration=DURATION, mono=True)
    features = []

    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    for mfcc in mfccs:
        features += [mfcc.mean(), mfcc.std()]

    chroma = librosa.feature.chroma_stft(y=y, sr=sr)

    for c in chroma:
        features += [c.mean(), c.std()]

    contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    for c in contrast:
        features += [c.mean(), c.std()]

    zcr     = librosa.feature.zero_crossing_rate(y)
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    rms     = librosa.feature.rms(y=y)

    features += [zcr.mean(), zcr.std()]
    features += [rolloff.mean(), rolloff.std()]
    features += [rms.mean(), rms.std()]

    return np.array(features)

# ── Función principal de predicción ─────────────────────────
def identificar_ave(ruta_audio):
    if ruta_audio is None:
        return "⚠️ Por favor sube un archivo de audio WAV.", None

    try:
        # ── CNN ──────────────────────────────────────────────
        img_arr  = audio_a_espectrograma_array(ruta_audio)
        img_input = np.expand_dims(img_arr, axis=0)
        probs_cnn = modelo_cnn.predict(img_input, verbose=0)[0]
        idx_cnn   = np.argsort(probs_cnn)[::-1][:3]

        # ── Random Forest ────────────────────────────────────
        feats     = audio_a_features_rf(ruta_audio)
        feats_sc  = scaler_rf.transform([feats])

        probs_rf  = modelo_rf.predict_proba(feats_sc)[0]
        idx_rf    = np.argsort(probs_rf)[::-1][:3]

        # ── Resultado CNN ─────────────────────────────────────
        resultado_cnn = "### 🤖 CNN — Transfer Learning MobileNetV2\n\n"
        for i, idx in enumerate(idx_cnn):
            especie = le_cnn.inverse_transform([idx])[0]
            nombre  = especie.split(' - ')[0]
            prob    = probs_cnn[idx] * 100
            barra   = '█' * int(prob / 5) + '░' * (20 - int(prob / 5))
            medalla = ["🥇", "🥈", "🥉"][i]
            resultado_cnn += f"{medalla} **{nombre}**\n`{barra}` {prob:.1f}%\n\n"

        # ── Resultado RF ──────────────────────────────────────
        resultado_rf = "### 🌲 Random Forest — 70 Features\n\n"
        for i, idx in enumerate(idx_rf):
            especie = le_rf.inverse_transform([idx])[0]
            nombre  = especie.split(' - ')[0]
            prob    = probs_rf[idx] * 100
            barra   = '█' * int(prob / 5) + '░' * (20 - int(prob / 5))
            medalla = ["🥇", "🥈", "🥉"][i]
            resultado_rf += f"{medalla} **{nombre}**\n`{barra}` {prob:.1f}%\n\n"

        # ── Coincidencia entre modelos ────────────────────────
        especie_cnn = le_cnn.inverse_transform([idx_cnn[0]])[0].split(' - ')[0]
        especie_rf  = le_rf.inverse_transform([idx_rf[0]])[0].split(' - ')[0]

        if especie_cnn == especie_rf:
            acuerdo = f"\n✅ **Ambos modelos coinciden: {especie_cnn}**"
        else:
            acuerdo = f"\n⚠️ Los modelos difieren — CNN: {especie_cnn} | RF: {especie_rf}"


        texto_final = resultado_cnn + "---\n" + resultado_rf + "---\n" + acuerdo

        # ── Gráfica comparativa ───────────────────────────────
        nombres_cnn = [le_cnn.inverse_transform([i])[0].split(' - ')[0]
                       for i in idx_cnn]
        nombres_rf  = [le_rf.inverse_transform([i])[0].split(' - ')[0]
                       for i in idx_rf]

        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        fig.patch.set_facecolor('#0D1B2A')

        for ax, nombres, probs_data, indices, titulo, color in zip(
            axes,
            [nombres_cnn, nombres_rf],
            [probs_cnn, probs_rf],
            [idx_cnn, idx_rf],
            ['CNN — Transfer Learning', 'Random Forest'],
            ['#00A896', '#F4A261']
        ):
            vals = [probs_data[i] * 100 for i in indices]
            bars = ax.barh(nombres[::-1], vals[::-1], color=color, height=0.5)
            ax.set_xlim(0, 100)
            ax.set_xlabel('Probabilidad (%)', color='white')
            ax.set_title(titulo, color='white', fontsize=12, fontweight='bold')
            ax.set_facecolor('#1E3A4C')
            ax.tick_params(colors='white')
            ax.spines[:].set_color('#1E3A4C')
            for bar, val in zip(bars, vals[::-1]):
                ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                        f'{val:.1f}%', va='center', color='white', fontsize=10)

        plt.tight_layout()

        return texto_final, fig

    except Exception as e:
        return f"❌ Error procesando el audio: {str(e)}", None

# ── Interfaz Gradio ──────────────────────────────────────────
with gr.Blocks(title="🐦 Identificador de Aves", theme=gr.themes.Base()) as demo:

    gr.Markdown("""
    # 🐦 Sistema de Identificación de Aves por Sonido
    ### Universidad de los Llanos · Ingeniería Electrónica
    Sube un archivo WAV de canto de ave y el sistema mostrará las especies
    más probables usando dos modelos de IA en paralelo.
    """)

    with gr.Row():
        audio_input = gr.Audio(
            label="🎙️ Audio del canto de ave (.WAV)",
            type="filepath"
        )

    btn = gr.Button("🔍 Identificar Ave", variant="primary", size="lg")

    with gr.Row():
        resultado_texto = gr.Markdown(label="Resultado")

    grafica = gr.Plot(label="Comparativa de probabilidades")

    btn.click(
        fn=identificar_ave,
        inputs=audio_input,
        outputs=[resultado_texto, grafica]

    )

    gr.Markdown("""
    ---
    **Especies que el sistema puede identificar:**
    Amazilia de vientre blanco · Golondrina de muslos blancos · Gorrión Pectoral ·
    Mango gorjinegro · Mosquerito ojiblanco · Tecolote llanero · Urraca violácea
    """)

demo.launch(share=True, debug=False)