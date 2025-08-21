ZZIngestions is a powerful Python package that uses PySpark to transform data ingestion into a fluid and efficient process. It allows performing ETL operations in a scalable and intuitive way, improving the robustness and agility of data flows.
        
        
# Parameters:

## Template:

```
{
    "latest_only": (bool, optional) Get only the latest partition in the source table (Default: False).
                                    When in "process_history" mode, "latest_only" will be False.

    "process_history": (*, optional) Process the source table in a loop by partition values, in ascending order. (Default: False)
                                    Can be bool or dict. The data type indicates the process mode:
                                    - A True value or an empty dict ({}) indicates "full" mode, and the default values will apply.
                                    - For "partial" mode or non-default values, follow the rules above:
    {
        "partition_name": (str, optional) The column name to use in the loop (Default: "dt_ingestion").
        "min_value": (str, optional) The lowest value to start the loop (Default: min(partition_name) in the source table).
        "max_value": (str, optional) The highest value to finish the loop (Default: max(partition_name) in the source table).
    }

    "partition_column": (str, optional) The column to filter the latest partition (Default: dt_ingestion).

    "parallel_read": (dict, optional) Settings for parallel reading of data and use of results during ingestion.
                                      Each key corresponds to an identifier, and each value corresponds to the reading options.
                                      These keys will be used as values in "read_options".
    Example:
    {
        "read_1": {...},
        "read_2": {...}
    }

    "common_secrets": (list, optional) Processes the secrets used in ingestion. Necessary when using parallelism, to prevent errors.
    [
        "secret_name_1",
        "secret_name_2"
    ]
    
    "read_options": (*, required) When "parallel_read" is not specified, the value must be a dict with settings to load Spark DataFrames.
                                  Otherwise, the value can be a string containing a key to access the result of parallel read.
    {
        "format": (str, required) The format of the data to read from. Ex.: "parquet"|"csv"|"jdbc"|"delta"|"sap"|etc.
        "schema": (*, optional) Enforce a schema to the source table. Can be str, list or dict.
                                In "string" and "list" modes, all columns will be of type StringType().
                                String example: "col_1, col_2, col_3"
                                List example: ["col_1", "col_2", "col_3"]
                                Dict example: {"col_1": StringType(), "col_2": IntegerType(), "col_3": DateType()}
                                Obs.: To use "dict" mode, import PySpark Types using the command below:
                                    from pyspark.sql.types import *
        
        # some Parquet options:
        "path": (str, required) Folder where the data is located. Ex.: "s3://..."
        
        # some CSV options:
        "path": (str, required) Folder where the data is located. Ex.: "s3://..."
        "header": (bool, optional) Uses the first line as names of columns. Ex.: True|False (Default: False)
        "sep": (str, optional) Sets a separator for each field and value. Ex.: ";" (Default: ",")
        
        # some JDBC options:
        "secret_name": (str, optional) Name of secret in AWS Secrets Manager.
        "dbtable"|"query": (str, required) "dbtable": The full table to read from, or a subquery in parentheses.
                                        "query": A query that will be used as a subquery in the FROM clause to read data.
                                        Obs.: It is not allowed to specify "dbtable" and "query" options at the same time.
        
        # Delta Lake options:
        "name": (str, required) Name of the source table. Format "<catalog>.<database>.<table>".

        # SAP options:
        "secret_name": (str, optional) Name of secret in AWS Secrets Manager.
        "table_name": (str, required) Name of the source table.
        "fields": (list, required) List of columns to get.
        "options": (list, optional) List of filters to apply on source table. (Default: [])
        "delimiter: (str, optional) Sets a separator for each field and value. (Default: "|")
        "rowcount": (integer, optional) Number of rows to return. (Default: Return all rows)
        "rowskips": (integer, optional) Number of rows to ignore before reading. (Default: 0)
        "fetchrows": (integer, optional) Number of rows to fetch in each loop. (Defaul: 1000000)
    }
    
```

### _\<TRANSFORMATIONS: BEGIN>_
_<p>IMPORTANT: The order of the keys in JSON file determines the order which the transformations are performed.</p>_

