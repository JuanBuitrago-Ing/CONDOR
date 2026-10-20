# ============================================================
# PASO 2 v2 — CNN con Transfer Learning (MobileNetV2)
# ============================================================
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import joblib

RUTA_SPECTRO = '/content/drive/MyDrive/PROYECTO IA/ESPECTROGRAMAS'
RUTA_MODELO  = '/content/drive/MyDrive/PROYECTO IA/MODELO_CNN'

IMG_SIZE = (128, 128)
BATCH    = 16
SEED     = 42

# ── 1. Cargar imágenes ───────────────────────────────────────
def cargar_dataset(ruta_base):
    print("Cargando espectrogramas...\n")
    from tensorflow.keras.preprocessing.image import load_img, img_to_array
    imagenes, etiquetas = [], []

    for especie in sorted(os.listdir(ruta_base)):

        ruta_especie = os.path.join(ruta_base, especie)
        if not os.path.isdir(ruta_especie):
            continue
        archivos = [f for f in os.listdir(ruta_especie) if f.endswith('.png')]
        print(f"  {especie}: {len(archivos)} imágenes")
        for archivo in archivos:
            img = load_img(os.path.join(ruta_especie, archivo),
                           target_size=IMG_SIZE, color_mode='rgb')
            arr = img_to_array(img) / 255.0
            imagenes.append(arr)
            etiquetas.append(especie)

    print(f"\nTotal: {len(imagenes)} imágenes")
    return np.array(imagenes), np.array(etiquetas)

X, y_raw = cargar_dataset(RUTA_SPECTRO)

le      = LabelEncoder()
y       = le.fit_transform(y_raw)
clases  = le.classes_
N_CLASES = len(clases)
nombres_cortos = [c.split(' - ')[0] for c in clases]

print(f"Clases ({N_CLASES}): {nombres_cortos}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=SEED, stratify=y
)
print(f"Train: {len(X_train)}  |  Test: {len(X_test)}\n")

# ── 2. Augmentación ──────────────────────────────────────────
data_aug = keras.Sequential([

    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.05),
    layers.RandomZoom(0.1),
    layers.RandomContrast(0.1),
], name="augmentacion")

# ── 3. Modelo con Transfer Learning (MobileNetV2) ────────────
def construir_modelo_transfer(n_clases):
    # Base preentrenada en ImageNet — congelada inicialmente
    base = MobileNetV2(
        input_shape=(128, 128, 3),
        include_top=False,
        weights='imagenet'
    )
    base.trainable = False  # Fase 1: solo entrenar capas nuevas

    inputs = keras.Input(shape=(128, 128, 3))
    x = data_aug(inputs)
    x = base(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(n_clases, activation='softmax')(x)

    return keras.Model(inputs, outputs), base

modelo, base_model = construir_modelo_transfer(N_CLASES)
modelo.summary()

# ── 4. FASE 1 — Entrenar solo capas nuevas (10 epochs) ───────

print("\n== FASE 1: Entrenando capas nuevas (base congelada) ==\n")

modelo.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

callbacks_fase1 = [
    EarlyStopping(monitor='val_accuracy', patience=8,
                  restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                      patience=4, min_lr=1e-6, verbose=1)
]

inicio = datetime.now()
hist1 = modelo.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=20,
    batch_size=BATCH,
    callbacks=callbacks_fase1,
    verbose=1
)

# ── 5. FASE 2 — Fine-tuning (descongelar últimas capas) ───────
print("\n== FASE 2: Fine-tuning (últimas 30 capas descongeladas) ==\n")

base_model.trainable = True

# Congelar todo excepto las últimas 30 capas
for layer in base_model.layers[:-30]:

    layer.trainable = False

# Learning rate mucho más bajo para no destruir los pesos preentrenados
modelo.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-4),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

callbacks_fase2 = [
    EarlyStopping(monitor='val_accuracy', patience=10,
                  restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                      patience=5, min_lr=1e-7, verbose=1)
]

hist2 = modelo.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=30,
    batch_size=BATCH,
    callbacks=callbacks_fase2,
    verbose=1
)

tiempo = datetime.now() - inicio
print(f"\nTiempo total: {tiempo}")

# ── 6. Evaluación ────────────────────────────────────────────
loss, acc = modelo.evaluate(X_test, y_test, verbose=0)
print(f"\nPrecisión en test: {acc:.4f}")
print(f"Loss en test:      {loss:.4f}")


