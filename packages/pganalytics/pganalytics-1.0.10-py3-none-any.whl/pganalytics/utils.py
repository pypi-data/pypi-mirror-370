import pandas as pd
import decimal
import datetime
import yaml
from google.cloud import bigquery
from google.api_core.exceptions import Conflict
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans, DBSCAN

import os
from prefect import get_run_logger
from prefect_email import EmailServerCredentials, email_send_message


import psycopg2
from psycopg2 import sql
import pandas as pd
from sqlalchemy import create_engine

SLACK_CHANNEL_EMAIL = 'analytics-notificatio-aaaaolpxr7yqmeuhgcddksk6yu@platform.org.slack.com'

#POSTGRES CREDENTIALS
DB_HOST = "192.168.40.213"
DB_NAME = "datascience_prod"
DB_USER = "datascience_app"
DB_PASS = "2fH7c34E9!2eL"
DB_PORT = "5432"


class BigQueryUtils:
    """
    A utility class for performing operations on Google BigQuery. It provides methods
    for fetching data, inserting data, and managing tables within BigQuery.

    Attributes:
        client (google.cloud.bigquery.Client): A client for BigQuery operations.
    """
    SERVICE_ACCOUNT_PATH = "/home/pronetgaming/Documents/bq_key.json"

    def __init__(self, service_account_path=SERVICE_ACCOUNT_PATH):
        """
        Initializes the BigQuery client using a service account JSON key file.

        Args:
            service_account_path (str): The file path to the JSON key for Google Cloud service account.
        """
        self.client = bigquery.Client.from_service_account_json(service_account_path)

    def fetch_data(self, query):
        """
        Executes a SQL query on BigQuery and returns the result as a Pandas DataFrame.

        Args:
            query (str): The SQL query to execute.

        Returns:
            pandas.DataFrame: A DataFrame containing the query results.
        """
        query_job = self.client.query(query)
        df = query_job.to_dataframe()
        return df

    def insert_data(self, table_id, df):
        """
        Inserts data from a Pandas DataFrame into a specified BigQuery table.

        Args:
            table_id (str): The BigQuery table ID where data will be inserted.
            df (pandas.DataFrame): The DataFrame containing data to insert.

        Prints:
            Confirmation message or error details if insertion fails.
        """
        rows_to_insert = df.to_dict('records')
        errors = self.client.insert_rows_json(table_id, rows_to_insert)

        if errors:
            print("Errors occurred: {}".format(errors))
        else:
            print("Rows inserted successfully.")

    def create_and_insert_data(self, table_id, dataframe):
        """
        Creates a BigQuery table with the schema derived from a Pandas DataFrame and
        inserts the DataFrame data into the table.

        Args:
            table_id (str): The ID of the table to be created and populated.
            dataframe (pandas.DataFrame): DataFrame whose data and schema will be used for table creation and data insertion.

        Prints:
            Messages indicating table creation status and successful data insertion.
        """

        def preprocess_dataframe(df):
            """
            Preprocess the DataFrame by converting columns that can be interpreted as dates
            into the datetime format understood by pandas.

            Args:
                df (pd.DataFrame): The input DataFrame.

            Returns:
                pd.DataFrame: The DataFrame with date-like columns converted to datetime64.
            """
            for column in df.columns:
                try:
                    df[column] = pd.to_datetime(df[column], format='%Y-%m-%d')
                except (ValueError, TypeError):
                    pass
            return df

        dataframe = preprocess_dataframe(df=dataframe)

        def pandas_dtype_to_bq_dtype(series, dtype):
            """
            Converts a Pandas dtype to a BigQuery field type.

            Args:
                series (pandas.Series): The data series from the DataFrame.
                dtype (pandas.dtype): The dtype of the series.

            Returns:
                str: The corresponding BigQuery data type.
            """
            if pd.api.types.is_integer_dtype(dtype):
                return 'INTEGER'
            elif pd.api.types.is_float_dtype(dtype):
                return 'FLOAT'
            elif pd.api.types.is_bool_dtype(dtype):
                return 'BOOLEAN'
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                return 'TIMESTAMP'
            elif pd.api.types.is_object_dtype(dtype):
                non_null_values = series.dropna()
                if not non_null_values.empty:
                    first_value = non_null_values.iloc[0]
                    if isinstance(first_value, datetime.datetime):
                        return 'STR'
                    elif isinstance(first_value, datetime.date):
                        return 'DATE'
                    elif isinstance(first_value, decimal.Decimal):
                        return 'NUMERIC'
                    elif isinstance(first_value, str):
                        return 'STRING'
                return 'STRING'
            else:
                return 'STRING'

        fields = [
            bigquery.SchemaField(name=column_name, field_type=pandas_dtype_to_bq_dtype(dataframe[column_name], dtype), mode='NULLABLE')
            for column_name, dtype in dataframe.dtypes.items()
        ]
        table_schema = fields

        table = bigquery.Table(table_id, schema=table_schema)
        try:
            table = self.client.create_table(table)
            print("Created table {}".format(table_id))
        except Conflict:
            print("Table {} already exists.".format(table_id))

        self.client.insert_rows_from_dataframe(table, dataframe)
        print("Rows inserted successfully.")


    def truncate_and_insert_data(self, table_id, dataframe):
        """
        Truncates the specified BigQuery table and inserts new data from the provided DataFrame.

        Args:
            table_id (str): The BigQuery table ID to truncate and insert data into.
            dataframe (pandas.DataFrame): The DataFrame containing the new data to insert.

        Prints:
            Confirmation message of successfully truncating and inserting new data.
        """
        # Configure the load job with a WRITE_TRUNCATE disposition
        job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)
        # Perform the load operation
        load_job = self.client.load_table_from_dataframe(dataframe, table_id, job_config=job_config)
        load_job.result()  # Wait for the job to complete
        print(f"Table {table_id} has been truncated and new data inserted successfully.")

    def delete_data(self, query):
        """
        Deletes data from a BigQuery table based on the specified SQL query.

        Args:
            query (str): The SQL query to execute for deleting data.

        Prints:
            Confirmation message upon successful data deletion.
        """
        query_job = self.client.query(query)
        query_job.result()  # Wait for the job to complete
        print("Data deleted successfully.")

    def delete_table(self, table_id):
        """
        Deletes the specified BigQuery table.

        Args:
            table_id (str): The BigQuery table ID to delete.

        Prints:
            Confirmation message indicating successful table deletion or an error if deletion fails.
        """
        try:
            self.client.delete_table(table_id)
            print(f"Table {table_id} deleted successfully.")
        except Exception as e:
            print(f"Error deleting table {table_id}: {e}")

