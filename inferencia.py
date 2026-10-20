import os, io, time, joblib
import numpy as np
import sounddevice as sd
import librosa
from datetime import datetime
from tensorflow import keras
from PIL import Image
import matplotlib.pyplot as plt

DEVICE   = 2
SR_CAM   = 32000
SR_MODEL = 22050
DURACION = 10
UMBRAL   = 0.02
TOP_N    = 3

RUTA_CNN = '/home/juan/sistema_aves/modelos/CNN'
RUTA_RF  = '/home/juan/sistema_aves/modelos/RF'
RUTA_LOG = '/home/juan/sistema_aves/detecciones.log'

print("Cargando modelos...")
modelo_cnn = keras.models.load_model(f'{RUTA_CNN}/modelo_cnn.keras')
le_cnn     = joblib.load(f'{RUTA_CNN}/label_encoder_cnn.joblib')
modelo_rf  = joblib.load(f'{RUTA_RF}/modelo.joblib')
scaler_rf  = joblib.load(f'{RUTA_RF}/scaler.joblib')
le_rf      = joblib.load(f'{RUTA_RF}/label_encoder.joblib')
print("Modelos cargados\n")

def grabar_audio():
    audio = sd.rec(int(DURACION * SR_CAM), samplerate=SR_CAM, channels=1, dtype='float32', device=DEVICE)
    sd.wait()
    return librosa.resample(audio.flatten(), orig_sr=SR_CAM, target_sr=SR_MODEL)


def hay_sonido(audio):
    return np.abs(audio).max() > UMBRAL

def audio_a_espectrograma(audio):
    longitud = SR_MODEL * DURACION
    if len(audio) < longitud:
        audio = np.pad(audio, (0, longitud - len(audio)))
    mel      = librosa.feature.melspectrogram(y=audio, sr=SR_MODEL, n_mels=128, hop_length=512, n_fft=2048)
    mel_db   = librosa.power_to_db(mel, ref=np.max)
    mel_norm = (mel_db - mel_db.min()) / (mel_db.max() - mel_db.min())
    fig, ax  = plt.subplots(figsize=(1.28, 1.28), dpi=100)
    ax.imshow(mel_norm, aspect='auto', origin='lower', cmap='viridis')
    ax.axis('off')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    buf.seek(0)
    img = Image.open(buf).convert('RGB').resize((128, 128))
    return np.expand_dims(np.array(img) / 255.0, axis=0)

def audio_a_features_rf(audio):
    longitud = SR_MODEL * DURACION
    if len(audio) < longitud:
        audio = np.pad(audio, (0, longitud - len(audio)))
    features = []
    mfccs = librosa.feature.mfcc(y=audio, sr=SR_MODEL, n_mfcc=13)
    for mfcc in mfccs:
        features += [mfcc.mean(), mfcc.std()]
    chroma = librosa.feature.chroma_stft(y=audio, sr=SR_MODEL)
    for c in chroma:

        features += [c.mean(), c.std()]
    contrast = librosa.feature.spectral_contrast(y=audio, sr=SR_MODEL)
    for c in contrast:
        features += [c.mean(), c.std()]
    zcr     = librosa.feature.zero_crossing_rate(audio)
    rolloff = librosa.feature.spectral_rolloff(y=audio, sr=SR_MODEL)
    rms     = librosa.feature.rms(y=audio)
    features += [zcr.mean(), zcr.std(), rolloff.mean(), rolloff.std(), rms.mean(), rms.std()]
    return scaler_rf.transform([np.array(features)])

def predecir(audio):
    probs_cnn = modelo_cnn.predict(audio_a_espectrograma(audio), verbose=0)[0]
    idx_cnn   = np.argsort(probs_cnn)[::-1][:TOP_N]
    probs_rf  = modelo_rf.predict_proba(audio_a_features_rf(audio))[0]
    idx_rf    = np.argsort(probs_rf)[::-1][:TOP_N]
    return probs_cnn, idx_cnn, probs_rf, idx_rf

def guardar_log(esp_cnn, conf_cnn, esp_rf, conf_rf):
    hora  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    linea = f"{hora} | CNN: {esp_cnn} ({conf_cnn:.1f}%) | RF: {esp_rf} ({conf_rf:.1f}%)\n"
    with open(RUTA_LOG, 'a') as f:
        f.write(linea)

def mostrar_resultado(probs_cnn, idx_cnn, probs_rf, idx_rf):
    print(f"\n{'='*55}")
    print(f"  {datetime.now().strftime('%H:%M:%S')} - DETECCION")
    print(f"{'='*55}")
    print("\n  CNN - Transfer Learning:")
    for i, idx in enumerate(idx_cnn):
        nombre = le_cnn.inverse_transform([idx])[0].split(' - ')[0]
        prob   = probs_cnn[idx] * 100
        barra  = 'X' * int(prob / 5) + '.' * (20 - int(prob / 5))

        print(f"  {i+1}. {nombre:<35} {prob:5.1f}%  [{barra}]")
    print("\n  Random Forest:")
    for i, idx in enumerate(idx_rf):
        nombre = le_rf.inverse_transform([idx])[0].split(' - ')[0]
        prob   = probs_rf[idx] * 100
        barra  = 'X' * int(prob / 5) + '.' * (20 - int(prob / 5))
        print(f"  {i+1}. {nombre:<35} {prob:5.1f}%  [{barra}]")
    esp_cnn = le_cnn.inverse_transform([idx_cnn[0]])[0].split(' - ')[0]
    esp_rf  = le_rf.inverse_transform([idx_rf[0]])[0].split(' - ')[0]
    print()
    if esp_cnn == esp_rf:
        print(f"  COINCIDEN: {esp_cnn}")
    else:
        print(f"  CNN: {esp_cnn} | RF: {esp_rf}")
    print(f"{'='*55}\n")
    return esp_cnn, probs_cnn[idx_cnn[0]]*100, esp_rf, probs_rf[idx_rf[0]]*100

print("Sistema iniciado - escuchando...\n")
print("Ctrl+C para detener\n")

try:
    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Grabando {DURACION} segundos...")
        audio = grabar_audio()
        if not hay_sonido(audio):
            print("  Sin sonido relevante, esperando...\n")
            continue
        print("  Sonido detectado - procesando...")
        probs_cnn, idx_cnn, probs_rf, idx_rf = predecir(audio)
        esp_cnn, conf_cnn, esp_rf, conf_rf = mostrar_resultado(probs_cnn, idx_cnn, probs_rf, idx_rf)
        guardar_log(esp_cnn, conf_cnn, esp_rf, conf_rf)
except KeyboardInterrupt:

    print("\nSistema detenido.")