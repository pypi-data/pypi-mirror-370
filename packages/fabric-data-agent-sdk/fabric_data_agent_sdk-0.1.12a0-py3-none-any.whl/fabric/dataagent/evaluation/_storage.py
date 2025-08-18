"""
Functions for interacting with the database/storage for evaluation results.
"""
from synapse.ml.internal_utils.session_utils import get_fabric_context
import pandas as pd
import logging
from IPython.display import display, HTML


def _save_output(df: pd.DataFrame, table_name: str):
    """
    Saves the Dataframe to the Delta table.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with processed output rows.
    table_name : str
        Table name to store the evaluation result
    """
    try:
        lakehouse_path = _default_lakehouse_path()
        table_path = f"{lakehouse_path}/Tables/{table_name}"

        if _on_jupyter():
            try:
                from deltalake.writer import write_deltalake
                write_deltalake(table_path, df, mode="append")
            except ImportError:
                logging.error("deltalake module not found. Please install it to use this feature.")
            except Exception as e:
                logging.error(f"Error writing to Delta table: {str(e)}")
        else:
            try:
                from pyspark.sql import SparkSession
                from pyspark.sql.functions import col

                spark = SparkSession.builder.getOrCreate()
                try:
                    # Get schema if table exists
                    delta_df = spark.read.format("delta").load(table_path)
                    expected_schema = delta_df.schema
                    spark_df = spark.createDataFrame(df, schema=expected_schema)
                except Exception:
                    spark_df = spark.createDataFrame(df)
                    if "run_timestamp" in spark_df.columns:
                        # Making the timestamp compatible with Python
                        spark_df = spark_df.withColumn("run_timestamp", col("run_timestamp").cast("timestamp_ntz"))

                spark_df.write.format("delta").mode("append").save(table_path)
            except ImportError:
                logging.error("pyspark module not found. Please install it to use this feature.")
            except Exception as e:
                logging.error(f"Error in Spark processing: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error in _save_output: {str(e)}")


def _default_lakehouse_path():
    """
    Get default lakehouse path.

    Returns
    -------
    str
        Default lakehouse path.
    """
    try:
        fabric_context = get_fabric_context()
        defaultFs = fabric_context.get('fs.defaultFS')
        lakehouse_id = fabric_context.get('trident.lakehouse.id')
        
        if not defaultFs or not lakehouse_id:
            raise ValueError("Missing required Fabric context parameters")
            
        return f"{defaultFs}{lakehouse_id}"
    except Exception as e:
        logging.error(f"Error getting default lakehouse path: {str(e)}")
        # Return a placeholder path that will be used in error handling
        return "abfs://default@fabric/default_lakehouse"


def _get_data(table_name: str):
    """
    Get data from the specified delta table and return it as a Pandas DataFrame.

    Parameters
    ----------
    table_name : str
        Table name which contains the evaluation result.

    Returns
    -------
    DataFrame
        Data from the specified delta table as a Pandas DataFrame instance.
    """
    import os

    df = None
    try:
        lakehouse_path = _default_lakehouse_path()
        table_path = f"{lakehouse_path}/Tables/{table_name}"
        
        if _on_jupyter():
            try:
                from deltalake import DeltaTable

                # Load the Delta Lake table
                delta_table = DeltaTable(table_path)
                df = delta_table.to_pandas() if delta_table is not None else None
            except ImportError:
                message = f"<h4>deltalake package not found. Please install it to use this feature.</h4>"
                display(HTML(message))
                return None
            except Exception:
                message = f"<h4>Table does not exist. Please provide the table name from attached default lakehouse.</h4>"
                display(HTML(message))
                return None
        else:
            try:
                from pyspark.sql import SparkSession

                spark = SparkSession.builder.getOrCreate()
                spark_df = spark.read.format("delta").load(table_path)
                df = spark_df.toPandas()
            except ImportError:
                logging.error("pyspark module not found. Please install it to use this feature.")
                return None
            except Exception:
                message = f"<h4>Table does not exist. Please provide the table name from attached default lakehouse.</h4>"
                display(HTML(message))
                return None
    except Exception as e:
        message = f"<h4>Error accessing table: {str(e)}. Please check your lakehouse connection.</h4>"
        display(HTML(message))
        return None

    return df


def _on_jupyter() -> bool:
    """
    Check if the code is running in a Jupyter environment.

    Returns
    -------
    bool
        True if running in Jupyter, False otherwise.
    """
    try:
        import os
        return os.environ.get("MSNOTEBOOKUTILS_RUNTIME_TYPE", "").lower() == "jupyter"
    except Exception as e:
        logging.warning(f"Error detecting Jupyter environment: {str(e)}")
        return False
