import os
import pandas as pd
import psycopg
from dotenv import load_dotenv


class Database:

    def __init__(self):
        # Load values from the .env file
        load_dotenv()

        # Get the Neon database connection string
        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            raise ValueError("DATABASE_URL was not found in the .env file.")

        # Connect to Neon PostgreSQL
        self.connection = psycopg.connect(database_url)

        # Create a cursor for running SQL commands
        self.cursor = self.connection.cursor()

        print("Connected to Neon database.")
        
    def create_training_table(self):
        """Create the table used to store historical training data."""

        query = """
            CREATE TABLE IF NOT EXISTS training_data (
                id SERIAL PRIMARY KEY,
                time TIMESTAMPTZ NOT NULL,
                axis_1 DOUBLE PRECISION,
                axis_2 DOUBLE PRECISION,
                axis_3 DOUBLE PRECISION,
                axis_4 DOUBLE PRECISION,
                axis_5 DOUBLE PRECISION,
                axis_6 DOUBLE PRECISION,
                axis_7 DOUBLE PRECISION,
                axis_8 DOUBLE PRECISION
            );
        """

        self.cursor.execute(query)
        self.connection.commit()
        
        
    def insert_training_data(self, dataframe):
        """Insert training data into the PostgreSQL database."""

        query = """
            INSERT INTO training_data
            (time, axis_1, axis_2, axis_3, axis_4,
            axis_5, axis_6, axis_7, axis_8)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        records = list(
            dataframe[
                [
                    "time",
                    "axis_1",
                    "axis_2",
                    "axis_3",
                    "axis_4",
                    "axis_5",
                    "axis_6",
                    "axis_7",
                    "axis_8"
                ]
            ].itertuples(index=False, name=None)
        )

        self.cursor.executemany(query, records)
        self.connection.commit()
        
        
    def training_data_exists(self):
        """Check whether the training table already contains data."""

        self.cursor.execute("SELECT COUNT(*) FROM training_data;")
        count = self.cursor.fetchone()[0]

        return count > 0
    
    def fetch_training_data(self):
        """Retrieve the training data from PostgreSQL."""

        query = """
            SELECT
                time,
                axis_1,
                axis_2,
                axis_3,
                axis_4,
                axis_5,
                axis_6,
                axis_7,
                axis_8
            FROM training_data
            ORDER BY time;
        """

        self.cursor.execute(query)

        rows = self.cursor.fetchall()

        columns = [
            "time",
            "axis_1",
            "axis_2",
            "axis_3",
            "axis_4",
            "axis_5",
            "axis_6",
            "axis_7",
            "axis_8"
        ]

        return pd.DataFrame(rows, columns=columns)
    
    def create_stream_table(self):
        """Create the table used to store streaming sensor data."""
        query = """
            CREATE TABLE IF NOT EXISTS stream_data (
                id SERIAL PRIMARY KEY,
                time TIMESTAMPTZ NOT NULL,
                axis_1 DOUBLE PRECISION,
                axis_2 DOUBLE PRECISION,
                axis_3 DOUBLE PRECISION,
                axis_4 DOUBLE PRECISION,
                axis_5 DOUBLE PRECISION,
                axis_6 DOUBLE PRECISION,
                axis_7 DOUBLE PRECISION,
                axis_8 DOUBLE PRECISION
            );
        """
        self.cursor.execute(query)
        self.connection.commit()
        
        
    def insert_stream_reading(self, row):
        """Insert one sensor reading into the streaming table."""
        query = """
            INSERT INTO stream_data
            (time, axis_1, axis_2, axis_3, axis_4,
            axis_5, axis_6, axis_7, axis_8)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        values = (
            row["time"],
            row["axis_1"],
            row["axis_2"],
            row["axis_3"],
            row["axis_4"],
            row["axis_5"],
            row["axis_6"],
            row["axis_7"],
            row["axis_8"]
        )

        self.cursor.execute(query, values)
        self.connection.commit()
        
        
    def fetch_stream_data(self):
        """Retrieve streaming sensor data from PostgreSQL."""
        query = """
            SELECT
                time,
                axis_1,
                axis_2,
                axis_3,
                axis_4,
                axis_5,
                axis_6,
                axis_7,
                axis_8
            FROM stream_data
            ORDER BY time;
        """

        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        columns = [
            "time", "axis_1", "axis_2", "axis_3", "axis_4",
            "axis_5", "axis_6", "axis_7", "axis_8"
        ]

        return pd.DataFrame(rows, columns=columns)
    
    
    def clear_stream_data(self):
        """Remove previous synthetic streaming data."""
        self.cursor.execute("TRUNCATE TABLE stream_data RESTART IDENTITY;")
        self.connection.commit()
        
    def close(self):
        """Close the database cursor and connection."""
        self.cursor.close()
        self.connection.close()