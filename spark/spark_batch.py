import argparse

from spark_statistics import (
    class_summary,
    count_by_class,
    count_by_subset,
    count_by_subset_and_class,
    descriptive_statistics,
    subset_class_summary,
)
from spark_utils import (
    build_image_records,
    create_images_dataframe,
    create_spark_session,
    export_class_summary_csv,
    export_csv,
    export_dataset_metadata_csv,
    export_parquet,
    get_default_paths,
    is_windows_hadoop_error,
    prepare_output_dir,
    write_export_status,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Pipeline batch PySpark para metadata de imagenes de hojas de papa."
    )
    parser.add_argument(
        "--partitions",
        type=int,
        default=2,
        help="Numero de particiones Spark para procesar el DataFrame.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.partitions < 1:
        raise ValueError("El numero de particiones debe ser mayor o igual a 1.")

    dataset_split_dir, output_dir = get_default_paths()
    prepare_output_dir(output_dir)

    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    try:
        print("\n=== PIPELINE BATCH PYSPARK ===")
        print(f"Dataset origen: {dataset_split_dir}")
        print(f"Salida: {output_dir}")
        print(f"Particiones solicitadas: {args.partitions}")

        records = build_image_records(dataset_split_dir)
        images_df = create_images_dataframe(spark, records, args.partitions)

        print("\n=== ESQUEMA DEL DATAFRAME ===")
        images_df.printSchema()

        print("\n=== PARTICIONES DEL DATAFRAME ===")
        print(f"Numero de particiones reales: {images_df.rdd.getNumPartitions()}")

        print("\n=== MUESTRA DE REGISTROS ===")
        images_df.show(10, truncate=False)

        print("\n=== CANTIDAD DE IMAGENES POR CLASE ===")
        by_class_df = count_by_class(images_df)
        by_class_df.show(truncate=False)

        print("\n=== CANTIDAD DE IMAGENES POR SUBSET ===")
        by_subset_df = count_by_subset(images_df)
        by_subset_df.show(truncate=False)

        print("\n=== CANTIDAD DE IMAGENES POR SUBSET Y CLASE ===")
        by_subset_class_df = count_by_subset_and_class(images_df)
        by_subset_class_df.show(truncate=False)

        print("\n=== CANTIDAD TOTAL DE IMAGENES ===")
        total_images = images_df.count()
        print(f"Total: {total_images}")

        print("\n=== ESTADISTICAS DESCRIPTIVAS DE TAMANO DE ARCHIVO ===")
        descriptive_statistics(images_df).show(truncate=False)

        print("\n=== RESUMEN POR CLASE ===")
        class_summary_df = class_summary(images_df)
        class_summary_df.show(truncate=False)

        print("\n=== RESUMEN POR SUBSET Y CLASE ===")
        subset_class_summary_df = subset_class_summary(images_df)
        subset_class_summary_df.show(truncate=False)

        print("\n=== DAG / PLAN FISICO DEL PROCESO ===")
        subset_class_summary_df.explain(mode="formatted")

        print("\n=== EXPORTACION ===")
        try:
            parquet_path = export_parquet(images_df, output_dir)
            csv_path = export_csv(class_summary_df, output_dir)
            status_path = write_export_status(
                output_dir=output_dir,
                mode="Spark Complete",
                parquet_status="Generado",
                reason="",
                generated_files=[parquet_path, csv_path],
            )

            print("Estado: SUCCESS")
            print(f"Parquet generado en: {parquet_path}")
            print(f"CSV resumen generado con Spark en: {csv_path}")
            print(f"Estado de exportacion: {status_path}")
        except Exception as error:
            if not is_windows_hadoop_error(error):
                raise

            print("WARNING: Se activo Windows Compatibility Mode.")
            print("Motivo: Hadoop/winutils no disponible para escritura local de Spark.")

            metadata_csv_path = export_dataset_metadata_csv(records, output_dir)
            summary_csv_path = export_class_summary_csv(records, output_dir)
            status_path = write_export_status(
                output_dir=output_dir,
                mode="Windows Compatibility",
                parquet_status="No generado",
                reason="Hadoop/winutils no disponible",
                generated_files=[metadata_csv_path, summary_csv_path],
            )

            print("Estado: SUCCESS con Windows Compatibility Mode")
            print("Parquet: No generado")
            print(f"Metadata CSV generado con Python en: {metadata_csv_path}")
            print(f"Resumen CSV generado con Python en: {summary_csv_path}")
            print(f"Estado de exportacion: {status_path}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