class PredictionModels:
    """
    A class for managing and using machine learning models, specifically Random Forest
    and XGBoost regressors, for training and predictions.

    Attributes:
        rf_regressor (RandomForestRegressor): Instance of a RandomForestRegressor.
        xgb_regressor (XGBRegressor): Instance of a XGBRegressor.
    """
    
    def train_random_forest(self, X_train, y_train):
        """
        Trains the RandomForestRegressor with provided training data.

        Args:
            X_train (array-like): Features for training the model.
            y_train (array-like): Target values for training the model.
        """
        self.rf_regressor = RandomForestRegressor()
        self.rf_regressor.fit(X_train, y_train)
        print("Random Forest training complete.")

        return self.rf_regressor

    def train_xgboost(self, X_train, y_train):
        """
        Trains the XGBRegressor with provided training data.

        Args:
            X_train (array-like): Features for training the model.
            y_train (array-like): Target values for training the model.
        """
        self.xgb_regressor = XGBRegressor()
        self.xgb_regressor.fit(X_train, y_train)
        print("XGBoost training complete.")

        return self.xgb_regressor

    def predict_random_forest(self, X_test):
        """
        Makes predictions using the trained RandomForestRegressor model.

        Args:
            X_test (array-like): Features for which predictions are to be made.

        Returns:
            array-like: Predicted values.
        """
        return self.rf_regressor.predict(X_test)

    def predict_xgboost(self, X_test):
        """
        Makes predictions using the trained XGBRegressor model.

        Args:
            X_test (array-like): Features for which predictions are to be made.

        Returns:
            array-like: Predicted values.
        """
        return self.xgb_regressor.predict(X_test)