# Curvas (unir fase 1 y fase 2)
acc_total  = hist1.history['accuracy']     + hist2.history['accuracy']
val_total  = hist1.history['val_accuracy'] + hist2.history['val_accuracy']
loss_total = hist1.history['loss']         + hist2.history['loss']
vloss_total= hist1.history['val_loss']     + hist2.history['val_loss']
sep_epoch  = len(hist1.history['accuracy'])  # línea divisoria fase 1 / fase 2

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for ax, train, val, title in zip(
    axes,
    [acc_total, loss_total],
    [val_total, vloss_total],
    ['Precisión por Epoch', 'Loss por Epoch']
):
    ax.plot(train, label='Train',      color='#00A896')
    ax.plot(val,   label='Validación', color='#F4A261')
    ax.axvline(x=sep_epoch, color='gray', linestyle='--',
               linewidth=1, label='Fine-tuning inicia')
    ax.set_title(title)
    ax.set_xlabel('Epoch')
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Matriz de confusión
y_pred = np.argmax(modelo.predict(X_test), axis=1)

cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=nombres_cortos,
            yticklabels=nombres_cortos)
plt.title('Matriz de Confusión — CNN Transfer Learning')
plt.ylabel('Real')
plt.xlabel('Predicción')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

print("\nReporte de clasificación:")
print(classification_report(y_test, y_pred, target_names=nombres_cortos))

# ── 7. Guardar ───────────────────────────────────────────────
os.makedirs(RUTA_MODELO, exist_ok=True)
modelo.save(os.path.join(RUTA_MODELO, 'modelo_cnn.keras'))
joblib.dump(le, os.path.join(RUTA_MODELO, 'label_encoder_cnn.joblib'))
print(f"\nModelo guardado en: {RUTA_MODELO}")

# ── 8. Función Shazam corregida ──────────────────────────────
def espectrograma_a_array(ruta_audio):
    import librosa, io
    from PIL import Image

    y_audio, sr = librosa.load(ruta_audio, sr=22050, duration=10, mono=True)
    longitud = 22050 * 10
    if len(y_audio) < longitud:
        y_audio = np.pad(y_audio, (0, longitud - len(y_audio)))

    mel = librosa.feature.melspectrogram(
        y=y_audio, sr=sr, n_mels=128, hop_length=512, n_fft=2048

    )
    mel_db   = librosa.power_to_db(mel, ref=np.max)
    mel_norm = (mel_db - mel_db.min()) / (mel_db.max() - mel_db.min())

    # Guardar en buffer en vez de canvas (compatible con Python 3.12)
    fig, ax = plt.subplots(figsize=(1.28, 1.28), dpi=100)
    ax.imshow(mel_norm, aspect='auto', origin='lower', cmap='viridis')
    ax.axis('off')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    buf.seek(0)

    img = Image.open(buf).convert('RGB').resize((128, 128))
    arr = np.array(img) / 255.0
    return np.expand_dims(arr, axis=0)

def identificar_ave(ruta_audio, modelo, label_encoder, top_n=3):
    img_arr = espectrograma_a_array(ruta_audio)
    probs   = modelo.predict(img_arr, verbose=0)[0]
    indices = np.argsort(probs)[::-1][:top_n]

    print(f"\n{'='*50}")
    print("  IDENTIFICACIÓN DE AVE — Resultado")
    print(f"{'='*50}")
    for i, idx in enumerate(indices):
        especie = label_encoder.inverse_transform([idx])[0]
        nombre  = especie.split(' - ')[0]
        prob    = probs[idx] * 100
        barra   = '█' * int(prob / 5)

        print(f"  {i+1}. {nombre:<35} {prob:5.1f}%  {barra}")
    print(f"{'='*50}\n")

    return [(label_encoder.inverse_transform([idx])[0], float(probs[idx]))
            for idx in indices]

# ── Prueba Shazam ────────────────────────────────────────────
print("\nPrueba tipo Shazam:")
especie_prueba  = sorted(os.listdir(RUTA_SPECTRO))[0]
ruta_audio_base = RUTA_SPECTRO.replace('ESPECTROGRAMAS', 'AUDIOS_MOD_AVES')
primer_audio    = sorted(os.listdir(os.path.join(ruta_audio_base, especie_prueba)))[0]
ruta_prueba     = os.path.join(ruta_audio_base, especie_prueba, primer_audio)

print(f"Audio de prueba: {especie_prueba}")
identificar_ave(ruta_prueba, modelo, le, top_n=3)