# ============================================================
# MODELO AVES v3 - Bug corregido + Features mejoradas
# ============================================================
import os
import numpy as np
import pandas as pd
import librosa
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report
import joblib
from google.colab import drive

drive.mount('/content/drive')

RUTA_BASE   = '/content/drive/MyDrive/PROYECTO IA/AUDIOS_MOD_AVES'
RUTA_MODELO = '/content/drive/MyDrive/PROYECTO IA/MODELO_3'

# ── Procesador de audio ──────────────────────────────────────
class AudioProcesador:
    def __init__(self, sr=22050, duration=5):
        self.sr = sr
        self.duration = duration

    def extraer_caracteristicas(self, archivo_audio):
        try:
            y, sr = librosa.load(archivo_audio, duration=self.duration, sr=self.sr)
            features = []


            # 1. MFCCs (26 features)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            for mfcc in mfccs:
                features.append(mfcc.mean())
                features.append(mfcc.std())

            # 2. Chroma - relación entre notas musicales (24 features)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            for c in chroma:
                features.append(c.mean())
                features.append(c.std())

            # 3. Spectral Contrast - diferencia entre picos y valles (14 features)
            contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            for c in contrast:
                features.append(c.mean())
                features.append(c.std())

            # 4. Zero Crossing Rate - cuántas veces la señal cruza el cero (2 features)
            zcr = librosa.feature.zero_crossing_rate(y)
            features.append(zcr.mean())
            features.append(zcr.std())

            # 5. Spectral Rolloff - hasta qué frecuencia está el 85% de la energía (2 features)
            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            features.append(rolloff.mean())
            features.append(rolloff.std())

            # 6. RMS Energy - energía del sonido (2 features)
            rms = librosa.feature.rms(y=y)
            features.append(rms.mean())

            features.append(rms.std())

            # Total: 70 features
            return np.array(features)

        except Exception as e:
            print(f"  Error procesando {archivo_audio}: {str(e)}")
            return None

# ── Modelo ───────────────────────────────────────────────────
class ModeloAves:
    def __init__(self):
        self.procesador = AudioProcesador()
        self.scaler     = StandardScaler()
        self.le         = LabelEncoder()
        self.modelo     = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=4,
            min_samples_leaf=2,
            n_jobs=-1,
            random_state=42
        )
        self.clases = None

    def preparar_datos(self, ruta_base):
        print("Preparando datos...\n")
        caracteristicas, etiquetas = [], []

        for especie in sorted(os.listdir(ruta_base)):
            ruta_especie = os.path.join(ruta_base, especie)
            if not os.path.isdir(ruta_especie):

                continue

            archivos = [f for f in os.listdir(ruta_especie) if f.endswith('.wav')]
            print(f"  {especie}: {len(archivos)} archivos")

            for archivo in archivos:
                ruta_archivo = os.path.join(ruta_especie, archivo)
                features = self.procesador.extraer_caracteristicas(ruta_archivo)
                if features is not None:
                    caracteristicas.append(features)
                    etiquetas.append(especie)

        print(f"\nTotal muestras: {len(etiquetas)}")
        return np.array(caracteristicas), np.array(etiquetas)

    def entrenar(self, ruta_base):
        inicio = datetime.now()

        # Preparar datos
        X, y_raw = self.preparar_datos(ruta_base)
        y = self.le.fit_transform(y_raw)
        self.clases = self.le.classes_

        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Escalar
        X_train_sc = self.scaler.fit_transform(X_train)
        X_test_sc  = self.scaler.transform(X_test)


        # ── Entrenamiento principal ──────────────────────────
        print("\nEntrenando modelo...")
        self.modelo.fit(X_train_sc, y_train)

        train_acc = self.modelo.score(X_train_sc, y_train)
        test_acc  = self.modelo.score(X_test_sc,  y_test)
        tiempo    = datetime.now() - inicio

        print(f"\n{'='*50}")
        print(f"Precisión entrenamiento : {train_acc:.4f}")
        print(f"Precisión prueba        : {test_acc:.4f}")
        print(f"Tiempo                  : {tiempo}")
        print(f"{'='*50}")

        # ── Validación cruzada (modelo SEPARADO para no corromper el principal) ──
        print("\nValidación cruzada K-Fold (5 folds)...")
        X_scaled = self.scaler.transform(X)
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        scores = []

        for fold, (train_idx, val_idx) in enumerate(kf.split(X_scaled), 1):
            modelo_fold = RandomForestClassifier(
                n_estimators=200, max_depth=10,
                min_samples_split=4, min_samples_leaf=2,
                n_jobs=-1, random_state=42
            )
            modelo_fold.fit(X_scaled[train_idx], y[train_idx])
            score = modelo_fold.score(X_scaled[val_idx], y[val_idx])
            scores.append(score)
            print(f"  Fold {fold}: {score:.4f}")

        print(f"\nPrecisión media CV: {np.mean(scores):.4f} ± {np.std(scores):.4f}")


        # ── Métricas reales (con self.modelo intacto) ────────
        y_pred = self.modelo.predict(X_test_sc)

        print("\nReporte de clasificación:")
        print(classification_report(y_test, y_pred, target_names=self.clases))

        # Matriz de confusión
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(12, 10))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=self.clases, yticklabels=self.clases)
        plt.title('Matriz de Confusión - Modelo v3')
        plt.ylabel('Etiqueta Real')
        plt.xlabel('Predicción')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=45)
        plt.tight_layout()
        plt.show()

        # Importancia de features
        self._graficar_features()

    def _graficar_features(self):
        nombres = (
            [f'mfcc_mean_{i}' for i in range(13)] +
            [f'mfcc_std_{i}'  for i in range(13)] +
            [f'chroma_mean_{i}' for i in range(12)] +
            [f'chroma_std_{i}'  for i in range(12)] +
            [f'contrast_mean_{i}' for i in range(7)] +
            [f'contrast_std_{i}'  for i in range(7)] +
            ['zcr_mean', 'zcr_std', 'rolloff_mean', 'rolloff_std', 'rms_mean', 'rms_std']

        )
        importancias = self.modelo.feature_importances_
        idx = np.argsort(importancias)[-20:]  # Top 20

        plt.figure(figsize=(10, 8))
        plt.barh([nombres[i] for i in idx], importancias[idx], color='steelblue')
        plt.title('Top 20 Features más importantes')
        plt.tight_layout()
        plt.show()

    def guardar_modelo(self, ruta_modelo):
        os.makedirs(ruta_modelo, exist_ok=True)
        joblib.dump(self.modelo,  os.path.join(ruta_modelo, 'modelo.joblib'))
        joblib.dump(self.scaler,  os.path.join(ruta_modelo, 'scaler.joblib'))
        joblib.dump(self.le,      os.path.join(ruta_modelo, 'label_encoder.joblib'))
        print(f"\nModelo guardado en: {ruta_modelo}")

# ── Ejecutar ─────────────────────────────────────────────────
if __name__ == "__main__":
    modelo = ModeloAves()
    modelo.entrenar(RUTA_BASE)
    modelo.guardar_modelo(RUTA_MODELO)