class ClassificationModels:
    """
    A utility class for creating and training various classification models
    using popular algorithms from scikit-learn.

    Methods:
        logistic_regression: Trains a Logistic Regression model.
        decision_tree: Trains a Decision Tree model.
        random_forest: Trains a Random Forest model.
        svm: Trains a Support Vector Machine model.
        knn: Trains a k-Nearest Neighbors model.
    """

    def logistic_regression(self, X, y):
        """
        Trains a Logistic Regression model.

        Args:
            X (pd.DataFrame or np.ndarray): The features for training.
            y (pd.Series or np.ndarray): The target variable for training.

        Returns:
            LogisticRegression: The trained Logistic Regression model.
        """
        model = LogisticRegression()
        model.fit(X, y)
        return model

    def decision_tree(self, X, y):
        """
        Trains a Decision Tree Classifier.

        Args:
            X (pd.DataFrame or np.ndarray): The features for training.
            y (pd.Series or np.ndarray): The target variable for training.

        Returns:
            DecisionTreeClassifier: The trained Decision Tree Classifier.
        """
        model = DecisionTreeClassifier(random_state=42)
        model.fit(X, y)
        return model

    def random_forest(self, X, y):
        """
        Trains a Random Forest Classifier.

        Args:
            X (pd.DataFrame or np.ndarray): The features for training.
            y (pd.Series or np.ndarray): The target variable for training.

        Returns:
            RandomForestClassifier: The trained Random Forest Classifier.
        """
        model = RandomForestClassifier(random_state=42)
        model.fit(X, y)
        return model

    def svm(self, X, y):
        """
        Trains a Support Vector Machine (SVM) Classifier.

        Args:
            X (pd.DataFrame or np.ndarray): The features for training.
            y (pd.Series or np.ndarray): The target variable for training.

        Returns:
            SVC: The trained Support Vector Machine Classifier.
        """
        model = SVC()
        model.fit(X, y)
        return model

    def knn(self, X, y, n_neighbors=5):
        """
        Trains a k-Nearest Neighbors (kNN) Classifier.

        Args:
            X (pd.DataFrame or np.ndarray): The features for training.
            y (pd.Series or np.ndarray): The target variable for training.
            n_neighbors (int): Number of neighbors to use.

        Returns:
            KNeighborsClassifier: The trained k-Nearest Neighbors Classifier.
        """
        model = KNeighborsClassifier(n_neighbors=n_neighbors)
        model.fit(X, y)
        return model
    
class ClusteringModels:
    """
    A utility class for creating and training popular clustering models:
    K-Means and DBSCAN from scikit-learn.

    Methods:
        k_means: Trains a K-Means clustering model.
        dbscan: Trains a DBSCAN clustering model.
    """

    def k_means(self, X, n_clusters=3):
        """
        Trains a K-Means clustering model.

        Args:
            X (pd.DataFrame or np.ndarray): The features for clustering.
            n_clusters (int): The number of clusters to form.

        Returns:
            KMeans: The trained K-Means model.
        """
        model = KMeans(n_clusters=n_clusters, random_state=42)
        model.fit(X)
        return model

    def dbscan(self, X, eps=0.5, min_samples=5):
        """
        Trains a DBSCAN clustering model.

        Args:
            X (pd.DataFrame or np.ndarray): The features for clustering.
            eps (float): The maximum distance between two samples for one to be considered as in the neighborhood of the other.
            min_samples (int): The number of samples in a neighborhood for a point to be considered a core point.

        Returns:
            DBSCAN: The trained DBSCAN model.
        """
        model = DBSCAN(eps=eps, min_samples=min_samples)
        model.fit(X)
        return model
       
class Misc:
    """
    A miscellaneous utility class for handling file operations, such as reading SQL files
    and loading configuration from YAML files.
    """

    def read_sql_file(self, file_path: str):
        """
        Reads the contents of a SQL file and returns it as a string.

        Args:
            file_path (str): The path to the SQL file.

        Returns:
            str: The contents of the SQL file.
        """
        with open(file_path, 'r') as file:
            return file.read()
    
    def load_config(self, file_path: str):
        """
        Loads configuration settings from a YAML file.

        Args:
            file_path (str): The path to the YAML configuration file.

        Returns:
            dict: The configuration data loaded from the file.
        """
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
        return config


