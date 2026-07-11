# =============================================================================
# 01_data_ingestion.py
# Loads all CSV files from the /data folder into a SQLite database.
# Each CSV becomes a table named after its filename.
# =============================================================================

import pandas as pd
import os
from sqlalchemy import create_engine
import logging
import time

logging.basicConfig(
    filename="logs/ingestion_db.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)

engine = create_engine('sqlite:///inventory.db')


def ingest_db(df, table_name, engine):
    """Ingest a dataframe into the database as a table."""
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)


def load_raw_data():
    """Load all CSVs from /data folder and ingest into the database."""
    start = time.time()

    for file in os.listdir('data'):
        if file.endswith('.csv'):
            df = pd.read_csv('data/' + file)
            logging.info(f'Ingesting {file} into db')
            ingest_db(df, file[:-4], engine)
            print(f'  ✓ Ingested: {file}')

    end = time.time()
    total_time = (end - start) / 60

    logging.info('--------------Ingestion Complete------------')
    logging.info(f'Total Time Taken: {total_time:.2f} minutes')
    print(f'\nIngestion complete. Time taken: {total_time:.2f} minutes')


if __name__ == '__main__':
    os.makedirs('logs', exist_ok=True)
    print('Starting data ingestion...')
    load_raw_data()