```
    "aggregate": (dict, optional) Calculate and group the data.
        {"group_by": ["col_A"], "agg": {"col_B": "sum(col_B)"}}
    
    "cast": (dict, optional) Change the data type of columns.
        {"integer": ["col_A"]} ==> df.withColumn("col_A", f.col("col_A").cast("integer"))
    
    "col_names": (list, optional) Rename all columns of the dataframe.
                                The length of the list should be equal to the number of columns in the dataframe.

    "comments": (dict, optional) Update the comment of columns.
        {"column": "comment..."}
    
    "data_quality": (dict, required) A set of rules to validate the data.
    {
        "expectation_suite_name": (str, required) Name of expectation suite.
        "expectations": (list, required) List of expectations
        [
            {
                "expectation_name": "expect_...",
                "kwargs": {...}
            },
            "meta": {
                "level: "error|warning" # If "error", invalid rows will not be written to the target table. (Default: "error")
            }
        ]
    }

    "distinct": (*, optional) Remove duplicated rows from dataframe.
                            The value of this parameter doesn't matter, as long as the key is entered the command will be executed.
                            Ex.: "distinct": True | "distinct": None | "distinct": ""
    
    "drop": (list, optional) Drop specific columns.
        ["col_X", "col_Y"] ==> df.drop(*["col_X", "col_Y"])

    "filter": (list, optional) Apply SQL filters.
        ["col_C is not null"] ==> df.filter("col_C is not null")

    "grants": (dict, optional) Set grants to target table.
        {"principal": "privileges"}
    
    "join": (dict, optional) Joins two DataFrames.
        {"read_options": {...}, "on": [...], "how": "left"} ==> df.join(spark.read.load(**{...}), on=[...], how="left")

    "order_by": (dict, optional) Sort the data.
        {"col_A": "asc", "col_B": "desc"} ==> df.sort(col("col_A").asc(), col("col_B").desc())

    "rename": (dict, optional) Rename specific columns.
        {"old_col": "new_col"} ==> df.withColumnRenamed("old_col", "new_col")

    "repartition": [integer, optional] Reorder dataframe partitions to specific number.
    
    "remove_accents": (list, optional) Removes accents and cedilla from specified columns.

    "select": (list, optional) Select specific columns. Can be used to sort columns.
        ["col_X", "col_A"] ==> df.select("col_X", "col_A")
    
    "transform": (dict, optional) Dataframe transformation.
        {"col_1": "current_date()"} ==> df.withColumn("col_1", f.expr("current_date()"))
    
    "trim_cols": (*, optional) Remove the leading and/or trailing spaces from columns. Can be bool, list or dict.
        A True value trims both ends in all columns.
        A list of columns trims both ends in these columns. Ex.: ["col_1", "col_2", "col_3"]
        The "dict" mode allows additional settings:
        {
            "mode": "both"|"leading"|"trailing" (Default: "both").
            "trim_str": The trim string characters to trim (Default: single space).
            "columns": ["list", "of", "columns"] (Default: all columns)
        }
    
    "union": (dict, optional) Unites two DataFrames by column position.
        {"read_options": {...}} ==> df.union(spark.read.load(**{...}))

    "union_by_name": (dict, optional) Unites two DataFrames by column name.
        {"read_options": {...}} ==> df.unionByName(spark.read.load(**{...}))
    
```

### _\<TRANSFORMATIONS: END>_

