# Pipeline Batch PySpark

Esta fase agrega un pipeline batch real con PySpark para analizar la metadata de las imagenes ya divididas en `dataset_split/`.
No modifica el entrenamiento, la CNN, el backend, el frontend, el dataset original ni los resultados del modelo.

## Archivos

| Archivo               | Responsabilidad                                                                                     |
| --------------------- | --------------------------------------------------------------------------------------------------- |
| `spark_batch.py`      | Ejecuta el pipeline batch completo.                                                                 |
| `spark_statistics.py` | Contiene transformaciones estadisticas sobre el DataFrame.                                          |
| `spark_utils.py`      | Contiene utilidades para crear SparkSession, leer imagenes, construir DataFrame y exportar salidas. |
| `README.md`           | Documenta ejecucion, transformaciones, acciones, particiones y batch processing.                    |

## Entrada

El pipeline lee automaticamente:

```text
dataset_split/
  train/
  validation/
  test/
```

Cada imagen se convierte en un registro con:

```text
image_path
class_name
file_name
subset
file_size_bytes
```

## Salidas

Al ejecutar el pipeline se crean salidas dentro de:

```text
spark/output/
```

En modo Spark completo se generan:

```text
spark/output/images_metadata.parquet/
spark/output/class_summary_csv/
spark/output/export_status.txt
```

Spark escribe Parquet y CSV como carpetas con archivos `part-*`.

En Windows sin Hadoop o sin `winutils.exe`, Spark puede fallar al escribir en disco local.
En ese caso el pipeline activa automaticamente Windows Compatibility Mode y genera:

```text
spark/output/dataset_metadata.csv
spark/output/class_summary.csv
spark/output/export_status.txt
```

## Ejecucion

Desde la raiz del proyecto:

```powershell
.\venv\Scripts\python.exe spark\spark_batch.py --partitions 4
```

Si no se indica `--partitions`, se usa `2` por defecto:

```powershell
.\venv\Scripts\python.exe spark\spark_batch.py
```

## Transformaciones

El pipeline usa transformaciones Spark como:

| Transformacion   | Uso en el pipeline                                            |
| ---------------- | ------------------------------------------------------------- |
| `repartition(n)` | Configura el numero de particiones del DataFrame.             |
| `groupBy(...)`   | Agrupa imagenes por clase, subset o ambos.                    |
| `agg(...)`       | Calcula totales, minimos, maximos y promedios.                |
| `orderBy(...)`   | Ordena los resultados para lectura clara.                     |
| `select(...)`    | Selecciona columnas numericas para estadisticas descriptivas. |

Las transformaciones son lazy: Spark no las ejecuta hasta que aparece una accion.

## Acciones

El pipeline ejecuta acciones como:

| Accion               | Uso en el pipeline                            |
| -------------------- | --------------------------------------------- |
| `printSchema()`      | Muestra el esquema del DataFrame.             |
| `show()`             | Materializa y muestra conteos y estadisticas. |
| `count()`            | Calcula la cantidad total de imagenes.        |
| `write.parquet(...)` | Exporta metadata completa en formato Parquet. |
| `write.csv(...)`     | Exporta resumen por clase en CSV.             |
| `explain(...)`       | Muestra el DAG o plan fisico del proceso.     |

Si la escritura Spark falla por `HADOOP_HOME`, `hadoop.home.dir`, `winutils.exe` o `RawLocalFileSystem`,
el programa captura solo ese tipo de error y continua con exportacion local compatible con Windows.

## Particiones

El argumento `--partitions` permite controlar cuantas particiones tendra el DataFrame principal.
Esto permite evidenciar distribucion de procesamiento incluso en modo local:

```powershell
.\venv\Scripts\python.exe spark\spark_batch.py --partitions 6
```

El script muestra el numero real de particiones con:

```python
images_df.rdd.getNumPartitions()
```

## Batch Processing

Este pipeline es batch porque:

- procesa todos los archivos existentes en `dataset_split/`
- calcula estadisticas globales del conjunto completo
- no depende de peticiones en tiempo real
- genera salidas persistentes en Parquet y CSV
- ejecuta acciones Spark sobre un DataFrame completo

## Modos de exportacion

### Modo Spark completo

Este es el modo principal y profesional del pipeline.
Spark escribe directamente:

```text
spark/output/images_metadata.parquet/
spark/output/class_summary_csv/
```

El archivo `spark/output/export_status.txt` registra:

```text
Modo: Spark Complete
Parquet: Generado
```

### Modo Windows Compatibility

Este modo se activa automaticamente solo si Spark falla al escribir por una limitacion local de Windows relacionada con Hadoop o `winutils.exe`.
El pipeline no se rompe y termina con codigo de salida 0.

En este modo se generan archivos CSV locales con Python:

```text
spark/output/dataset_metadata.csv
spark/output/class_summary.csv
spark/output/export_status.txt
```

El archivo `export_status.txt` registra:

```text
Modo: Windows Compatibility
Parquet: No generado
Motivo: Hadoop/winutils no disponible
```

Este modo no reemplaza el procesamiento Spark.
La lectura, DataFrame, transformaciones, acciones, conteos, estadisticas, particiones y DAG siguen ejecutandose con PySpark.
Solo la persistencia final cambia para evitar instalar Hadoop completo en Windows.

## Relacion con CE2_CD1

La implementacion demuestra procesamiento de datos con PySpark usando datos reales del proyecto.
Cubre lectura, estructuracion en DataFrame, transformaciones, acciones, particiones, estadisticas, DAG y persistencia de resultados.
