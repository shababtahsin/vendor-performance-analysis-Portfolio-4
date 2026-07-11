# Vendor Performance Analysis

A data analytics project analyzing vendor and product performance for a retail inventory business, covering the full pipeline from raw data ingestion through exploratory data analysis to an interactive Power BI dashboard.

---

## Project Overview

This project answers key business questions around vendor profitability, procurement efficiency, inventory management, and pricing strategy using a multi-table SQLite inventory database (~1.5 GB of raw data).

**Business Questions Answered:**
- Which vendors and brands are most profitable?
- Which vendors dominate total procurement, and is there over-dependence risk?
- Does bulk purchasing reduce unit costs, and what is the optimal order size?
- Which vendors have slow-moving inventory, and how much capital is locked in unsold stock?
- Is there a statistically significant difference in profit margins between top and low-performing vendors?
- Which brands have high margins but low sales and need promotional attention?

---

## Project Structure

```
vendor-performance-analysis/
│
├── data/                          # Raw CSV files (not included — ~1.5 GB)
├── logs/                          # Log files generated during ingestion & processing
│   ├── ingestion_db.log
│   └── get_vendor_summary.log
│
├── Untitled.ipynb                          # Step 1: Data Ingestion — loads CSVs into SQLite DB
├── Exploratory_data_analysis_SHABAB.ipynb  # Step 2: EDA & feature engineering
├── Vendor_Performance_Analysis_SHABAB.ipynb # Step 3: Analysis, visualizations & statistics
│
├── vendor_sales_summary.csv        # Final aggregated summary table (exported from DB)
├── vendor_performance.pbix         # Power BI dashboard
└── README.md
```

---

## Data Pipeline

### Step 1 — Data Ingestion (`Untitled.ipynb`)
- Reads all CSV files from the `/data` folder
- Loads each file into a SQLite database (`inventory.db`) using its filename as the table name
- Logs ingestion activity and time taken to `logs/ingestion_db.log`

**Source Tables in DB:**
| Table | Description |
|---|---|
| `purchases` | Actual purchase transactions — vendor, brand, quantity, dollars |
| `purchase_prices` | Product-level actual and purchase prices (unique per vendor + brand) |
| `vendor_invoice` | Aggregated PO-level data including freight costs |
| `sales` | Actual sales transactions — brand, quantity, revenue, excise tax |

---

### Step 2 — EDA & Feature Engineering (`Exploratory_data_analysis_SHABAB.ipynb`)
- Explored each raw table structure and relationships using a single vendor (VendorNumber 4466) as a test case
- Built a summary SQL query using 3 CTEs to join purchases, sales, and freight data into one flat table
- Performed data cleaning: type conversions, null fills, whitespace stripping
- Engineered 4 new business metrics:

| Metric | Formula |
|---|---|
| `GrossProfit` | TotalSalesDollars − TotalPurchaseDollars |
| `ProfitMargin` | (GrossProfit / TotalSalesDollars) × 100 |
| `StockTurnover` | TotalSalesQuantity / TotalPurchaseQuantity |
| `SalesToPurchaseRatio` | TotalSalesDollars / TotalPurchaseDollars |

- Saved the final table back to `inventory.db` as `vendor_sales_summary` and exported as `vendor_sales_summary.csv`

---

### Step 3 — Analysis & Visualizations (`Vendor_Performance_Analysis_SHABAB.ipynb`)
- Loaded the `vendor_sales_summary` table from SQLite
- Filtered out records with negative/zero profit and zero sales for analysis integrity
- Performed the following analyses:

**Distribution & Outlier Analysis**
- Histograms and boxplots for all numerical columns
- Identified premium-priced products, freight cost outliers, and zero-sales stock

**Correlation Analysis**
- Heatmap revealing strong purchase-to-sales quantity correlation (0.999)
- Weak correlation between purchase price and gross profit — price alone doesn't drive margin

**Top Vendors & Brands by Sales**
- Bar charts for top 10 vendors and top 10 brands by total sales dollars

**Vendor Procurement Concentration (Pareto Analysis)**
- Pareto chart showing top 10 vendors account for ~65.69% of total procurement
- Donut chart visualizing vendor concentration risk

**Bulk Purchasing Impact**
- Orders segmented into Small / Medium / Large by purchase quantity
- Large orders achieve ~72% lower unit cost vs Small orders ($10.78 vs ~$38)

**Slow-Moving Inventory**
- Identified vendors with StockTurnover < 1 (purchased more than sold)
- Calculated total capital locked in unsold inventory per vendor

**Brands Needing Promotional Attention**
- Scatter plot flagging brands in the bottom 15% of sales but top 15% of profit margin — candidates for pricing adjustments or marketing push

**Statistical Testing (T-Test)**
- Hypothesis test comparing profit margins of top-performing vs low-performing vendors
- Result: Statistically significant difference (p < 0.05) — low-performing vendors have higher margins (40–43%) vs top vendors (30–32%), suggesting premium pricing in niche segments

---

## Key Findings

1. **Top 10 vendors drive ~65.7% of procurement** — high dependency risk if any key vendor is disrupted
2. **Bulk purchasing reduces unit costs by ~72%** — large orders are significantly more cost-efficient
3. **Low-performing vendors have higher profit margins** (~41% vs ~31%) despite lower sales volume, suggesting untapped pricing or marketing opportunities
4. **Significant capital is locked in slow-moving stock** — vendors with turnover < 1 represent inventory inefficiency and holding cost risk
5. **Strong purchase-to-sales correlation (0.999)** confirms that inventory is generally well-matched to demand

---

## Dashboard

The `vendor_performance.pbix` Power BI file provides an interactive view of:
- Vendor sales and profitability
- Procurement concentration
- Inventory turnover
- Brand-level performance

> Open with Power BI Desktop.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.12 | Data processing and analysis |
| pandas | Data manipulation |
| SQLite + SQLAlchemy | Database storage and querying |
| matplotlib + seaborn | Visualizations |
| scipy.stats | Statistical testing (T-test, confidence intervals) |
| numpy | Numerical operations |
| Power BI | Interactive dashboarding |
| Jupyter Notebook | Development environment |

---

## Setup & Usage

> **Note:** The raw dataset (~1.5 GB of CSV files) is not included in this repository due to file size constraints.

To run this project locally with your own data:

1. Clone the repository
2. Place your raw CSV files in the `/data` folder
3. Create a `/logs` folder in the root directory
4. Install dependencies:
   ```bash
   pip install pandas sqlalchemy scipy matplotlib seaborn numpy jupyter
   ```
5. Run the notebooks in order:
   - `Untitled.ipynb` → ingests CSVs into `inventory.db`
   - `Exploratory_data_analysis_SHABAB.ipynb` → builds and cleans `vendor_sales_summary`
   - `Vendor_Performance_Analysis_SHABAB.ipynb` → analysis and visualizations
6. Open `vendor_performance.pbix` in Power BI Desktop for the dashboard

---

## Author

**Shabab Tahsin**  
Business Data Analyst | SQL · Python · Power BI · Excel