class PrefectHelpers:

    async def send_email_prefect(
        self,
        recipients: list,
        subject: str,
        body: str,
        attachment_path: str = None
    ):
        print("Starting task: send_email_prefect")

        try:
            credentials = await EmailServerCredentials.load("pronet-smtp-server")
        except Exception as e:
            print(f"Failed to load credentials block 'pronet-smtp-server': {e}")
            return

        attachments = [attachment_path] if attachment_path and os.path.exists(attachment_path) else []

        await email_send_message(
            email_server_credentials=credentials,
            subject=subject,
            msg=body,
            email_to=recipients,
            attachments=attachments
        )
        print("Report email sent successfully!")

    async def send_failure_email(self, flow_name: str, error_message: str):
        print("Starting task: send_failure_email")

        try:
            credentials = await EmailServerCredentials.load("pronet-smtp-server")
        except Exception as e:
            print(f"Failed to load credentials block 'pronet-smtp-server': {e}")
            return

        subject = f"{flow_name} flow failed."
        msg = f"The flow failed with an error. Error: {error_message}"

        await email_send_message(
            email_server_credentials=credentials,
            subject=subject,
            msg=msg,
            email_to=[SLACK_CHANNEL_EMAIL]
        )
        print("Failure email sent successfully!")


class PostgresUtils:
    """
    A utility class for interacting with a PostgreSQL database. This class
    provides methods for querying, inserting, and managing data using a
    standard `psycopg2` and `sqlalchemy` connection.
    """

    def __init__(self):
        """
        Initializes the PostgresUtils instance. The connection is managed
        on a per-method basis to ensure it is closed properly.
        """
        self.connection_params = {
            "host": DB_HOST,
            "database": DB_NAME,
            "user": DB_USER,
            "password": DB_PASS,
            "port": DB_PORT
        }
        
        self.sqlalchemy_engine = create_engine(
            f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

    def fetch_data(self, query: str) -> pd.DataFrame:
        """
        Executes a SQL query and returns the result as a Pandas DataFrame.

        Args:
            query (str): The SQL query to execute.

        Returns:
            pandas.DataFrame: The query results.
        """
        with psycopg2.connect(**self.connection_params) as conn:
            return pd.read_sql(query, conn)

    def execute_query(self, query: str):
        """
        Executes a SQL command that doesn't return data (e.g., INSERT, UPDATE, DELETE).

        Args:
            query (str): The SQL command to execute.
        """
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                conn.commit()
        print("Query executed successfully.")

    def insert_dataframe(self, table: str, dataframe: pd.DataFrame, schema: str = None, if_exists: str = "append"):
        """
        Inserts a Pandas DataFrame into a PostgreSQL table using a SQLAlchemy engine.

        Args:
            table (str): Name of the target table.
            dataframe (pd.DataFrame): The DataFrame to be inserted.
            schema (str): The target schema (optional).
            if_exists (str): What to do if the table exists: 'fail', 'replace', or 'append'. Defaults to 'append'.
        """
        dataframe.to_sql(table, self.sqlalchemy_engine, schema=schema, if_exists=if_exists, index=False)
        full_table_name = f"{schema}.{table}" if schema else table
        print(f"Data inserted into {full_table_name} successfully.")

    def truncate_table(self, table: str, schema: str = None):
        """
        Truncates a table in PostgreSQL.

        Args:
            table (str): Table name.
            schema (str): Schema name (optional).
        """
        full_table_name = f"{schema}.{table}" if schema else table
        query = sql.SQL("TRUNCATE TABLE {}").format(sql.Identifier(full_table_name))
        self.execute_query(query.as_string(self.connection_params))
        print(f"Table {full_table_name} truncated successfully.")

    def delete_from_table(self, table: str, condition: str = "1=1", schema: str = None):
        """
        Deletes data from a table with the specified condition.

        Args:
            table (str): Table name.
            condition (str): WHERE condition for deletion.
            schema (str): Schema name (optional).
        """
        full_table_name = f"{schema}.{table}" if schema else table
        query = sql.SQL("DELETE FROM {} WHERE {}").format(sql.Identifier(full_table_name), sql.SQL(condition))
        self.execute_query(query.as_string(self.connection_params))
        print(f"Data deleted from {full_table_name} where {condition}.")
