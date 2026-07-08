from pyspark.sql import functions as F


def count_by_class(dataframe):
    # Transformacion: agrupa por clase para preparar el conteo.
    return dataframe.groupBy("class_name").count().orderBy("class_name")


def count_by_subset(dataframe):
    # Transformacion: resume cuantas imagenes hay en train, validation y test.
    return dataframe.groupBy("subset").count().orderBy("subset")


def count_by_subset_and_class(dataframe):
    # Transformacion: permite verificar la distribucion estratificada por subset.
    return (
        dataframe
        .groupBy("subset", "class_name")
        .count()
        .orderBy("subset", "class_name")
    )


def descriptive_statistics(dataframe):
    # Accion posterior con show(): describe estadisticas numericas del tamano de archivo.
    return dataframe.select("file_size_bytes").describe()


def class_summary(dataframe):
    # Transformacion agregada para exportar un CSV resumen por clase.
    return (
        dataframe
        .groupBy("class_name")
        .agg(
            F.count("*").alias("total_images"),
            F.min("file_size_bytes").alias("min_file_size_bytes"),
            F.max("file_size_bytes").alias("max_file_size_bytes"),
            F.round(F.avg("file_size_bytes"), 2).alias("avg_file_size_bytes"),
        )
        .orderBy("class_name")
    )


def subset_class_summary(dataframe):
    # Transformacion agregada para revisar distribucion y tamano promedio por subset y clase.
    return (
        dataframe
        .groupBy("subset", "class_name")
        .agg(
            F.count("*").alias("total_images"),
            F.round(F.avg("file_size_bytes"), 2).alias("avg_file_size_bytes"),
        )
        .orderBy("subset", "class_name")
    )