```
    "write_options": (dict, required) Settings in JSON format to save Spark dataframes.
    {
        "format": (str, required) The format of the data to write to. Ex.: "parquet"|"csv"|"delta"|etc.
        "mode": (str, required) Indicates how the data will be saved. Ex.: "overwrite"|"append"|"ignore"|etc. (more details below)
        "path": (str, required) Folder where the data is located. Ex.: "s3://..."
        
        # some CSV options:
        "header": (bool, optional) Writes the names of columns as the first line. Ex.: True|False (Default: False)
        "sep": (str, optional) Sets a separator for each field and value. Ex.: ";" (Default: ",")
        
        # Delta Lake options:
        "name": (str, required) Name of the target table. Format "<catalog>.<database>.<table>". 
        "partitionBy": (list, optional) Column used to group the data into folders. Ex.: ["dt_ingestion"]
        "partitionOverwriteMode": (str, optional) Used together with "partitionBy", in modes "overwrite" and "replace". (Default: "static")
                                                "dynamic": Indicates that only the partitions containing new data will be overwritten.
                                                "static": The entire table will be overwritten with the new data.
        "owner": (str, optional) The owner of the table. (Default: "zzdata@arezzo.com.br")
        "comment": (str, optional) The comment of the table in data catalog. (Default: The source table)
        "optimize_where": (list, optional) Apply filters to optimize a part of the table.
        "optimize_zorder": (list, optional) Order the data by specific columns.
        "merge_keys": (list, optional) List of columns to match source and target tables. Required if mode="merge".
        "merge_filter": (list, optional) Filter to reduce the search space for matches.
        "delete_keys": (list, optional) List of columns to match source and target tables. Required if mode="delete_insert".
    }
    
    "rename_target_file": (dict, optional) Rename the target file (Default: False).
                                        If this parameter is set, the 'repartition' parameter will receive the value '1'.
    {
        "target_name" : (str, required) It can be fixed or contain variables. Ex.: "the_new_file_name_{date}_{time}.ext"
        "format_values": (dict, optional) Required if 'target_name' contains variables. The keys here must match to the values inside '{}' in 'target_name'.
        {
            "date": Ex.: "%Y%m%d"
            "time": Ex.: "%H%M%S"
        }
    }
                                
    "delete_processed_files": (bool, optional) Deleted the source files after process (Default: False).
    
    "optimize_target_table": (bool, optional) Optimize the target table (Default: True).
    
    "vacuum_target_table": (bool, optional) Apply vacuum in target table to remove unused files (Default: True).
}
```

## Write modes:

| MODE_NAME           | CREATE_MODE   | CREATE_WITH_DATA | DATA_MODE        | WRITE: DELTA | WRITE: NON-DELTA | DEFINITION
|---------------------|---------------|------------------|------------------|--------------|------------------|------------
| append              | if_not_exists | No               | Insert into      | Yes          | Yes              | Just insert the new data at the end of the table.
| delete_insert       | if_not_exists | No               | Delete + Append  | Yes          | No               | Create the table if it doesn't exist; delete data from target and insert the new data.
| error/errorifexists | default       | Yes              | None             | Yes          | Yes              | Create the table if it doesn't exist and insert the new data; otherwise generate an error.
| ignore              | if_not_exists | Yes              | None             | Yes          | Yes              | Create the table if it doesn't exist and insert the new data; otherwise do nothing.
| merge               | if_not_exists | No               | Merge            | Yes          | No               | Create the table if it doesn't exist; update/insert the new data.
| overwrite           | replace       | Yes              | None             | Yes          | Yes              | Overwrite the table definition and data.
| replace             | if_not_exists | No               | Insert overwrite | Yes          | No               | Create the table if it doesn't exist; replace the content with the new data.<br>If used with partitionOverwriteMode=dynamic, only overwrite the current partition,<br>otherwise overwrite all table contents with the new data.

## Example:

```python
{
    "latest_only": False,
    "read_options": {
        "format": "csv",
        "path": "s3://arzz-datalake-transient-us-east-1-prd/zznet/anjos/loja/wfa_pessoa/",
        "header": True,
        "sep": ";"
    },
    "data_quality": {
        "expectation_suite_name": "transient_to_raw_loja_wfa_pessoa",
        "expectations": [
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {
                    "column": "PESSOA",
                    "result_format": "COMPLETE"
                },
                "meta": {
                    "level": "error"
                }
            }
        ]
    },
    "transform": {
        "dt_ingestion": "date_format(current_date(), 'yyyy-MM-dd')"
    },
    "write_options": {
        "format": "csv",
        "path": "s3://arzz-datalake-raw-us-east-1-prd/zznet/anjos/loja/wfa_pessoa/",
        "header": True,
        "sep": ";",
        "mode": "overwrite",
        "partitionOverwriteMode": "dynamic",
        "partitionBy": [
            "dt_ingestion"
        ]
    },
    "delete_processed_files": True
}
```

## Useful Links:

- Spark data sources: https://spark.apache.org/docs/latest/sql-data-sources.html
- Spark data types: https://spark.apache.org/docs/latest/sql-ref-datatypes.html
- List of expectations: https://greatexpectations.io/expectations/
- Python datetime formats: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes