import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

# ─── Load environment variables ───────────────────────────────────────
load_dotenv()

# ─── STEP 1: Load raw data ────────────────────────────────────────────
data = pd.read_csv("Airbnb_Open_Data.csv")
print("Raw data shape:", data.shape)

# ─── STEP 2: Select columns to keep ──────────────────────────────────
columns_to_keep = [
    'NAME', 'host id', 'host_identity_verified', 'host name',
    'neighbourhood group', 'neighbourhood', 'lat', 'long', 'country',
    'country code', 'instant_bookable', 'cancellation_policy', 'room type',
    'Construction year', 'price', 'service fee', 'minimum nights',
    'number of reviews', 'last review'
]
data = data[columns_to_keep]
print("After column selection:", data.shape)

# ─── STEP 3: Drop irrelevant columns ─────────────────────────────────
columns_to_drop = [
    'reviews per month', 'review rate number',
    'calculated host listings count', 'availability 365',
    'house_rules', 'id', 'license'
]
# Only drop columns that exist (avoids errors on different dataset versions)
columns_to_drop = [c for c in columns_to_drop if c in data.columns]
data.drop(columns=columns_to_drop, inplace=True)

# ─── STEP 4: Rename columns to uppercase ─────────────────────────────
data.columns = [col.upper() for col in data.columns]

# ─── STEP 5: Remove duplicate rows ───────────────────────────────────
print("Duplicates found:", data.duplicated().sum())
data.drop_duplicates(inplace=True)
print("After removing duplicates:", data.shape)

# ─── STEP 6: Handle missing values ───────────────────────────────────
# Drop 'last review' - too many nulls
data.drop(columns=["LAST REVIEW"], inplace=True)

# Drop all remaining rows with any null
print("Null counts before dropna:\n", data.isna().sum())
data.dropna(inplace=True)
print("After dropna:", data.shape)

# ─── STEP 7: Standardise host_identity_verified ──────────────────────
data["HOST_IDENTITY_VERIFIED"] = data["HOST_IDENTITY_VERIFIED"].str.upper()

# ─── STEP 8: Convert instant_bookable to 0/1 ─────────────────────────
data["INSTANT_BOOKABLE"] = data["INSTANT_BOOKABLE"].apply(lambda x: 1 if x == True else 0)

# ─── STEP 9: Clean price column ──────────────────────────────────────
data["PRICE"] = data["PRICE"].str.replace(",", "", regex=False)
data["PRICE"] = data["PRICE"].str.replace("$", "", regex=False)
data["PRICE"] = data["PRICE"].str.replace(" ", "", regex=False)
data["PRICE"] = data["PRICE"].astype(float)  # Convert to numeric

# ─── STEP 10: Reset index ─────────────────────────────────────────────
data.reset_index(drop=True, inplace=True)
print("Final cleaned data shape:", data.shape)

# ─── STEP 11: Export to CSV ───────────────────────────────────────────
data.to_csv("cleaned_airbnb_data.csv", index=False)
print("Exported to cleaned_airbnb_data.csv")

# ─── STEP 12: Export to Excel ────────────────────────────────────────
data.to_excel("excel_cleaned_airbnb_data.xlsx", index=False)
print("Exported to excel_cleaned_airbnb_data.xlsx")

# ─── STEP 13: Export to MySQL ────────────────────────────────────────
username      = os.getenv("DB_USERNAME")
password      = quote_plus(os.getenv("DB_PASSWORD"))
host          = os.getenv("DB_HOST")
port          = os.getenv("DB_PORT")
database_name = os.getenv("DB_NAME")

engine = create_engine(
    f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database_name}"
)

data.to_sql(
    name="cleaned_airbnb_data",
    con=engine,
    if_exists="replace",
    index=False
)
print("Exported to MySQL successfully!")
