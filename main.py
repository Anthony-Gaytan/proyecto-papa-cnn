import json
import os
import random
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    classification_report,
    confusion_matrix,
)
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.layers import Conv2D, Dense, Dropout, Flatten, MaxPooling2D
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.image import ImageDataGenerator


DATASET_DIR = Path("dataset")
DATASET_SPLIT_DIR = Path("dataset_split")
RESULTADOS_DIR = Path("resultados")

SEED = 42
TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.15
TEST_RATIO = 0.15

img_size = (224, 224)
batch_size = 32
epochs = 10


def configurar_reproducibilidad(seed):
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


def crear_dataset_split():
    if not DATASET_DIR.exists():
        raise FileNotFoundError(f"No existe la carpeta del dataset: {DATASET_DIR}")

    if DATASET_SPLIT_DIR.exists():
        shutil.rmtree(DATASET_SPLIT_DIR)

    clases = sorted(
        carpeta.name
        for carpeta in DATASET_DIR.iterdir()
        if carpeta.is_dir()
    )

    if not clases:
        raise ValueError("No se encontraron clases dentro de la carpeta dataset.")

    for subset in ["train", "validation", "test"]:
        for clase in clases:
            (DATASET_SPLIT_DIR / subset / clase).mkdir(parents=True, exist_ok=True)

    resumen_split = {}
    rng = random.Random(SEED)

    for clase in clases:
        carpeta_clase = DATASET_DIR / clase
        imagenes = sorted(
            archivo
            for archivo in carpeta_clase.iterdir()
            if archivo.is_file()
        )

        if not imagenes:
            raise ValueError(f"La clase {clase} no tiene imagenes.")

        rng.shuffle(imagenes)

        total = len(imagenes)
        train_count = int(total * TRAIN_RATIO)
        validation_count = int(total * VALIDATION_RATIO)

        split_imagenes = {
            "train": imagenes[:train_count],
            "validation": imagenes[train_count:train_count + validation_count],
            "test": imagenes[train_count + validation_count:],
        }

        resumen_split[clase] = {
            subset: len(archivos)
            for subset, archivos in split_imagenes.items()
        }

        for subset, archivos in split_imagenes.items():
            destino_clase = DATASET_SPLIT_DIR / subset / clase
            for archivo in archivos:
                shutil.copy2(archivo, destino_clase / archivo.name)

    return resumen_split


def crear_generadores():
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=20,
        zoom_range=0.2,
        horizontal_flip=True,
    )

    validation_datagen = ImageDataGenerator(rescale=1.0 / 255)
    test_datagen = ImageDataGenerator(rescale=1.0 / 255)

    train_data = train_datagen.flow_from_directory(
        DATASET_SPLIT_DIR / "train",
        target_size=img_size,
        batch_size=batch_size,
        class_mode="categorical",
        seed=SEED,
    )

    validation_data = validation_datagen.flow_from_directory(
        DATASET_SPLIT_DIR / "validation",
        target_size=img_size,
        batch_size=batch_size,
        class_mode="categorical",
        shuffle=False,
    )

    test_data = test_datagen.flow_from_directory(
        DATASET_SPLIT_DIR / "test",
        target_size=img_size,
        batch_size=batch_size,
        class_mode="categorical",
        shuffle=False,
    )

    return train_data, validation_data, test_data


def calcular_class_weight(train_data):
    clases = np.unique(train_data.classes)
    pesos = compute_class_weight(
        class_weight="balanced",
        classes=clases,
        y=train_data.classes,
    )

    return {
        int(clase): float(peso)
        for clase, peso in zip(clases, pesos)
    }


def crear_modelo():
    model = Sequential([
        Conv2D(32, (3, 3), activation="relu", input_shape=(224, 224, 3)),
        MaxPooling2D(2, 2),
        Conv2D(64, (3, 3), activation="relu"),
        MaxPooling2D(2, 2),
        Conv2D(128, (3, 3), activation="relu"),
        MaxPooling2D(2, 2),
        Flatten(),
        Dense(128, activation="relu"),
        Dropout(0.5),
        Dense(3, activation="softmax"),
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model


def guardar_graficas_entrenamiento(history):
    plt.figure()
    plt.plot(history.history["accuracy"], label="Entrenamiento")
    plt.plot(history.history["val_accuracy"], label="Validacion")
    plt.title("Precision del Modelo")
    plt.xlabel("Epocas")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.savefig(RESULTADOS_DIR / "grafica_accuracy.png")
    plt.close()

    plt.figure()
    plt.plot(history.history["loss"], label="Entrenamiento")
    plt.plot(history.history["val_loss"], label="Validacion")
    plt.title("Perdida del Modelo")
    plt.xlabel("Epocas")
    plt.ylabel("Loss")
    plt.legend()
    plt.savefig(RESULTADOS_DIR / "grafica_loss.png")
    plt.close()


def evaluar_en_test(model, test_data, class_names, resumen_split, class_weights):
    test_loss, test_accuracy = model.evaluate(test_data, verbose=0)

    test_data.reset()
    predicciones = model.predict(test_data)
    y_pred = np.argmax(predicciones, axis=1)
    y_true = test_data.classes

    cm = confusion_matrix(y_true, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    disp.plot(xticks_rotation=45)
    plt.title("Matriz de Confusion - Test")
    plt.savefig(RESULTADOS_DIR / "matriz_confusion.png", bbox_inches="tight")
    plt.close()

    reporte_texto = classification_report(
        y_true,
        y_pred,
        target_names=class_names,
    )

    with open(RESULTADOS_DIR / "reporte_metricas.txt", "w", encoding="utf-8") as f:
        f.write(reporte_texto)

    reporte_dict = classification_report(
        y_true,
        y_pred,
        target_names=class_names,
        output_dict=True,
    )

    metrics = {
        "seed": SEED,
        "img_size": list(img_size),
        "batch_size": batch_size,
        "epochs": epochs,
        "split_ratio": {
            "train": TRAIN_RATIO,
            "validation": VALIDATION_RATIO,
            "test": TEST_RATIO,
        },
        "dataset_split": resumen_split,
        "class_indices": test_data.class_indices,
        "class_weight": class_weights,
        "test_loss": float(test_loss),
        "test_accuracy": float(test_accuracy),
        "confusion_matrix": cm.tolist(),
        "classification_report": reporte_dict,
    }

    with open(RESULTADOS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4, ensure_ascii=False)

    return predicciones, y_pred, y_true


def guardar_predicciones(model, test_data, class_names):
    test_data.reset()
    imagenes, etiquetas = next(test_data)
    preds = model.predict(imagenes)
    pred_classes = np.argmax(preds, axis=1)
    true_classes = np.argmax(etiquetas, axis=1)

    correctas = []
    incorrectas = []

    for i in range(len(imagenes)):
        if pred_classes[i] == true_classes[i]:
            correctas.append(i)
        else:
            incorrectas.append(i)

    guardar_ejemplos_predicciones(
        imagenes,
        preds,
        pred_classes,
        true_classes,
        class_names,
        correctas,
        "predicciones_correctas.png",
        "Ejemplos de predicciones correctas",
    )

    guardar_ejemplos_predicciones(
        imagenes,
        preds,
        pred_classes,
        true_classes,
        class_names,
        incorrectas,
        "predicciones_incorrectas.png",
        "Ejemplos de predicciones incorrectas",
    )


def guardar_ejemplos_predicciones(
    imagenes,
    preds,
    pred_classes,
    true_classes,
    class_names,
    indices,
    nombre_archivo,
    titulo,
):
    cantidad = min(len(indices), 3)

    if cantidad == 0:
        plt.figure(figsize=(8, 3))
        plt.axis("off")
        plt.text(0.5, 0.5, f"No se encontraron ejemplos para {titulo}", ha="center")
        plt.savefig(RESULTADOS_DIR / nombre_archivo, bbox_inches="tight")
        plt.close()
        return

    plt.figure(figsize=(12, 4))

    for j in range(cantidad):
        idx = indices[j]
        plt.subplot(1, cantidad, j + 1)
        plt.imshow(imagenes[idx])
        plt.axis("off")

        real = class_names[true_classes[idx]]
        pred = class_names[pred_classes[idx]]
        confianza = np.max(preds[idx]) * 100

        plt.title(
            f"Real: {real}\nPred: {pred}\nConf: {confianza:.2f}%",
            fontsize=8,
        )

    plt.suptitle(titulo)
    plt.tight_layout()
    plt.savefig(RESULTADOS_DIR / nombre_archivo, bbox_inches="tight")
    plt.close()


def main():
    configurar_reproducibilidad(SEED)
    RESULTADOS_DIR.mkdir(exist_ok=True)

    resumen_split = crear_dataset_split()
    train_data, validation_data, test_data = crear_generadores()
    class_weights = calcular_class_weight(train_data)

    model = crear_modelo()

    history = model.fit(
        train_data,
        validation_data=validation_data,
        epochs=epochs,
        class_weight=class_weights,
    )

    model.save(RESULTADOS_DIR / "modelo_papa_cnn.h5")

    guardar_graficas_entrenamiento(history)

    class_names = list(test_data.class_indices.keys())
    evaluar_en_test(model, test_data, class_names, resumen_split, class_weights)
    guardar_predicciones(model, test_data, class_names)

    print("Proceso terminado. Revisa la carpeta resultados.")


if __name__ == "__main__":
    main()
