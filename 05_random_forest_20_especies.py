# ============================================================
# MODELO v3 — Random Forest — 20 especies
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
    def __init__(self, sr=22050, duration=10):
        self.sr       = sr
        self.duration = duration

    def extraer_caracteristicas(self, archivo_audio):
        try:
            y, sr = librosa.load(archivo_audio, duration=self.duration, sr=self.sr, mono=True)
            features = []


            # MFCCs (26)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            for mfcc in mfccs:
                features.append(mfcc.mean())
                features.append(mfcc.std())

            # Chroma (24)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            for c in chroma:
                features.append(c.mean())
                features.append(c.std())

            # Spectral Contrast (14)
            contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            for c in contrast:
                features.append(c.mean())
                features.append(c.std())

            # ZCR (2)
            zcr = librosa.feature.zero_crossing_rate(y)
            features.append(zcr.mean())
            features.append(zcr.std())

            # Rolloff (2)
            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            features.append(rolloff.mean())
            features.append(rolloff.std())

            # RMS (2)
            rms = librosa.feature.rms(y=y)
            features.append(rms.mean())

            features.append(rms.std())

            return np.array(features)  # 70 features

        except Exception as e:
            print(f"  Error: {archivo_audio}: {e}")
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
                features = self.procesador.extraer_caracteristicas(
                    os.path.join(ruta_especie, archivo)
                )
                if features is not None:
                    caracteristicas.append(features)
                    etiquetas.append(especie)

        print(f"\nTotal muestras: {len(etiquetas)}")
        return np.array(caracteristicas), np.array(etiquetas)

    def entrenar(self, ruta_base):
        inicio = datetime.now()
        X, y_raw = self.preparar_datos(ruta_base)
        y = self.le.fit_transform(y_raw)
        self.clases = self.le.classes_

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        X_train_sc = self.scaler.fit_transform(X_train)
        X_test_sc  = self.scaler.transform(X_test)

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

        # Validación cruzada con modelo separado
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

        # Métricas reales
        y_pred = self.modelo.predict(X_test_sc)
        nombres_cortos = [c.split(' - ')[0] for c in self.clases]


        print("\nReporte de clasificación:")
        print(classification_report(y_test, y_pred, target_names=nombres_cortos))

        # Matriz de confusión
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(16, 14))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=nombres_cortos,
                    yticklabels=nombres_cortos)
        plt.title('Matriz de Confusión — Modelo v3 (20 especies)')
        plt.ylabel('Real')
        plt.xlabel('Predicción')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

    def guardar_modelo(self, ruta_modelo):
        os.makedirs(ruta_modelo, exist_ok=True)
        joblib.dump(self.modelo, os.path.join(ruta_modelo, 'modelo.joblib'))
        joblib.dump(self.scaler, os.path.join(ruta_modelo, 'scaler.joblib'))
        joblib.dump(self.le,     os.path.join(ruta_modelo, 'label_encoder.joblib'))
        print(f"\nModelo guardado en: {ruta_modelo}")

# ── Ejecutar ─────────────────────────────────────────────────
modelo = ModeloAves()
modelo.entrenar(RUTA_BASE)
modelo.guardar_modelo(RUTA_MODELO)