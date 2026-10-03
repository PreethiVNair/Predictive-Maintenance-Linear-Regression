import pandas as pd

from data_service.database_manager import Database


# Read the original training dataset
training_df = pd.read_csv("data/RMBR4-2_export_test.csv")

# Keep only the columns required for this project
training_df = training_df[
    [
        "Time",
        "Axis #1",
        "Axis #2",
        "Axis #3",
        "Axis #4",
        "Axis #5",
        "Axis #6",
        "Axis #7",
        "Axis #8"
    ]
].copy()

# Rename columns to database-friendly names
training_df.columns = [
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

# Convert time to datetime
training_df["time"] = pd.to_datetime(
    training_df["time"],
    errors="coerce",
    utc=True
)

# Convert axis values to numbers
axis_columns = [
    "axis_1", "axis_2", "axis_3", "axis_4",
    "axis_5", "axis_6", "axis_7", "axis_8"
]

for axis in axis_columns:
    training_df[axis] = pd.to_numeric(
        training_df[axis],
        errors="coerce"
    )

# Remove rows containing missing required values
training_df = training_df.dropna(
    subset=["time"] + axis_columns
)

print("Training records ready:", len(training_df))

# Store the training data in Neon
db = Database()

db.create_training_table()
if db.training_data_exists():
    print("Training data already exists. No new data was inserted.")
else:
    db.insert_training_data(training_df)
    print("Training data stored successfully.")

db.close()

