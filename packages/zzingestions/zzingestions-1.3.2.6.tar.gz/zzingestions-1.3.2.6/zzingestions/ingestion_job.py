from copy import deepcopy
from functools import reduce
from databricks.sdk.runtime import spark, dbutils
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.errors import exceptions as E
import great_expectations as gx
import os
import re
import requests


class IngestionJob:
    
    # vvvvv DEFAULT CLASS METHODS vvvvv

    def __init__(self, parameters:dict=None, debug_mode:bool=False, process_history=False, disable_warnings=True) -> None:
        """
        # Arguments (all optional):
        - parameters: [dict] The parameters for job execution. For more details see README or help().
        - debug_mode: [bool] Run in debug mode, displaying step-by-step execution messages. Default is False.
        - process_history: [any] Run historical reprocessing in loop partition by partition. Default is False. See README or help() for details.
        - disable_warnings: [bool] Disable warnings. Default is True.
        """

        self.parameters = None
        self.debug_mode = debug_mode
        self.process_history = process_history

        if disable_warnings:
            self.toggle_warnings(False)

        if parameters is not None:
            self.parameters = deepcopy(parameters)
            self.__set_work_parameters()
        self.__set_class_docstring()

    def __set_class_docstring(self):
        self.__doc__ = """ZZIngestions is a powerful Python package that uses PySpark to transform data ingestion into a fluid and efficient process. It allows performing ETL operations in a scalable and intuitive way, improving the robustness and agility of data flows.
        
        
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
"""
    
    def __str__(self):
        """
        Return the class docstring.
        """

        return self.__doc__

    def help(self, name:str=None) -> None:
        """
        Print the docstring of the class or of a method 'name'.
        - name: Method name to find the docstring. If None, prints the class docstring.
        """

        from IPython.display import display, Markdown
        
        if name:
            method = getattr(self, name, None)
            if method is not None:
                docstring = method.__doc__
            else:
                raise NameError(f"Method '{name}' not found.")
        else:
            docstring = self.__doc__

        display(Markdown(docstring))        

    def run(self, kwargs:dict={}) -> None:
        """
        The main method of the class, responsible for executing the entire process contained in the JSON parameters received.
        """

        self.pprint("Process start", dots=0, skip_line=True)
        
        if kwargs.get("parameters"):
            self.parameters = deepcopy(kwargs["parameters"])
            self.__set_work_parameters()

        if not self.__validate_job_parameters(self.parameters):
            raise AttributeError("JSON parameter cannot be empty.")
        
        if kwargs.get("debug_mode"):
            self.debug_mode = kwargs["debug_mode"]
        if kwargs.get("process_history"):
            self.process_history = kwargs["process_history"]

        self.pprint(f"Job parameters: {self.parameters}", dots=0)
        self.pprint(f"Debug mode: {self.debug_mode}", dots=0)
        self.pprint(f"Process history: {self.process_history}", dots=0)
        
        try:
            if self.__common_secrets:
                self.preprocess_secrets()
            
            if self.__fl_parallel:
                self.process_parallel_read(**self.__parallel_options)

            self.process_history = self.__get_process_history(self.process_history, print_level=0)
            self.debug_print(f"Process history after get = {self.process_history}")
            
            if self.process_history:
                self.pprint("Process history starting")

                partitions = self.__get_process_history_partitions(print_level=0)
                self.debug_print(f"partitions = {partitions}")
                
                for partition_value in partitions:
                    df = self.read_data(self.__read_options, self.__fl_latest_partition_only, self.__partition_column)

                    self.pprint(f"Filtering {self.process_history['partition_name']} = '{partition_value}'")
                    df = df.filter(F.col(self.process_history['partition_name']) == F.lit(partition_value))
                    
                    df = self.transformations(df, self.parameters)
                    df = self.__write_data(df)

            else:
                df = self.read_data(self.__read_options, self.__fl_latest_partition_only, self.__partition_column)
                df = self.transformations(df, self.parameters)
                df = self.__write_data(df)

            self.__rename_target_file()
            self.__delete_processed_files()

            self.pprint("Process finished", dots=0)

        except Exception as e:
            error_message = f"{type(e).__name__}: {str(e)}"
            self.pprint("ERROR => "+error_message, dots=0)
            raise

    # ^^^^^ DEFAULT CLASS METHODS ^^^^^

    # vvvvv PARAMETERS DEFINITION vvvvv

    def __get_read_options(self, kwargs) -> dict:
        if self.__fl_parallel and isinstance(kwargs, str):
            return kwargs

        else:
            read_options = deepcopy(kwargs)

            # If format = 'jdbc' then get secret value in AWS and append to 'read_options'
            if read_options.get("format") == "jdbc":
                read_options.pop("path", None)
            
            # If there is a "secret_name" key then get secret value in AWS and append to 'read_options'
            if read_options.get("secret_name"):
                jdbc_options = self.get_secret(read_options.pop("secret_name"))
                read_options.update(jdbc_options)

            if read_options.get("schema"):
                read_options["schema"] = self.create_schema(read_options["schema"])
            
            self.debug_print(f"Read options: {read_options}")
            return read_options
    
    def __get_process_history_partitions(self, print_level:int) -> list:
        query_partitions = f"select distinct {self.process_history['partition_name']} from {self.__read_options['name']}"

        if self.process_history["mode"] == "partial":
            query_partitions += f" where {self.process_history['partition_name']} between '{self.process_history['min_value']}' and '{self.process_history['max_value']}'"
        
        query_partitions += f" order by {self.process_history['partition_name']} asc"
        
        return [row[0] for row in self.__execute_sql(f"{query_partitions}", True, print_level+1, True).collect()]

    def __get_process_history(self, args, print_level:int):
        self.debug_print(f"def GET_PROCESS_HISTORY >> parameters >> args={args}")

        if args is True:
            process_history = {}
        elif args is False or args is None or not isinstance(args, dict):
            return False
        elif isinstance(args, dict):
            process_history = deepcopy(args)
        
        process_history["mode"] = "partial" if process_history.get("min_value") or process_history.get("max_value") else "full"
        process_history["partition_name"] = self.__partition_column or "dt_ingestion"
        
        if process_history["mode"] == "partial":
            if not process_history.get("min_value"):
                process_history["min_value"] = self.__execute_sql(f"select min({process_history['partition_name']}) from {self.__read_options['name']}", True, print_level+1, True).collect()[0][0]
            if not process_history.get("max_value"):
                process_history["max_value"] = self.__execute_sql(f"select max({process_history['partition_name']}) from {self.__read_options['name']}", True, print_level+1, True).collect()[0][0]
        
        return process_history

    def __set_work_parameters(self) -> None:
        self.__parallel_read_options = self.__get(self.parameters, "parallel_read", {})
        self.__fl_parallel = True if self.__parallel_read_options else False
        self.__parallel_options = self.__get(self.parameters, "parallel_options", {})
        self.__parallel_completed = {}
        self.__common_secrets = self.__get(self.parameters, "common_secrets", None)
        self.__read_options = self.__get_read_options(self.__get(self.parameters, "read_options", {}))
        self.__write_options = self.__get(self.parameters, "write_options", None)
        self.__fl_latest_partition_only = self.__get(self.parameters, "latest_only", False)
        self.__partition_column = self.__get(self.parameters, "partition_column", "dt_ingestion")
        self.__fl_delete_processed_files = self.__get(self.parameters, "delete_processed_files", False)
        self.__fl_rename_target_file = self.__get(self.parameters, "rename_target_file", False)
        self.__fl_optimize_target_table = self.__get(self.parameters, "optimize_target_table", False)
        self.__fl_vacuum_target_table = self.__get(self.parameters, "vacuum_target_table", False)
        self.__dataframe_columns = None
        self.__temp_view = "temp_view"
        self.__secrets = {}

        # Constants
        self.__AND__ = " and "
        self.__OR__ = " or "

        # If 'rename_target_file' is True, then set 'repartition' transformation
        if self.__fl_rename_target_file:
            self.parameters["repartition"] = 1

        # If 'process_history', then set 'latest_partition_only' as False
        if self.process_history:
            self.__fl_latest_partition_only = False

        self.debug_print(f"parallel = {self.__fl_parallel}")
        self.debug_print(f"latest_partition_only = {self.__fl_latest_partition_only}")
        self.debug_print(f"partition_column = {self.__partition_column}")
        self.debug_print(f"delete_processed_files = {self.__fl_delete_processed_files}")
        self.debug_print(f"rename_target_file = {self.__fl_rename_target_file}")
        self.debug_print(f"optimize_target_table = {self.__fl_optimize_target_table}")
        self.debug_print(f"vacuum_target_table = {self.__fl_vacuum_target_table}")

    def __validate_job_parameters(self, kwargs:dict) -> bool:
        if not kwargs:
            return False
        
        if not bool(self.__get(kwargs, "read_options")):
            return False

        return True

    # ^^^^^ PARAMETERS DEFINITION ^^^^^
    
    # vvvvv GENERIC METHODS vvvvv

    def __authenticate_in_microsoft_graph(self, tenant_id:str, client_id:str, client_secret:str) -> str:
        url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

        payload = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://graph.microsoft.com/.default"
        }

        response = requests.post(url, data=payload)

        if response.status_code != 200:
            raise requests.HTTPError(f"Error while authenticating: {response.text}")

        return response.json()["access_token"]

    def __execute_sql(self, sql_statement:str, print_statement=False, print_level=0, return_result=False):
        if print_statement:
            self.pprint(f"Executing statement: {sql_statement}", dots=0, lvl=print_level)
        try:
            result = spark.sql(sql_statement)
        except Exception as e:
            result = None
            print(f"{type(e).__name__}: {str(e)}")
            raise
        return result if return_result else None
    
    def __ftp_isdir(self, ftp_connection, path:str) -> bool:
        from ftplib import error_perm
        try:
            ftp_connection.cwd(path)
            return True
        except error_perm:
            return False

    def __get(self, kwargs:dict, key:str, default_value=None):
        keys = [k for k in kwargs.keys() if self.get_split_part(k) == key]
        if keys:
            return kwargs.get(keys[0], default_value)
        else:
            return default_value
    
    def __get_all_values_by_core_key(self, d:dict, key:str, default_value=None):
        merge_dicts = lambda a, b: a | b
        list_values = [v for k,v in d.items() if self.get_split_part(k) == key]

        if len(list_values) > 0 and list_values[0] == False:
            return False

        return reduce(merge_dicts, list_values) if list_values else default_value

    def create_empty_schema(self, kwargs):
        """
        Create an DataFrame Column with specific schema, based on 'kwargs'.

        # Relation:
        
        - {} -> StructType()
        - [] -> ArrayType()
        - "string" -> StringType()
        - "integer" -> IntegerType()
        [...]
        
        # Example input:
        
        input_schema = {
            "col_1": {
                "col_1_1": "string",
                "col_1_2": "integer"
            },
            "col_2": [
                {
                    "col_2_1": "date",
                    "col_2_2": "boolean"
                }
            ],
            "col_3": "timestamp",
            "col_4": ["string"]
        }
        df.withColumn("teste", create_empty_schema(input_schema))
        
        # output:

        root
        |-- teste: struct (nullable = false)
        |    |-- col_1: struct (nullable = false)
        |    |    |-- col_1_1: string (nullable = true)
        |    |    |-- col_1_2: integer (nullable = true)
        |    |-- col_2: array (nullable = false)
        |    |    |-- element: struct (containsNull = false)
        |    |    |    |-- col_2_1: date (nullable = true)
        |    |    |    |-- col_2_2: boolean (nullable = true)
        |    |-- col_3: timestamp (nullable = true)
        |    |-- col_4: array (nullable = false)
        |    |    |-- element: string (containsNull = true)
        
        """
        
        if isinstance(kwargs, dict):
            return F.struct(*[self.create_empty_schema(v).alias(k) for k,v in kwargs.items()])
        
        if isinstance(kwargs, list):
            return F.array(*[self.create_empty_schema(e) for e in kwargs])
        
        return F.lit(None).cast(kwargs or "string")

    def create_schema(self, args) -> T.StructType:
        """
        Create Spark schema from 'args'.
        Parameters:
        - args: The fields to create the schema. Can be list, string, dict or StructType.

        Dict example: # Each column in 'keys' will receive the type in 'value'. See help('create_empty_schema') for details.
            {"col_1": "string", "col_2": "integer", "col_3": "date"}

        List example: # All columns will be of type StringType().
            ["col_1", "col_2", "col_3"]
        
        String example: # All columns will be of type StringType().
            "col_1,col_2,col_3"
        
        StructType example: StructType([
                                StructField("col_1", StringType()),
                                StructField("col_2", IntegerType()),
                                StructField("col_3", DateType())
                            ])
        """

        self.debug_print(f"def CREATE_SCHEMA >> args = {args}")
        
        if isinstance(args, dict):
            return self.create_empty_schema(args)

        if isinstance(args, list):
            return T.StructType([T.StructField(col, T.StringType()) for col in args])

        if isinstance(args, str):
            return T.StructType([T.StructField(col.strip(), T.StringType()) for col in args.split(",")])
            
        if isinstance(args, T.StructType):
            return args
    
    def debug_print(self, obj) -> None:
        """
        Prints messages to help the debugging process.
        Parameters:
        - obj: The object to print
        """
        
        if self.debug_mode:
            if isinstance(obj, DataFrame):
                print(obj.show())
            else:
                print(f"DEBUG >> {str(obj)}")
    
    def drop_table(self, table_name:str) -> bool:
        """
        Removes the "table_name" and deletes its directory.
        Parameters:
        - table_name: The table to remove.
        """

        # get path from table
        table_path = self.__execute_sql(f"describe extended {table_name}", return_result=True).filter("col_name = 'Location'").select("data_type").head()[0]

        # drop table
        self.__execute_sql(f"drop table if exists {table_name}")

        # remove path
        dbutils.fs.rm(table_path, True)

        return True

    def get_secret(self, secret_name:str):
        """
        Gets value from 'secret_name' and return a dictionary
        Parameters:
        - secret_name: The secret in AWS Secrets Manager
        """
        
        self.debug_print(f"def GET_SECRET >> parameters >> secret_name={secret_name}")

        if not hasattr(self, "_IngestionJob__secrets"):
            self.__secrets = {}
        
        if self.__secrets.get(secret_name):
            return self.__secrets[secret_name]

        from ast import literal_eval
        from botocore.exceptions import ClientError
        from base64 import b64decode
        import boto3
        
        client = boto3.client(
            service_name="secretsmanager",
            region_name="us-east-1"
        )

        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
            self.debug_print(f"def GET_SECRET >> get_secret_value_response = {get_secret_value_response}")
        except ClientError as e:
            errors = {
                "DecryptionFailureException": "Secrets Manager can't decrypt the protected secret text using the provided KMS key.",
                "InternalServiceErrorException": "An error occurred on the server side.",
                "InvalidParameterException": "You provided an invalid value for a parameter.",
                "InvalidRequestException": "You provided a parameter value that is not valid for the current state of the resource.",
                "ResourceNotFoundException": "We can't find the resource that you asked for."
            }
            if e.response["Error"]["Code"] in list(errors):
                print(errors[e.response["Error"]["Code"]])
                raise e
                
        if "SecretString" in get_secret_value_response:
            secret_str = get_secret_value_response["SecretString"]
        else:
            secret_str = b64decode(get_secret_value_response["SecretBinary"])

        try:
            if isinstance(literal_eval(secret_str), dict):
                self.__secrets[secret_name] = literal_eval(secret_str)
            else:
                self.__secrets[secret_name] = secret_str
        except ValueError:
            self.__secrets[secret_name] = secret_str
        except Exception:
            return None

        return self.__secrets[secret_name]

    def get_split_part(self, s:str, d="-", p=0) -> str:
        """
        Get value in string splitting by delimiter and returning prefix or suffix.
        Parameters:
        - s: Key to find delimiter
        - d: Delimiter to split key (default = '-')
        - p: Part to return. 0: prefix, 1: suffix (default = 0)
        """

        parts = s.split(d,1)
        if p != 0 and len(parts) == 1:
            return ""
        else:
            return parts[p]

    #TODO: continuar a implementação em list_objects_by_env SFTP...
    def ls(self, path:str, env_type="dbfs", file_filter="", recursive=False, return_files=True, return_dirs=True, **kwargs) -> list:
        """
        Lists files and/or directories using dbutils.
        Parameters:
        - path: The directory to search
        - env_type: The type of environment to search in (can be: "dbfs"|"os"|"ftp") (default = "dbfs")
        - file_filter: Substring to filter filenames (default = empty)
        - recursive: Search subdirectories (default = False)
        - return_files: Return found files (default = True)
        - return_dirs: Return found directories (default = True)
        """

        self.debug_print(f"def LS >> parameters >> path={path}; \
                                                   env_type={env_type}; \
                                                   file_filter={file_filter}; \
                                                   recursive={recursive}; \
                                                   return_files={return_files}; \
                                                   return_dirs={return_dirs}; \
                                                   kwargs={kwargs}")

        elements = []

        list_objects_by_env = {
            "dbfs": lambda p: {x.path: "dir" if x.isDir() else "file" for x in dbutils.fs.ls(p)},
            "os": lambda p: {x: "dir" if os.path.isdir(x) else "file" for x in os.listdir(p)},
            "ftp": lambda p: {x: "dir" if self.__ftp_isdir(kwargs["connection"], x) else "file" for x in kwargs["connection"].nlst(p)},
            #"sftp": lambda p: {x: "dir" if ??? else "file" for x in kwargs["connection"].listdir(p)}
        }[env_type]
        
        objects = { k:v for k,v in list_objects_by_env(path).items() \
                        if (v == "dir" and (return_dirs or recursive)) or \
                            (v == "file" and return_files and file_filter.lower() in k.lower()) }

        for obj_path, obj_type in objects.items():
            elements.append(obj_path)

            if recursive and obj_type == "dir":
                elements += self.ls(obj_path, env_type, file_filter, recursive, return_files, return_dirs, **kwargs)

        return elements

    def now(self, fmt="%Y-%m-%d %H:%M:%S", timezone=None) -> str:
        """
        Returns the current timestamp in string format.
        Parameters:
        - fmt: The format of timestamp to return (default = %Y-%m-%d %H:%M:%S)
        - timezone: Timezone to apply on date (default = America/Sao_Paulo, i.e., GMT-3)
        """

        from datetime import datetime
        import pytz
        tz = pytz.timezone(timezone or "America/Sao_Paulo")
        return datetime.now(tz).strftime(fmt)

    def path_join(self, args:list, sep=None) -> str:
        """
        Join args by sep.
        Parameters:
        - args: List of values to join
        - sep: Char used to join the list of values (defaul = "/")
        """

        if sep is None:
            sep = "/"
        return sep.join([self.remove_last_slash(s) for s in args])

    def pprint(self, msg:str, lvl=0, dots=3, spaces=3, skip_line=False, return_msg=False) -> str:
        """
        Pretty print messages.
        Parameters:
        - msg: The message to print
        - lvl: Indent level (default = 0)
        - dots: The number of dots after message (default = 3)
        - spaces: Spaces per level (default = 3)
        - skip_line: Skip a line after the message (default = False)
        - return_msg: Return the message text (default = False)
        """
        
        ts = self.now()
        print(f"[{ts}] {'':<{spaces*lvl}}|-- {msg}{'.'*dots}")
        
        if skip_line:
            print()
        
        if return_msg is True:
            return msg
    
    def preprocess_secrets(self) -> None:
        """
        Processes the secrets used in ingestion. The result is stored internally. This method has no parameters.
        The list of secrets must be placed in "parameters" dictionary, inside the "common_secretes" structure.
        """
        
        self.debug_print("def PREPROCESS_SECRETS")

        for secret_name in self.__common_secrets:
            self.get_secret(secret_name)

    def rename_file(self, old:str, new:str) -> str:
        """
        Rename file from 'old' to 'new'.
        Parameters:
        - old: Current file path
        - new: New file path
        """
        
        self.debug_print(f"def RENAME_FILE >> parameters >> old={old}; new={new}")
        
        try:
            dbutils.fs.mv(old, new)
        except Exception as e:
            return str(e)
        else:
            return 'success'

    def remove_last_slash(self, s:str) -> str:
        """
        Remove the last slash from string.
        Parameters:
        - s: The string to remove last slash
        """
        
        self.debug_print(f"def REMOVE_LAST_SLASH >> parameters >> s={s}")
        
        return s[:-1] if s[-1] == "/" else s

    def to_list(self, p) -> list:
        """
        Checks the data type of 'p' and always returns a list (if the data type is not list then it is converted).
        Parameters:
        - p: The variable to check data type
        """
        
        self.debug_print(f"def TO_LIST >> parameters >> p={p}")
        self.debug_print(f"def TO_LIST >> type(p) = {type(p)}")
        
        return p if isinstance(p, list) else [p]

    def toggle_warnings(self, turn:bool=False):
        """
        Enable or disable warnings
        Parameters:
        - turn: False to disable, True to enable
        """

        import warnings

        mode = "ignore" if turn is False else "default"
        warnings.filterwarnings(mode)

    # ^^^^^ GENERIC METHODS ^^^^^

    # vvvvv READ DATA vvvvv

    def __read_data_from_delta(self, kwargs:dict, print_level=1) -> DataFrame:
        self.debug_print(f"def READ_DATA_FROM_DELTA >> kwargs = {kwargs}")
        return spark.read.table(kwargs["name"])

    #TODO: implementar este método
    def __read_data_from_excel(self, kwargs:dict, print_level=1) -> DataFrame:
        pass

    def __read_data_from_ftp(self, kwargs:dict, print_level=1) -> DataFrame:
        '''
        "format": "ftp" -> Indica que a ingestão será feita via FTP.
        "secret_name": [str, required] -> Nome da secret onde estão as informações de conexão.
        "name": [str, required] -> Nome do arquivo a procurar.
        "path": [str, optional] -> Pasta raiz. Default: pasta raiz da conexão
        "dirs: [list, optional] -> Lista de subpastas a procurar o arquivo. Default: pesquisar em todas as subpastas.
        '''
        self.debug_print(f"def READ_DATA_FROM_FTP >> kwargs = {kwargs}")

        from ftplib import FTP
        import io
        import pandas as pd

        accepted_options = ["host", "user", "passwd", "acct", "timeout", "source_address", "encoding"]
        connection_options = {k:v for k,v in kwargs.items() if k in accepted_options}
        self.debug_print(f"def READ_DATA_FROM_FTP >> connection_options = {connection_options}")

        self.pprint("Connecting to FTP server", lvl=print_level)
        with FTP(**connection_options) as ftp:
            root_path = kwargs.get("path") or ftp.pwd()
            
            self.pprint("Getting list of directories to search in", lvl=print_level)
            directories = [ d for d in self.ls(root_path, env_type="ftp", return_files=False, connection=ftp) \
                                if any(x in d for x in kwargs.get("dirs",[])) ] or [root_path]
            self.debug_print(f"def READ_DATA_FROM_FTP >> directories = {directories}")

            self.pprint("Searching for files", lvl=print_level)
            files = []
            for path in directories:
                files += [f for f in self.ls(path, env_type="ftp", recursive=True, return_dirs=False, connection=ftp) if re.search(kwargs["name"], f)]
            self.debug_print(f"def READ_DATA_FROM_FTP >> files = {files}")

            self.pprint("Getting files in FTP server", lvl=print_level)
            spark_dfs = []
            for source_file in files:
                self.pprint(source_file, lvl=print_level+1)
                output_bytes = io.BytesIO()
                ftp.retrbinary(f"RETR {source_file}", output_bytes.write)
                output_str = io.StringIO(output_bytes.getvalue().decode("utf-8-sig"))
                pandas_args = {k:v for k,v in kwargs.items() if k not in ["format", "secret_name", "name", "path", "dirs"] and k not in accepted_options}
                pandas_df = pd.read_csv(output_str, **pandas_args)
                spark_dfs.append(spark.createDataFrame(pandas_df))
                output_bytes.close()
                output_str.close()

        self.pprint("Converting data to Spark DataFrame", lvl=print_level)
        union_dataframes_by_name = lambda df1, df2: df1.unionByName(df2, allowMissingColumns=True)
        return reduce(union_dataframes_by_name, spark_dfs)

    def __read_data_from_query(self, kwargs:dict, print_level=1) -> DataFrame:
        self.debug_print(f"def READ_DATA_FROM_QUERY >> kwargs = {kwargs}")
        return self.__execute_sql(kwargs["query"], True, print_level, True)

    def __read_data_from_sap(self, kwargs:dict, print_level=1) -> DataFrame:
        self.debug_print(f"def READ_DATA_FROM_SAP >> kwargs = {kwargs}")
        
        import pyrfc as sap
        
        conn = None
        
        try:

            self.pprint("Connecting to SAP", lvl=print_level)
            connection_options = {k:v for k,v in kwargs.items() if k in ["user", "passwd", "client", "lang", "mshost", "msserv", "sysid", "group"]}
            self.debug_print(f"def READ_DATA_FROM_SAP >> connection_options = {connection_options}")
            conn = sap.Connection(**connection_options)
            
            data = []
            fetch_rows = kwargs.get("fetchrows", 1000000)
            total_rows = kwargs.get("rowcount")
            remaining_rows = total_rows
            self.debug_print(f"def READ_DATA_FROM_SAP >> fetch_rows = {fetch_rows}")
            self.debug_print(f"def READ_DATA_FROM_SAP >> total_rows = {total_rows}")
            
            call_parameters = {
                "func_name": "RFC_READ_TABLE",
                "QUERY_TABLE": kwargs["table_name"],
                "DELIMITER": kwargs.get("delimiter", "|"),
                "FIELDS": [{"FIELDNAME": f} for f in kwargs["fields"]],
                "OPTIONS": [{"TEXT": o} for o in kwargs.get("options", [])],
                "ROWCOUNT": min(fetch_rows, total_rows) if total_rows else fetch_rows,
                "ROWSKIPS": kwargs.get("rowskips", 0)
            }
            self.debug_print(f"def READ_DATA_FROM_SAP >> call_parameters = {call_parameters}")
            
            self.pprint("Calling sap RFC_READ_TABLE function", lvl=print_level)
            while True:
                response = conn.call(**call_parameters)
                self.debug_print(f"def READ_DATA_FROM_SAP >> response = {response}")

                data += response.get("DATA", [])

                if len(response.get("DATA", [])) < call_parameters["ROWCOUNT"]:
                    # There are no more rows to return
                    self.debug_print("def READ_DATA_FROM_SAP >> break: len(response['DATA']) < call_parameters['ROWCOUNT']")
                    break

                if len(data) == total_rows:
                    # Total number of rows reached
                    self.debug_print("def READ_DATA_FROM_SAP >> break: len(data) < total_rows")
                    break
                
                call_parameters["ROWSKIPS"] += call_parameters["ROWCOUNT"]

                if total_rows:
                    remaining_rows -= call_parameters["ROWCOUNT"]
                    call_parameters["ROWCOUNT"] = min(fetch_rows, remaining_rows)
                    self.debug_print(f"def READ_DATA_FROM_SAP >> remaining_rows = {remaining_rows}")
                
                self.debug_print(f"def READ_DATA_FROM_SAP >> call_parameters = {call_parameters}")
        
        finally:
            if conn:
                conn.close()
        
        if data:
            self.pprint("Transforming response data in Spark DataFrame", lvl=print_level)
            df = spark.createDataFrame(data)
            split_col = F.split(df["WA"], re.escape(kwargs.get("delimiter", "|")))
            df = df.select(*[split_col.getItem(i).alias(col_name) for i, col_name in enumerate(kwargs["fields"])])
            return df
        else:
            schema = self.create_schema(kwargs["fields"])
            return spark.createDataFrame([], schema)
    
    #TODO: implementar este método
    def __read_data_from_sftp(self, kwargs:dict, print_level=1) -> DataFrame:
        # import paramiko
        # obter secret AWS
        # connection_options = self.get_secret(kwargs["secret_name"])

        # conectar no SFTP
        # transport = paramiko.Transport(connection_options["host"], connection_options["port"])
        # private_key = paramiko.RSAKey.from_private_key_file(
        #     filename=connection_options["privatekeylocation"].replace("s3://", "/dbfs/mnt"),
        #     password=connection_options["privatekeypassword"]
        # )
        # transport.connect(
        #     username=connection_options["sftpuser"],
        #     pkey=private_key
        # )
        # sftp = paramiko.SFTPClient.from_transport(transport)
    
        # mudar o diretório p/ root_path (opcional)
        # sftp.chdir(connection_options["remoteprefix"])

        # listar os arquivos
        # files = sftp.listdir()

        # filtrar os arquivos
        # percorrer os arquivos:
            # baixar o arquivo para pasta temporária (ou em memória)
            # enviar para o S3
        pass

    def __read_data_from_sharepoint(self, kwargs:dict, print_level=1) -> DataFrame:
        self.debug_print(f"def READ_DATA_FROM_SHAREPOINT >> kwargs = {kwargs}")

        from io import BytesIO
        import pandas as pd

        kwargs.pop("format", None)

        tenant_id = kwargs.pop("tenant_id", None)
        client_id = kwargs.pop("client_id", None)
        client_secret = kwargs.pop("client_secret", None)

        if not all([tenant_id, client_id, client_secret]):
            raise ValueError("Missing required parameters in secret: tenant_id, client_id, client_secret")

        self.pprint("Authenticating with Microsoft Graph", lvl=print_level)
        token = self.__authenticate_in_microsoft_graph(tenant_id, client_id, client_secret)

        s = requests.Session()
        s.headers.update({"Authorization": f"Bearer {token}"})

        self.pprint("Splitting input URL to make the API calls in Microsoft Graph", lvl=print_level)
        input_url = kwargs.pop("url", None)

        if not input_url:
            raise ValueError("Missing required parameter: url")

        url_parts = input_url.split("/")
        host_name = url_parts[2]
        site_name = "/".join(url_parts[3:5])
        drive_name = url_parts[5]
        file_name = "/".join(url_parts[6:])
        file_extension = file_name.split(".")[-1].lower()

        self.pprint("Getting site ID from Microsoft Graph", lvl=print_level+1)
        site_url = f"https://graph.microsoft.com/v1.0/sites/{host_name}:/{site_name}"
        site_resp = s.get(site_url)
        site_id = site_resp.json()["id"]

        if not site_id:
            raise requests.HTTPError(f"Site not found: {site_name}")

        self.pprint("Getting drive ID from Microsoft Graph", lvl=print_level+1)
        drive_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
        drive_resp = s.get(drive_url)

        for d in drive_resp.json()["value"]:
            if d["webUrl"].endswith(drive_name):
                drive_id = d["id"]

        if not drive_id:
            raise requests.HTTPError(f"Drive not found: {drive_name}")

        self.pprint("Getting item ID from Microsoft Graph", lvl=print_level+1)
        item_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{file_name}"
        item_resp = s.get(item_url)
        item_id = item_resp.json()["id"]

        if not item_id:
            raise requests.HTTPError(f"File not found: {file_name}")

        self.pprint("Downloading file content from Microsoft Graph", lvl=print_level)
        download_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/content"
        download_resp = s.get(download_url)
        file_bytes = BytesIO(download_resp.content)

        if download_resp.status_code != 200:
            raise requests.HTTPError(f"Error while downloading file: {download_resp.text}")

        self.pprint("Reading file content with Pandas", lvl=print_level)
        read_method = None
        if file_extension in ("csv"):
            read_method = pd.read_csv
        elif file_extension in ("xlsx", "xls", "xlsm", "xltx", "xltm", "xlsb"):
            read_method = pd.read_excel
        
        if not read_method:
            raise ValueError(f"File extension not supported: {file_extension}")

        file_bytes.seek(0)
        pandas_df = read_method(file_bytes, **kwargs)

        self.pprint("Converting Pandas DataFrame to Spark DataFrame", lvl=print_level)
        spark_df = spark.createDataFrame(pandas_df)

        return spark_df

    def __read_data_from_spark(self, kwargs:dict, print_level=1) -> DataFrame:
        return spark.read.load(**kwargs)

    def process_parallel_read(self, max_workers:int=None) -> None:
        """
        Process all readings in parallel to reduce the final execution time.
        Parameters:
        - max_workers: Number of simultaneous threads. Default is None (then the class concurrent.futures calculates the best value).
        The settings must be placed in "parameters" dictionary, inside the "parallel_read" structure, where:
        - each key corresponds to an identifier
        - each value corresponds to the reading options
        These identifiers will be used as values for the "read_options" keys throughout the parameter dictionary.
        """

        self.debug_print("def PROCESS_PARALLEL_READ")
        self.debug_print(f"def PROCESS_PARALLEL_READ >> parameters >> max_workers={max_workers}")

        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_options = {}
            for key, options in self.__parallel_read_options.items():
                future = executor.submit(self.read_data, options)
                future_options[future] = key

            for future in as_completed(future_options):
                current_key = future_options[future]
                results[current_key] = future.result()
        
        self.__parallel_completed = results

    def read_data(self, read_options=None, latest_only=False, partition_column="dt_ingestion", print_level=0) -> DataFrame:
        """
        Reads the data and returns a DataFrame.
        Parameters:
        - read_options: Dict with options to read the data. Can be passed by parameter or at class initialization. For more details see README or help().
        - latest_only: Gets data filtering last partition of the table (sorting in descending order).
        - partition_column: Column used to filter last partition (default = dt_ingestion).
        """

        self.pprint("Reading Spark DataFrame", lvl=print_level)
        self.debug_print(f"read_options: {read_options}")
        self.debug_print(f"latest_only: {latest_only}")
        self.debug_print(f"partition_column: {partition_column}")

        if read_options:
            read_options = self.__get_read_options(read_options)
        else:
            read_options = deepcopy(self.__read_options)
            latest_only = self.__fl_latest_partition_only
            partition_column = self.__partition_column
        
        if self.__fl_parallel and isinstance(read_options, str):
            return self.__parallel_completed[read_options]

        methods = {
            "delta": self.__read_data_from_delta,
            # "excel": self.__read_data_from_excel, #TODO: Habilitar aqui após implementar o método
            "ftp": self.__read_data_from_ftp,
            "query": self.__read_data_from_query,
            "sap": self.__read_data_from_sap,
            "sftp": self.__read_data_from_sftp,
            "sharepoint": self.__read_data_from_sharepoint
        }
        read_method = methods.get(read_options.get("format"), self.__read_data_from_spark)
        
        df = read_method(read_options, print_level=print_level+1)
        
        if self.debug_mode:
            df.cache() # Prevents errors from some JDBC sources when debug_mode is True
        
        if latest_only:
            self.pprint("Filtering last partition", lvl=print_level)
            max_partition = df.agg({partition_column: "max"}).collect()[0][0]
            df = df.filter(F.col(partition_column) == F.lit(max_partition))
        
        if not self.__dataframe_columns:
            self.__dataframe_columns = df.columns
        
        self.debug_print(df)
        return df
    
    # ^^^^^ READ DATA ^^^^^

    # vvvvv TRANSFORMATIONS vvvvv

    def aggregate(self, df:DataFrame, args:dict, print_level=1, comment=None) -> DataFrame:
        """
        Groups the DataFrame by "group_by" list, calculating "agg" expressions.
        Parameters:
        - df: The DataFrame to aggregate
        - args: Dict containing the following keys:
                * group_by: list of columns to group the data
                * agg: dict of expressions, where the keys are the column names and the values are the expressions.
        """

        self.pprint("Grouping dataframe" + (f" ({comment})" if comment != "" else ""), lvl=print_level)
        self.debug_print(f"def AGGREGATE >> args = {args}")
        self.debug_print(df)
        df_grouped = df.groupBy(*args["group_by"])
        df = df_grouped.agg(*[F.expr(expression).alias(column) for column, expression in args["agg"].items()])
        return df

    def cast(self, df:DataFrame, args:dict, print_level=1, comment=None) -> DataFrame:
        """
        Change the data types of columns.
        Parameters:
        - df: The DataFrame to cast columns.
        - args: A dict where each key represents the data type (string, date, integer, etc.)
                and each value must be a list of columns to cast.
        """
        
        self.pprint("Converting datatypes" + (f" ({comment})" if comment != "" else ""), lvl=print_level)
        self.debug_print(f"def CAST >> args = {args}")
        self.debug_print(df)
        for data_type, cols_to_cast in args.items():
            for c in cols_to_cast:
                df = df.withColumn(c, F.col(c).cast(data_type))
        return df

    def col_names(self, df:DataFrame, args:list, print_level=1, comment=None) -> DataFrame:
        """
        Renames all columns of DataFrame by position.
        The length of "args" must be equal to the lengh of the columns of DataFrame.
        Parameters:
        - df: The DataFrame to rename.
        - args: A list containing new column names.
        """
        
        self.pprint("Renaming all columns" + (f" ({comment})" if comment != "" else ""), lvl=print_level)
        self.debug_print(f"def COL_NAMES >> args = {args}")
        self.debug_print(df)
        return df.toDF(*args)

    def distinct(self, df:DataFrame, *_, print_level=1, comment=None) -> DataFrame:
        """
        Removes duplicated rows, based on all columns in the DataFrame.
        Parameters:
        - df: The DataFrame to remove duplicates.
        """
        
        self.pprint("Removing duplicated rows in dataframe" + (f" ({comment})" if comment != "" else ""), lvl=print_level)
        return df.distinct()

    def drop(self, df:DataFrame, args:list, print_level=1, comment=None) -> DataFrame:
        """
        Removes specific columns from DataFrame.
        Parameters:
        - df: The DataFrame to remove columns.
        - args: A list of columns to remove.
        """
        
        self.pprint("Removing specific columns" + (f" ({comment})" if comment != "" else ""), lvl=print_level)
        self.debug_print(f"def DROP >> args = {args}")
        self.debug_print(df)
        return df.drop(*args)

    def filter(self, df:DataFrame, args:list, print_level=1, comment=None) -> DataFrame:
        """
        Filter rows of DataFrame.
        Parameters:
        - df: The DataFrame to filter.
        - args: A list of expressions to apply filters.
        """
        
        self.pprint("Applying filters" + (f" ({comment})" if comment != "" else ""), lvl=print_level)
        self.debug_print(f"def FILTER >> args = {args}")
        self.debug_print(df)
        for clause in args:
            df = df.filter(clause)
        return df

    def join(self, df:DataFrame, args:dict, print_level=1, comment=None) -> DataFrame:
        """
        Joins two DataFrames using "args" rules.
        Parameters:
        - df: The primary DataFrame used in join
        - args: A dict containing the rules to join:
                * on: The key(s) to match the DataFrames.
                * how: The mode of join, like "inner", "left", "right", etc. (defaul = "inner").
                * read_options: Dict with options to read the data of second DataFrame.
                * args also accepts all transformations to apply on second DataFrame before performs join.
        """
        
        self.pprint("Join dataframe" + (f" ({comment})" if comment != "" else ""), lvl=print_level)
        self.debug_print(f"def JOIN >> args = {args}")
        self.debug_print(df)

        on_clause = args.pop("on", None)
        how_clause = args.pop("how", None)
        new_df = self.read_data(self.__get(args, "read_options"), print_level=print_level+1)
        new_df = self.transformations(new_df, args, print_level=print_level+1)
        self.pprint("Performing join", lvl=print_level+1)
        return df.join(new_df, on_clause, how_clause)

    def order_by(self, df:DataFrame, args:dict, print_level=1, comment=None) -> DataFrame:
        """
        Sorts the rows of DataFrame using "args" rules.
        Parameters:
        - df: The DataFrame to sort.
        - args: A dict where each key corresponds to the column to be sorted
                and each value corresponds to the sorting method (asc or desc).
        """
        
        self.pprint("Sorting dataframe" + (f" ({comment})" if comment != "" else ""), lvl=print_level)
        self.debug_print(f"def SORT >> args = {args}")
        self.debug_print(df)
        return df.sort(*[getattr(F.col(column), method)() for column, method in args.items()])

    def rename(self, df:DataFrame, args:dict, print_level=1, comment=None) -> DataFrame:
        """
        Renames specific columns of DataFrame.
        Parameters:
        - df: The DataFrame to rename columns.
        - args: A dict containing the key:value pairs indicating old_value:new_value.
        """
        
        self.pprint("Renaming specific columns" + (f" ({comment})" if comment != "" else ""), lvl=print_level)
        self.debug_print(f"def RENAME >> args = {args}")
        self.debug_print(df)
        for old_col, new_col in args.items():
            df = df.withColumnRenamed(old_col, new_col)
        return df

    def repartition(self, df:DataFrame, args, print_level=1, comment=None) -> DataFrame:
        """
        Repartition DataFrame files using "args" rules.
        Parameters:
        - df: The DataFrame to repartition.
        - args: A list indicating the rules to repartition the data (usually a number).
        """
        
        self.pprint("Repartitioning dataframe" + (f" ({comment})" if comment != "" else ""), lvl=print_level)
        self.debug_print(f"def REPARTITION >> args = {args}")
        self.debug_print(df)
        return df.repartition(*self.to_list(args))

    def remove_accents(self, df:DataFrame, args:list, print_level=1, comment=None) -> DataFrame:
        """
        Removes accents and cedilla from the data in "args" columns.
        Parameters:
        - df: The DataFrame to apply the transformation.
        - args: A list of columns to apply.
        """
        
        self.pprint("Removing accents" + (f" ({comment})" if comment != "" else ""), lvl=print_level)
        self.debug_print(f"def REMOVE ACCENTS >> args = {args}")
        self.debug_print(df)
        for col in args:
            df = df.withColumn(col, F.expr(f"translate({col},'àáâãèéêìíîòóôõùúûüçÀÁÂÃÈÉÊÌÍÎÒÓÔÕÙÚÛÜÇ','aaaaeeeiiioooouuuucAAAAEEEIIIOOOOUUUUC')"))
        return df

    def select(self, df:DataFrame, args:list, print_level=1, comment=None) -> DataFrame:
        """
        Selects specific columns of DataFrame.
        Parameters:
        - df: The DataFrame to select columns.
        - args: A list of columns or expressions.
        """
        
        self.pprint("Selecting specific columns" + (f" ({comment})" if comment != "" else ""), lvl=print_level)
        self.debug_print(f"def SELECT >> args = {args}")
        self.debug_print(df)
        return df.selectExpr(*args)

    def transform(self, df:DataFrame, args:dict, print_level=1, comment=None) -> DataFrame:
        """
        Apply transformations in data by "args" expressions.
        Parameters:
        - df: The DataFrame to apply the transformations.
        - args: A dict where each key represents the column name (existing or new) and each value represents the expression.
        """
        
        self.pprint("Transforming columns" + (f" ({comment})" if comment != "" else ""), lvl=print_level)
        self.debug_print(f"def TRANSFORM >> args = {args}")
        self.debug_print(df)
        for col, expression in args.items():
            df = df.withColumn(col, F.expr(expression))
        return df

    def trim_cols(self, df:DataFrame, args, print_level=1, comment=None) -> DataFrame:
        """
        Trim the data in DataFrame, using "args" rules.
        Parameters:
        - df: The DataFrame to trim.
        - args: Can be a dict containing the rules, a list of columns, or None.
                If args is not a dict, the default values below will be applied.
                Accepted keys:
                * mode: both | leading | trailing (default = "both")
                * columns: The list of columns to trim (default = All columns)
                * trim_str: The char(s) to trim (defaul is a single space)
        """
        
        self.pprint("Trim cols" + (f" ({comment})" if comment != "" else ""), lvl=print_level)
        self.debug_print(f"def TRIM_COLS >> args = {args}")
        self.debug_print(df)

        if isinstance(args, dict):
            args["mode"] = args.get("mode", "both")
            args["columns"] = args.get("columns", df.columns)
        else:
            args = {
                "mode": "both",
                "columns": args if isinstance(args, list) else df.columns
            }
        args["trim_str"] = f"'{args['trim_str']}'" if args.get("trim_str") else ""
        
        for col in args["columns"]:
            df = df.withColumn(col, F.expr(f"trim({args['mode']} {args['trim_str']} from {col})"))

        return df

    def union(self, df:DataFrame, args:dict, print_level=1, comment=None) -> DataFrame:
        """
        Unites two DataFrames by column position.
        Parameters:
        - df: The primary DataFrame used in union
        - args: A dict containing the rules to perform union:
                * read_options: Dict with options to read the data of second DataFrame.
                * args also accepts all transformations to apply on second DataFrame before performs union.
        """
        
        self.pprint("Union dataframes by position" + (f" ({comment})" if comment != "" else ""), lvl=print_level)
        self.debug_print(f"def UNION >> args = {args}")
        self.debug_print(df)

        new_df = self.read_data(self.__get(args, "read_options"), print_level=print_level+1)
        new_df = self.transformations(new_df, args, print_level=print_level+1)
        self.pprint("Performing union by position", lvl=print_level+1)
        return df.union(new_df)

    def union_by_name(self, df:DataFrame, args:dict, print_level=1, comment=None) -> DataFrame:
        """
        Unites two DataFrames by column name.
        Parameters:
        - df: The primary DataFrame used in union
        - args: A dict containing the rules to perform union:
                * read_options: Dict with options to read the data of second DataFrame.
                * args also accepts all transformations to apply on second DataFrame before performs union.
        """
        
        allow_missing_columns = args.get("allow_missing_columns", False)
        
        self.pprint("Union dataframes by name" + (f" ({comment})" if comment != "" else ""), lvl=print_level)
        self.debug_print(f"def UNION_BY_NAME >> args = {args}")
        self.debug_print(f"def UNION_BY_NAME >> allow_missing_columns = {allow_missing_columns}")
        self.debug_print(df)

        new_df = self.read_data(self.__get(args, "read_options"), print_level=print_level+1)
        new_df = self.transformations(new_df, args, print_level=print_level+1)
        self.pprint("Performing union by name", lvl=print_level+1)
        return df.unionByName(new_df, allowMissingColumns=allow_missing_columns)

    def transformations(self, df:DataFrame, transformations_options:dict=None, print_level=0) -> DataFrame:
        """
        Apply one or more transformations to the data.
        Parameters:
        - df: The DataFrame to perform transformations.
        - transformations_options: A dict where each key corresponds to the function name (more detail below)
                                   and each value corresponds to the function parameters.
        Accepted transformations:
        - aggregate
        - cast
        - col_names
        - data_quality
        - distinct
        - drop
        - filter
        - join
        - order_by
        - rename
        - repartition
        - remove_accents
        - select
        - transform
        - trim_cols
        - union
        - union_by_name
        """

        if not transformations_options:
            transformations_options = self.parameters
        
        self.pprint("Dataframe transformations", lvl=print_level)
        self.debug_print(f"DEF transformations >> transformations_options = {transformations_options}")
        self.debug_print(df)
        
        accepted_transformations = [
            "aggregate",
            "cast",
            "col_names",
            "data_quality",
            "distinct",
            "drop",
            "filter",
            "join",
            "order_by",
            "rename",
            "repartition",
            "remove_accents",
            "select",
            "transform",
            "trim_cols",
            "union",
            "union_by_name"
        ]
        
        filtered_transformations = {k:v for k,v in transformations_options.items() if self.get_split_part(k) in accepted_transformations}
        self.debug_print(f"DEF transformations >> accepted_transformations = {accepted_transformations}")
        self.debug_print(f"DEF transformations >> filtered_transformations = {filtered_transformations}")

        for function_name, args in filtered_transformations.items():
            comment = self.get_split_part(function_name, p=1)
            function_name = self.get_split_part(function_name)
            df = getattr(self, function_name)(df, args, print_level=print_level+1, comment=comment)
        
        return df
    
    # ^^^^^ TRANSFORMATIONS ^^^^^

    # vvvvv DATA QUALITY vvvvv

    def __set_quarantine_options(self) -> dict:
        spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", True)

        quarantine_options = deepcopy(self.__read_options)

        if quarantine_options["format"] == "delta":
            catalog = quarantine_options["name"].split('.')[0]
            database = quarantine_options["name"].split('.')[1]
            table = quarantine_options["name"].split('.')[2]
            
            # If "path" is None, then get this information from table details in Delta Lake
            if not quarantine_options.get("path"):
                self.__execute_sql(f"use catalog {catalog}")
                self.__execute_sql(f"use database {database}")
                extended_info = self.__execute_sql(f"show table extended like '{table}'", return_result=True).select("information").collect()[0][0]
                quarantine_options["path"] = [row.replace("Location: ", "") for row in extended_info.split("\n") if "Location" in row][0]
            
            quarantine_options["name"] = f"{catalog}.{database}_quarantine.{table}"
            quarantine_options["mergeSchema"] = "true"
        else:
            quarantine_options["format"] = "parquet"
        
        quarantine_options["path"] = "/".join(quarantine_options["path"].split("/")[:3] + ["quarantine"] + quarantine_options["path"].split("/")[3:])
        quarantine_options["mode"] = "append"
        
        self.debug_print(f"Quarantine options: {quarantine_options}")
        return quarantine_options

    def __data_quality_convert_expectations_to_gx_format(self, args:dict) -> list:
        gx_expectations = []
        for exp in args["expectations"]:
            expectation_name = exp["expectation_type"].title().replace("_","")
            expectation_params = exp["kwargs"] | {"meta": exp["meta"]}
            expectation = getattr(gx.expectations, expectation_name)(**expectation_params)
            gx_expectations.append(expectation)
        return gx_expectations

    def __data_quality_fix_expectations(self, args:dict) -> dict:
        expectations = deepcopy(args)
        for ex in expectations["expectations"]:
            ex["kwargs"]["result_format"] = "COMPLETE"
            if not ex.get("meta"):
                ex["meta"] = {}
            if not ex["meta"].get("level"):
                ex["meta"]["level"] = "error"
        return expectations
    
    def __data_quality_process_failed_expectation(self, ex:dict, original_df:DataFrame, quarantine_df:DataFrame, quarantine_options:dict, print_level:int) -> DataFrame:
        success_clauses = []
        quarantine_clauses = []
        has_none = bool([val for val in ex["unexpected_list"] if val is None])
        has_not_none = bool([val for val in ex["unexpected_list"] if val is not None])
        
        if has_none:
            success_clauses.append(f"{ex['column']} is not null")
            quarantine_clauses.append(f"{ex['column']} is null")
        
        if has_not_none:
            list_without_none_value = [f'''"{val}"''' for val in ex["unexpected_list"] if val is not None]
            success_clauses.append(f"nvl({ex['column']},'-9999') not in ({','.join(list_without_none_value)})")
            quarantine_clauses.append(f"{ex['column']} in ({','.join(list_without_none_value)})")
        
        success_filter = self.__AND__.join(success_clauses)
        quarantine_filter = self.__OR__.join(quarantine_clauses)
        
        self.debug_print(f"def DATA_QUALITY >> success_clauses = {success_clauses}")
        self.debug_print(f"def DATA_QUALITY >> quarantine_clauses = {quarantine_clauses}")
        self.debug_print(f"def DATA_QUALITY >> has_none = {has_none}")
        self.debug_print(f"def DATA_QUALITY >> has_not_none = {has_not_none}")
        self.debug_print(f"def DATA_QUALITY >> success_filter = {success_filter}")
        self.debug_print(f"def DATA_QUALITY >> quarantine_filter = {quarantine_filter}")
        
        self.pprint("Saving failed values in quarantine", lvl=print_level)
        quarantine_df = quarantine_df.withColumn("quarantine_date", F.expr("current_timestamp()"))
        quarantine_df = quarantine_df.withColumn("expectation_failed", F.lit(ex["expectation"]))
        quarantine_df = quarantine_df.withColumn("column_failed", F.lit(ex["column"]))
        quarantine_df = quarantine_df.withColumn("table_failed", F.lit(ex["table_name"]))
        quarantine_df = quarantine_df.withColumn("expectation_level", F.lit(ex["level"]))
        
        if quarantine_options["format"] == "delta":
            try:
                quarantine_df.filter(quarantine_filter).write.saveAsTable(**quarantine_options)
            except E.captured.AnalysisException as e:
                if "DELTA_FAILED_TO_MERGE_FIELDS" in str(e):
                    self.pprint("Error on merge data. Overwriting instead", lvl=print_level+1)
                    overwrite_options = {
                        "mode": "overwrite",
                        "overwriteSchema": "true"
                    }
                    quarantine_df.filter(quarantine_filter).write.saveAsTable(**quarantine_options | overwrite_options)
        else:
            quarantine_df.filter(quarantine_filter).write.save(**quarantine_options)
        self.pprint("Data successfully quarantined", lvl=print_level+1, dots=1)
        
        if ex["level"] == "error":
            self.pprint("Removing invalid values from original dataframe", lvl=print_level)
            original_df = original_df.filter(success_filter)
        
        return original_df

    def __data_quality_run_validation(self, df:DataFrame, args:list) -> dict:
        context = gx.get_context(mode="ephemeral") # in memory

        definitions = context\
                        .data_sources.add_spark(name="gx_data_source_spark")\
                        .add_dataframe_asset(name="gx_dataframe_asset")\
                        .add_batch_definition_whole_dataframe(name="gx_batch_definition_dataframe")

        suite = context.suites.add(
            gx.ExpectationSuite(name="gx_expectation_suite", expectations=args)
        )

        validation = context.validation_definitions.add(
            gx.ValidationDefinition(name="gx_validation_definition", data=definitions, suite=suite)
        )

        validation_results = validation.run(batch_parameters={"dataframe": df})
        
        return validation_results

    def __data_quality_transform_failed_result(self, r:dict, quarantine_path:str, print_level:int) -> dict:
        # If fail in this expectation, raise an exception
        if r['expectation_config']['type'] == "expect_table_columns_to_match_ordered_list":
            unexpected_columns = [val["Expected"] if val["Expected"] else val["Found"] for val in r["result"]["details"]["mismatched"]]
            msg = self.pprint(f"The table structure doesn't match. Unexpected column(s): {unexpected_columns}", lvl=print_level+1, dots=0, return_msg=True)
            raise AttributeError(msg)
        
        if r['expectation_config']['type'] == "expect_column_distinct_values_to_be_in_set":
            # Creates the 'unexpected_list' with the difference between 'observed_value' and 'value_set' lists
            r["result"]["unexpected_list"] = [val for val in self.to_list(r["result"]["observed_value"]) if val not in r["expectation_config"]["kwargs"]["value_set"]]
        
        if r["result"].get("unexpected_list"):
            unexpected_list = r["result"].get("unexpected_list")
        elif r["result"].get("partial_unexpected_list"):
            unexpected_list = r["result"].get("partial_unexpected_list")
        else:
            unexpected_list = None

        return {
            "expectation": r['expectation_config']['type'],
            "column": r['expectation_config']['kwargs']['column'],
            "unexpected_list": list(set(unexpected_list)),
            "table_name": self.remove_last_slash(quarantine_path).split("/")[-1],
            "level": r["expectation_config"]["meta"]["level"]
        }

    def data_quality(self, df:DataFrame, args:dict, print_level=1, comment=None):
        """
        Checks the quality of the data using validation rules.
        Parameters:
        - df: The DataFrame to validate
        - args: A dict containg the following rules:
                * query: A SQL query to validate instead "df".
                * expectation_suite_name: A string used to identify the set of validation rules.
                * expectations: The list of expectations to check in the data. Each expectation is a dict containing:
                  * expectation_name: The name of expectation.
                  * kwargs: Expectation parameters.
        For more detail, see https://greatexpectations.io/expectations/
        """
        
        self.pprint("Data Quality" + (f" ({comment})" if comment != "" else ""), lvl=print_level)
        quarantine_options = self.__set_quarantine_options()

        self.debug_print(f"def DATA_QUALITY >> args = {args}")
        self.debug_print(f"def DATA_QUALITY >> quarantine_options = {quarantine_options}")
        self.debug_print(df)

        gx_query = args.pop("query", None)
        if gx_query:
            quarantine_df = self.__execute_sql(gx_query, True, print_level+1, True)
        else:
            quarantine_df = df

        self.pprint("Fixing all expectations with default arguments", lvl=print_level+1)
        args = self.__data_quality_fix_expectations(args)
        self.debug_print(f"def DATA_QUALITY >> args = {args}")

        self.pprint("Convert expectations to Great Expectations format", lvl=print_level+1)
        gx_args = self.__data_quality_convert_expectations_to_gx_format(args)
        self.debug_print(f"def DATA_QUALITY >> gx_expectations = {gx_args}")
        
        self.pprint("Running data quality validation on DataFrame", lvl=print_level+1)
        validation_results = self.__data_quality_run_validation(quarantine_df, gx_args)
        self.debug_print(f"def DATA_QUALITY >> validation_results = {validation_results}")

        if validation_results["success"] == True:
            self.pprint("Data quality valitation success", lvl=print_level+2, dots=1)
            return df

        self.pprint("Data Quality valitation failure", lvl=print_level+2, dots=1)

        self.pprint("Getting failed results", lvl=print_level+1)
        failed_results = [r for r in validation_results["results"] if r["success"] == False]
        self.debug_print(f"def DATA_QUALITY >> failed_results = {failed_results}")

        self.pprint("Treating the failed expectations", lvl=print_level+1)
        for r in failed_results:
            ex = self.__data_quality_transform_failed_result(r, quarantine_options["path"], print_level+1)
            
            self.pprint(f"Expectation '{ex['expectation']}' failed on column '{ex['column']}'", lvl=print_level+2, dots=1)
            self.pprint(f"Unexpected values: {ex['unexpected_list']}", lvl=print_level+3, dots=0)

            df = self.__data_quality_process_failed_expectation(ex, df, quarantine_df, quarantine_options, print_level+1)
        
        return df

    # ^^^^^ DATA QUALITY ^^^^^

    # vvvvv WRITE DATA vvvvv

    def __get_delta_write_mode_options(self, write_mode:str) -> dict:
        write_mode_options = {
            "overwrite": {
                "create_mode": "replace",
                "with_data": True
            },
            "replace": {
                "create_mode": "if_not_exists",
                "with_data": False,
                "insert_mode": "overwrite"
            },
            "append": {
                "create_mode": "if_not_exists",
                "with_data": False,
                "insert_mode": "into"
            },
            "merge": {
                "create_mode": "if_not_exists",
                "with_data": False,
                "merge": True
            },
            "delete_insert": {
                "create_mode": "if_not_exists",
                "with_data": False,
                "delete": True,
                "insert_mode": "into"
            },
            "ignore": {
                "create_mode": "if_not_exists",
                "with_data": True
            },
            "error": {
                "create_mode": "default",
                "with_data": True
            }
        }
        write_mode_options["errorifexists"] = write_mode_options["error"]
        write_mode_options["mode"] = write_mode
        return write_mode_options[write_mode]

    def __prepare_create_statement(self, create_mode:str, with_data:bool, partition_by:list, path:str, target_table:str):
        """
        Prepares the SQL "create" statement.
        Parameters:
        - create_mode: replace | if_not_exists | default
        - with_data: True | False
        - partition_by: List of columns or None
        - path: S3 path
        - target_table: Table to create in format <catalog>.<database>.<table>
        """
        
        self.debug_print(f"def PREPARE_CREATE_STATEMENT >> parameters >> create_mode={create_mode}; with_data={with_data}; partition_by={partition_by}; path={path}; target_table={target_table}")
        
        create_modes = {"replace": "create or replace table", "if_not_exists": "create table if not exists", "default": "create table"}
        partition_data = f"partitioned by ({','.join(self.to_list(partition_by))})" if bool(partition_by) else ""
        filter_data = "" if with_data else "limit 0"
        
        self.debug_print(f"def PREPARE_CREATE_STATEMENT >> create_modes = {create_modes}")
        self.debug_print(f"def PREPARE_CREATE_STATEMENT >> partition_data = {partition_data}")
        self.debug_print(f"def PREPARE_CREATE_STATEMENT >> filter_data = {filter_data}")
        
        return f"{create_modes[create_mode]} {target_table} {partition_data} location '{path}' as select * from {self.__temp_view} {filter_data}"

    def __prepare_delete_statement(self, delete_keys:list, target_table:str):
        """
        Prepares the SQL "delete" statement
        Parameters:
        - delete_keys: Keys to connect source and target tables
        - target_table: Table to delete in format <catalog>.<database>.<table>
        """
        
        self.debug_print(f"def PREPARE_DELETE_STATEMENT >> parameters >> delete_keys={delete_keys}; target_table={target_table}")
        
        on_clause = self.__AND__.join([f"source.{c} = target.{c}" for c in self.to_list(delete_keys)])
        
        self.debug_print(f"def PREPARE_DELETE_STATEMENT >> on_clause = {on_clause}")
        
        return f"delete from {target_table} as target where exists (select 1 from {self.__temp_view} as source where {on_clause})"
    
    def __prepare_insert_statement(self, insert_mode:str, partition_by:list, target_table:str):
        """
        Prepares the SQL "insert" statement.
        Parameters:
        - insert_mode: into | overwrite
        - partition_by: List of columns or None
        - target_table: Table to insert in format <catalog>.<database>.<table>
        """
        
        self.debug_print(f"def PREPARE_INSERT_STATEMENT >> parameters >> insert_mode={insert_mode}; partition_by={partition_by}; target_table={target_table}")
        
        partition_data = f"partition ({','.join(self.to_list(partition_by))})" if bool(partition_by) else ""
        
        self.debug_print(f"def PREPARE_INSERT_STATEMENT >> partition_data = {partition_data}")
        
        return f"insert {insert_mode} {target_table} {partition_data} select * from {self.__temp_view}"
    
    def __prepare_merge_statement(self, merge_keys:list, merge_filter:list, target_table:str):
        """
        Prepares the SQL "merge" statement
        Parameters:
        - merge_keys: Keys to connect source and target tables
        - merge_filter: Filter to reduce the search space for matches
        - target_table: Table to merge in format <catalog>.<database>.<table>
        """
        
        self.debug_print(f"def PREPARE_MERGE_STATEMENT >> parameters >> merge_keys={merge_keys}; target_table={target_table}")
        
        on_clause = self.__AND__.join([f"source.{c} = target.{c}" for c in self.to_list(merge_keys)] + self.to_list(merge_filter))
        
        self.debug_print(f"def PREPARE_MERGE_STATEMENT >> on_clause = {on_clause}")
        
        return f"merge into {target_table} as target using {self.__temp_view} as source on {on_clause} when matched then update set * when not matched then insert *"
    
    def __write_delta_column_comment(self, df_cols:list, print_level:int) -> None:
        source_table = self.__read_options["name"] if self.__read_options.get("name") else self.remove_last_slash(self.__read_options["path"]).split("/")[-1]
        source_cols = {c: f"Origem: {source_table}.{c}" for c in self.__dataframe_columns}
        generated_cols = {c: c for c in set(df_cols) - set(source_cols.keys())}
        renames = {new: f"Origem: {source_table}.{old}" for old,new in self.__get_all_values_by_core_key(self.parameters, "rename", {}).items()}
        comments = self.__get_all_values_by_core_key(self.parameters, "comments", {})
        current_comments = {row.col_name:row.comment for row in spark.sql(f"describe {self.__write_options['name']}").collect()}

        if comments != False:
            # merge dicts
            all_comments = source_cols | generated_cols | renames | comments
            valid_comments = {k:v for k,v in all_comments.items() if k in df_cols}
            new_comments = {k:v for k,v in valid_comments.items() if v != current_comments.get(k)}

            for column_name, comment in new_comments.items():
                self.pprint(f"Updating comment on column {column_name}", lvl=print_level)
                self.__execute_sql(f"alter table {self.__write_options['name']} alter column `{column_name}` comment '{comment}'")
                self.pprint("Column comment updated", lvl=print_level+1, dots=1)

    def __write_delta_optimize_target_table(self, print_level:int) -> None:
        if self.__fl_optimize_target_table:
            self.pprint("Optimizing target table", lvl=print_level)
            optimize_where = f"where {' and '.join(self.to_list(self.__write_options.get('optimize_where',[])))}" if self.__write_options.get("optimize_where") else ""
            optimize_zorder = f"zorder by ({','.join(self.to_list(self.__write_options.get('optimize_zorder',[])))})" if self.__write_options.get("optimize_zorder") else ""
            self.__execute_sql(f"optimize {self.__write_options['name']} {optimize_where} {optimize_zorder}")
            self.pprint(f"Table {self.__write_options['name']} successfully optimized", lvl=print_level+1, dots=1)

    def __write_delta_process_target_table(self, print_level:int) -> None:
        write_mode_options = self.__get_delta_write_mode_options(self.__write_options["mode"])
        
        # Create
        self.pprint("Creating delta table", lvl=print_level)
        query_create = self.__prepare_create_statement(
            create_mode=write_mode_options["create_mode"],
            with_data=write_mode_options["with_data"],
            partition_by=self.__write_options.get("partitionBy",None),
            path=self.__write_options["path"],
            target_table=self.__write_options["name"]
        )
        self.__execute_sql(query_create, True, print_level+1)

        if write_mode_options["with_data"] is False:
            # Delete
            if write_mode_options.get("delete"):
                self.pprint("Deleting data from delta table", lvl=print_level)
                query_delete = self.__prepare_delete_statement(
                    delete_keys=self.__write_options["delete_keys"],
                    target_table=self.__write_options["name"]
                )
                self.__execute_sql(query_delete, True, print_level+1)

            # Merge
            if write_mode_options.get("merge"):
                self.pprint("Updating/inserting data into delta table", lvl=print_level)
                query_merge = self.__prepare_merge_statement(
                    merge_keys=self.__write_options["merge_keys"],
                    merge_filter=self.__write_options.get("merge_filter",[]),
                    target_table=self.__write_options["name"])
                self.__execute_sql(query_merge, True, print_level+1)

            # Insert
            if write_mode_options.get("insert_mode"):
                self.pprint("Inserting data into delta table", lvl=print_level)
                query_insert = self.__prepare_insert_statement(
                    insert_mode=write_mode_options["insert_mode"],
                    partition_by=self.__write_options.get("partitionBy",None),
                    target_table=self.__write_options["name"]
                )
                self.__execute_sql(query_insert, True, print_level+1)

    def __write_delta_set_grants(self, print_level:int) -> None:
        if "grants" in [self.get_split_part(k) for k in self.parameters.keys()]:
            catalog_name = self.__write_options["name"].split(".")[0]
            database_name = self.__write_options["name"].split(".")[1]
            args = self.parameters[self.get_split_part("grants")]
            for principal, privileges in args.items():
                try:
                    self.pprint(f"Granting {privileges} to {principal}", lvl=print_level)
                    self.__execute_sql(f"grant usage on catalog {catalog_name} to `{principal}`")
                    self.__execute_sql(f"grant usage on database {catalog_name}.{database_name} to `{principal}`")
                    self.__execute_sql(f"grant {privileges} on table {self.__write_options['name']} to `{principal}`")
                    self.pprint("Permission(s) granted", lvl=print_level+1, dots=1)
                except Exception as e:
                    self.pprint(f"Grant failed: {str(e)}", dots=0, lvl=print_level+1)
                    self.pprint("Skipping", lvl=print_level+1)

    def __write_delta_set_owner(self, print_level:int) -> None:
        current_owner = self.__execute_sql(f"DESCRIBE EXTENDED {self.__write_options['name']}", return_result=True).filter("col_name = 'Owner'").select("data_type").collect()[0][0]
        new_owner = self.__write_options.get('owner', 'zzdata@arezzo.com.br')
        if current_owner != new_owner:
            try:
                self.pprint(f"Changing owner to {new_owner}", lvl=print_level)
                self.__execute_sql(f"alter table {self.__write_options['name']} owner to `{new_owner}`")
                self.pprint("Owner updated", lvl=print_level+1, dots=1)
            except Exception as e:
                self.pprint(f"Set owner failed: {str(e)}", dots=0, lvl=print_level+1)
                self.pprint("Skipping", lvl=print_level+1)
    
    def __write_delta_table_comment(self, print_level:int) -> None:
        if self.__write_options.get("comment"):
            self.pprint("Updating table comment", lvl=print_level)
            table_comment = f"comment on table {self.__write_options['name']} is '{self.__write_options['comment']}'"
        else:
            self.pprint("Updating table comment with lineage information", lvl=print_level)
            source_table = self.__read_options["name"] if self.__read_options.get("name") else self.remove_last_slash(self.__read_options["path"]).split("/")[-1]
            table_comment = f"comment on table {self.__write_options['name']} is 'Origem: {source_table}'"
        
        self.__execute_sql(table_comment)
        self.pprint("Table comment updated", lvl=print_level+1, dots=1)

    def __write_delta_vacuum_target_table(self, print_level:int) -> None:
        if self.__fl_vacuum_target_table:
            self.pprint("Executing vacuum in target table to remove unused files", lvl=print_level)
            self.__execute_sql(f"vacuum {self.__write_options['name']}")
            self.pprint(f"Vacuum {self.__write_options['name']} successfully executed", lvl=print_level+1, dots=1)

    def __write_delta(self, df:DataFrame, print_level:int) -> None:
        self.pprint("Cleaning delta lake cache", lvl=print_level)
        try:
            self.__execute_sql("clear cache")
        except:
            self.pprint("Error cleaning cache. Skipping", lvl=print_level+1)
        
        self.pprint("Creating temp view", lvl=print_level)
        df.createOrReplaceTempView(self.__temp_view)
        self.pprint(f"Temp view created: {self.__temp_view}", lvl=print_level+1, dots=0)
        
        self.pprint(f"Setting 'partitionOverwriteMode' config to '{self.__write_options.get('partitionOverwriteMode', 'static')}'", lvl=print_level)
        spark.conf.set("spark.sql.sources.partitionOverwriteMode", self.__write_options.get('partitionOverwriteMode', 'static'))
        
        spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")
        
        self.__write_delta_process_target_table(print_level)
        self.pprint("Data saved with success", lvl=print_level+1, dots=1)
        
        self.__write_delta_table_comment(print_level)
        self.__write_delta_column_comment(df.columns, print_level)
        self.__write_delta_set_owner(print_level)
        self.__write_delta_set_grants(print_level)
        self.__write_delta_optimize_target_table(print_level)
        self.__write_delta_vacuum_target_table(print_level)

    def __write_data(self, df, print_level=0) -> DataFrame:
        self.debug_print(f"def WRITE_DATA >> write_options = {self.__write_options}")

        # Don't create "_commited", "_success" and "_started" files
        try:
            spark.conf.set("mapreduce.fileoutputcommitter.marksuccessfuljobs", "false")
            spark.conf.set("spark.sql.sources.commitProtocolClass", "org.apache.spark.sql.execution.datasources.SQLHadoopMapReduceCommitProtocol")
        except:
            self.pprint("Error setting spark configs. Skipping", lvl=print_level+1)
        
        if self.__write_options["format"] == "delta":
            self.pprint("Saving data in delta format", lvl=print_level)
            self.__write_delta(df, print_level+1)
            
        else: # other formats (csv, json, parquet, etc.)
            self.pprint("Saving successful data", lvl=print_level)
            df.write.save(**self.__write_options)
            self.pprint("Data saved with success", lvl=print_level+1, dots=1)
        
        return df

    # ^^^^^ WRITE DATA ^^^^^

    # vvvvv AFTER WRITING vvvvv

    def __delete_processed_files(self, print_level=0) -> None:
        if self.__fl_delete_processed_files:
            self.pprint("Deleting processed files", lvl=print_level)
            
            for source_file in self.ls(self.__read_options["path"], recursive=True):
                self.debug_print(f"source_file = {source_file}")
                dbutils.fs.rm(source_file)
            
            self.pprint("Files deleted", lvl=print_level+1, dots=1)

    def __rename_target_file(self, print_level=0) -> None:
        if self.__fl_rename_target_file:
            self.pprint("Renaming target file", lvl=print_level)
            
            target_path = self.ls(self.__write_options["path"], file_filter=self.__write_options["format"], recursive=False)[0]
            old_name = target_path.split("/")[-1]
            
            tz = self.__fl_rename_target_file.get("timezone")
            new_name = self.__fl_rename_target_file["target_name"]
            if self.__fl_rename_target_file.get("format_values"):
                new_name = new_name.format(**{k: self.now(fmt=v, timezone=tz) for k,v in self.__fl_rename_target_file["format_values"].items()})
            new_path = target_path.replace(old_name, '') + new_name
            
            self.debug_print(f"target_path = {target_path}")
            self.debug_print(f"old_name = {old_name}")
            self.debug_print(f"new_name = {new_name}")
            self.debug_print(f"new_path = {new_path}")
            
            rename_result = self.rename_file(target_path, new_path)
            self.pprint(f"Rename result: {rename_result}", lvl=print_level+1, dots=0)

    # ^^^^^ AFTER WRITING ^^^^^
