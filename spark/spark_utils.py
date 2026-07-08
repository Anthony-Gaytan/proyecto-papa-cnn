import os
import sys
import csv
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.types import LongType, StringType, StructField, StructType


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}
WINDOWS_HADOOP_ERROR_MARKERS = (
    "HADOOP_HOME",
    "hadoop.home.dir",
    "winutils.exe",
    "RawLocalFileSystem",
)


def create_spark_session(app_name="PapaDatasetBatchPipeline"):
    # Fuerza a Spark a usar el mismo Python que ejecuto este script.
    python_executable = str(Path(sys.executable).resolve())
    os.environ["PYSPARK_PYTHON"] = python_executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = python_executable

    # Crea una sesion Spark local para procesamiento batch.
    return (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.pyspark.python", python_executable)
        .config("spark.pyspark.driver.python", python_executable)
        .config("spark.executorEnv.PYSPARK_PYTHON", python_executable)
        .getOrCreate()
    )


def get_project_root():
    # La carpeta spark esta dentro de la raiz del proyecto.
    return Path(__file__).resolve().parent.parent


def get_default_paths():
    # Centraliza rutas para mantener el pipeline independiente del entrenamiento.
    project_root = get_project_root()
    dataset_split_dir = project_root / "dataset_split"
    output_dir = project_root / "spark" / "output"

    return dataset_split_dir, output_dir


def build_image_records(dataset_split_dir):
    # Recorre dataset_split/subset/clase/imagen y crea registros de metadata.
    records = []
    dataset_split_path = Path(dataset_split_dir)

    if not dataset_split_path.exists():
        raise FileNotFoundError(f"No existe la carpeta: {dataset_split_path}")

    for subset_dir in sorted(dataset_split_path.iterdir()):
        if not subset_dir.is_dir():
            continue

        subset = subset_dir.name

        for class_dir in sorted(subset_dir.iterdir()):
            if not class_dir.is_dir():
                continue

            class_name = class_dir.name

            for image_path in sorted(class_dir.iterdir()):
                if not image_path.is_file() or image_path.suffix not in IMAGE_EXTENSIONS:
                    continue

                records.append(
                    {
                        "image_path": str(image_path.resolve()),
                        "class_name": class_name,
                        "file_name": image_path.name,
                        "subset": subset,
                        "file_size_bytes": os.path.getsize(image_path),
                    }
                )

    if not records:
        raise ValueError("No se encontraron imagenes en dataset_split.")

    return records


def create_images_dataframe(spark, records, partitions):
    # Crea el DataFrame base y configura el numero de particiones solicitado.
    schema = StructType(
        [
            StructField("image_path", StringType(), nullable=False),
            StructField("class_name", StringType(), nullable=False),
            StructField("file_name", StringType(), nullable=False),
            StructField("subset", StringType(), nullable=False),
            StructField("file_size_bytes", LongType(), nullable=False),
        ]
    )

    dataframe = spark.createDataFrame(records, schema=schema)
    return dataframe.repartition(partitions)


def prepare_output_dir(output_dir):
    # Crea la carpeta de salida si no existe. Spark sobrescribe subcarpetas especificas.
    Path(output_dir).mkdir(parents=True, exist_ok=True)


def export_parquet(dataframe, output_dir):
    parquet_path = Path(output_dir) / "images_metadata.parquet"
    dataframe.write.mode("overwrite").parquet(str(parquet_path))
    return parquet_path


def export_csv(dataframe, output_dir):
    csv_path = Path(output_dir) / "class_summary_csv"
    dataframe.coalesce(1).write.mode("overwrite").option("header", True).csv(str(csv_path))
    return csv_path


def is_windows_hadoop_error(error):
    error_text = str(error)
    return any(marker in error_text for marker in WINDOWS_HADOOP_ERROR_MARKERS)


def export_dataset_metadata_csv(records, output_dir):
    csv_path = Path(output_dir) / "dataset_metadata.csv"
    fieldnames = ["image_path", "class_name", "file_name", "subset", "file_size_bytes"]

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    return csv_path


def export_class_summary_csv(records, output_dir):
    csv_path = Path(output_dir) / "class_summary.csv"
    summary = {}

    for record in records:
        class_name = record["class_name"]
        file_size = record["file_size_bytes"]

        if class_name not in summary:
            summary[class_name] = {
                "class_name": class_name,
                "total_images": 0,
                "min_file_size_bytes": file_size,
                "max_file_size_bytes": file_size,
                "total_file_size_bytes": 0,
            }

        item = summary[class_name]
        item["total_images"] += 1
        item["min_file_size_bytes"] = min(item["min_file_size_bytes"], file_size)
        item["max_file_size_bytes"] = max(item["max_file_size_bytes"], file_size)
        item["total_file_size_bytes"] += file_size

    rows = []
    for class_name in sorted(summary):
        item = summary[class_name]
        rows.append(
            {
                "class_name": item["class_name"],
                "total_images": item["total_images"],
                "min_file_size_bytes": item["min_file_size_bytes"],
                "max_file_size_bytes": item["max_file_size_bytes"],
                "avg_file_size_bytes": round(
                    item["total_file_size_bytes"] / item["total_images"],
                    2,
                ),
            }
        )

    fieldnames = [
        "class_name",
        "total_images",
        "min_file_size_bytes",
        "max_file_size_bytes",
        "avg_file_size_bytes",
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return csv_path


def write_export_status(output_dir, mode, parquet_status, reason, generated_files):
    status_path = Path(output_dir) / "export_status.txt"

    with open(status_path, "w", encoding="utf-8") as file:
        file.write(f"Modo: {mode}\n")
        file.write(f"Parquet: {parquet_status}\n")
        if reason:
            file.write(f"Motivo: {reason}\n")
        file.write("Archivos generados:\n")
        for generated_file in generated_files:
            file.write(f"- {generated_file}\n")

    return status_path
