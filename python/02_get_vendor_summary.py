# =============================================================================
# 02_get_vendor_summary.py
# Joins purchases, sales, and freight tables from the database into a single
# aggregated vendor_sales_summary table. Cleans data and engineers new metrics.
# =============================================================================

import sqlite3
import pandas as pd
import logging
import os

logging.basicConfig(
    filename="logs/get_vendor_summary.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)


def ingest_db(df, table_name, conn):
    """Ingest a dataframe into the database as a table."""
    df.to_sql(table_name, con=conn, if_exists='replace', index=False)


def create_vendor_summary(conn):
    """
    Joins purchases, purchase_prices, sales, and vendor_invoice tables
    into one flat vendor_sales_summary table.
    """
    query = """
        WITH FreightSummary AS (
            SELECT
                VendorNumber,
                SUM(Freight) AS FreightCost
            FROM vendor_invoice
            GROUP BY VendorNumber
        ),

        PurchaseSummary AS (
            SELECT
                p.VendorNumber,
                p.VendorName,
                p.Brand,
                p.Description,
                p.PurchasePrice,
                pp.Price AS ActualPrice,
                pp.Volume,
                SUM(p.Quantity) AS TotalPurchaseQuantity,
                SUM(p.Dollars)  AS TotalPurchaseDollars
            FROM purchases p
            JOIN purchase_prices pp
                ON p.Brand = pp.Brand
            WHERE p.PurchasePrice > 0
            GROUP BY p.VendorNumber, p.VendorName, p.Brand,
                     p.Description, p.PurchasePrice, pp.Price, pp.Volume
        ),

        SalesSummary AS (
            SELECT
                VendorNo,
                Brand,
                SUM(SalesQuantity) AS TotalSalesQuantity,
                SUM(SalesDollars)  AS TotalSalesDollars,
                SUM(SalesPrice)    AS TotalSalesPrice,
                SUM(ExciseTax)     AS TotalExciseTax
            FROM sales
            GROUP BY VendorNo, Brand
        )

        SELECT
            ps.VendorNumber,
            ps.VendorName,
            ps.Brand,
            ps.Description,
            ps.PurchasePrice,
            ps.ActualPrice,
            ps.Volume,
            ps.TotalPurchaseQuantity,
            ps.TotalPurchaseDollars,
            ss.TotalSalesQuantity,
            ss.TotalSalesDollars,
            ss.TotalSalesPrice,
            ss.TotalExciseTax,
            fs.FreightCost
        FROM PurchaseSummary ps
        LEFT JOIN SalesSummary ss
            ON ps.VendorNumber = ss.VendorNo
            AND ps.Brand = ss.Brand
        LEFT JOIN FreightSummary fs
            ON ps.VendorNumber = fs.VendorNumber
        ORDER BY ps.TotalPurchaseDollars DESC
    """
    vendor_sales_summary = pd.read_sql_query(query, conn)
    return vendor_sales_summary


def clean_data(df):
    """
    Cleans the vendor summary dataframe and engineers new business metrics:
      - GrossProfit, ProfitMargin, StockTurnover, SalesToPurchaseRatio
    """
    # Fix data types
    df['Volume'] = df['Volume'].astype('float')

    # Fill missing values
    df.fillna(0, inplace=True)

    # Strip whitespace from categorical columns
    df['VendorName'] = df['VendorName'].str.strip()
    df['Description'] = df['Description'].str.strip()

    # Engineer new metrics
    df['GrossProfit'] = df['TotalSalesDollars'] - df['TotalPurchaseDollars']
    df['ProfitMargin'] = (df['GrossProfit'] / df['TotalSalesDollars']) * 100
    df['StockTurnover'] = df['TotalSalesQuantity'] / df['TotalPurchaseQuantity']
    df['SalesToPurchaseRatio'] = df['TotalSalesDollars'] / df['TotalPurchaseDollars']

    return df


if __name__ == '__main__':
    os.makedirs('logs', exist_ok=True)

    conn = sqlite3.connect('inventory.db')

    print('Creating vendor summary table...')
    logging.info('Creating Vendor Summary Table.....')
    summary_df = create_vendor_summary(conn)
    logging.info(summary_df.head())

    print('Cleaning data and engineering metrics...')
    logging.info('Cleaning Data.....')
    clean_df = clean_data(summary_df)
    logging.info(clean_df.head())

    print('Saving to database...')
    logging.info('Ingesting data.....')
    ingest_db(clean_df, 'vendor_sales_summary', conn)

    print('Exporting to CSV...')
    clean_df.to_csv('vendor_sales_summary.csv', index=False)

    logging.info('Completed')
    print('Done. vendor_sales_summary saved to DB and exported as CSV.')

    conn.close()
