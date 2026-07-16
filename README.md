# Vendor Performance Analysis

A full-pipeline data analytics project analyzing vendor and product performance across a retail inventory business — from raw data ingestion through SQL-based feature engineering to statistical testing and an interactive Power BI dashboard.

**Dataset:** ~1.5 GB across 4 source tables (119 vendors, $441M total sales, $307M total purchases)  
**Stack:** Python · SQLite · SQLAlchemy · pandas · matplotlib · seaborn · scipy · Power BI

![Dashboard](outputs/00.dashboard.png)


---

## Business Problem

Effective inventory and sales management are critical for optimizing profitability in the retail and wholesale industry. This analysis investigates whether the business is incurring losses due to inefficient pricing, poor inventory turnover, or over-dependence on a small number of vendors.

**Research Questions:**
1. Which brands have high margins but low sales — and could benefit from promotional attention?
2. How concentrated is procurement spend across vendors, and what is the supply chain risk?
3. Does bulk purchasing reduce unit costs, and by how much?
4. Which vendors have slow-moving inventory, and how much capital is locked in unsold stock?
5. Is there a statistically significant difference in profit margins between top and low-performing vendors?

---

## Data Pipeline

### Step 1 — Data Ingestion (`01_data_ingestion.py`)

Reads all CSV files from the `/data` folder and loads each into a SQLite database (`inventory.db`) using the filename as the table name. Logs ingestion activity and runtime.

**Source Tables:**

| Table | Description |
|---|---|
| `purchases` | Purchase transactions — vendor, brand, quantity, dollars |
| `purchase_prices` | Product-level pricing per vendor + brand |
| `vendor_invoice` | PO-level data including freight costs |
| `sales` | Sales transactions — brand, quantity, revenue, excise tax |

### Step 2 — Feature Engineering (`02_get_vendor_summary.py`)

Joins all four source tables using a CTE-based SQL query (3 CTEs: `FreightSummary`, `PurchaseSummary`, `SalesSummary`) into one flat `vendor_sales_summary` table. Cleans data (type casting, null fills, whitespace stripping) and engineers four business metrics:

| Metric | Formula |
|---|---|
| `GrossProfit` | TotalSalesDollars − TotalPurchaseDollars |
| `ProfitMargin` | (GrossProfit / TotalSalesDollars) × 100 |
| `StockTurnover` | TotalSalesQuantity / TotalPurchaseQuantity |
| `SalesToPurchaseRatio` | TotalSalesDollars / TotalPurchaseDollars |

Output saved to both `inventory.db` and `vendor_sales_summary.csv`.

### Step 3 — Analysis & Visualizations (`03_vendor_analysis.py`)

Loads the cleaned summary table, filters out records with negative/zero profit and zero sales for analysis integrity (10,692 raw → filtered for positive-profit analysis), then performs the full analysis documented below.

---

## Exploratory Data Analysis

### Distribution Analysis

All 16 numerical columns are heavily right-skewed, consistent with a retail dataset dominated by a long tail of small transactions and a small number of high-value outliers.

![Distributions](outputs/01_distributions.png)

**Key observations from the raw data:**
- **Gross Profit** has a minimum of −$52,002.78, indicating products sold below cost — likely heavy discounting or clearance activity.
- **Profit Margin** reaches −∞ where revenue is zero but purchase costs exist, confirming the presence of unsold inventory.
- **Freight Cost** ranges from $0.09 to $257,032 — extreme variation suggesting a mix of per-unit and bulk shipment logistics.
- **Stock Turnover** ranges from 0 to 274.5. Values above 1 indicate older stock fulfilling current-period orders.

These distributions informed the data filtering decisions: records with GrossProfit ≤ 0, ProfitMargin ≤ 0, and TotalSalesQuantity = 0 were excluded to focus the analysis on viable, profitable transactions.

### Correlation Analysis

![Correlation Heatmap](outputs/02_correlation_heatmap.png)

| Relationship | Correlation | Interpretation |
|---|---|---|
| Purchase Qty ↔ Sales Qty | **0.999** | Near-perfect — inventory is well-matched to demand |
| Purchase Price ↔ Gross Profit | −0.016 | Price alone does not drive margin |
| Profit Margin ↔ Total Sales Price | −0.179 | Higher prices compress margins (competitive pricing pressure) |
| Stock Turnover ↔ Gross Profit | −0.038 | Faster turnover ≠ higher profitability |

The 0.999 purchase-to-sales correlation is the standout finding — it confirms the business has strong demand forecasting. The weak price-to-profit correlation suggests margin is driven more by volume and mix than by unit pricing.

---

## Research Questions & Key Findings

### 1. Brands for Promotional or Pricing Adjustments

198 brands sit in the bottom 15% of sales but top 15% of profit margin — high-margin products that aren't moving.

![Promotional Brands — Table](outputs/03_promotional_brands.png)

![Promotional Brands — Scatter](outputs/04_promotional_brands_scatter.png)

The scatter plot isolates the target brands (red) in the upper-left quadrant: above the high-margin threshold (~65%) and below the low-sales threshold (~$560). These brands are profitable per unit but invisible to buyers — candidates for targeted promotions, bundle deals, or shelf placement changes rather than price cuts.

### 2. Vendor Procurement Concentration

The top 10 vendors account for **65.69%** of total procurement spend, with Diageo North America alone at 16.3%.

![Vendor Concentration — Donut](outputs/05_donut_vendor_scatter.png)

| Rank | Vendor | Contribution |
|---|---|---|
| 1 | Diageo North America Inc | 16.3% |
| 2 | Martignetti Companies | 8.3% |
| 3 | Pernod Ricard USA | 7.8% |
| 4 | Jim Beam Brands Company | 7.6% |
| 5 | Bacardi USA Inc | 5.7% |

This level of concentration creates supply chain risk — if any top-3 vendor faces disruption, over 32% of procurement is exposed. Diversification into secondary vendors for overlapping product categories would reduce this dependency.

### 3. Bulk Purchasing Impact on Unit Cost

Orders segmented into terciles by purchase quantity show a **72% reduction** in unit cost for large orders vs. small orders.

| Order Size | Avg Unit Price |
|---|---|
| Small | $39.06 |
| Medium | $15.49 |
| Large | $10.78 |

The cost curve flattens between Medium and Large (30% drop vs. 60% from Small to Medium), suggesting diminishing returns beyond the medium threshold. The business should target medium-to-large order sizes to capture the bulk of the savings without overcommitting to inventory.

### 4. Slow-Moving Inventory & Locked Capital

**$2.71M** in capital is locked in unsold inventory across all vendors.

| Lowest Turnover Vendors | Turnover | Highest Locked Capital | Value |
|---|---|---|---|
| Alisa Carr Beverages | 0.615 | Diageo North America Inc | $722.21K |
| Highland Wine Merchants LLC | 0.708 | Jim Beam Brands Company | $554.67K |
| Park Street Imports LLC | 0.751 | Pernod Ricard USA | $470.63K |
| Circa Wines | 0.756 | William Grant & Sons Inc | $401.96K |
| Dunn Wine Brokers | 0.766 | E & J Gallo Winery | $228.28K |

Notably, the vendors with the most locked capital (Diageo, Jim Beam, Pernod Ricard) are also the top procurement vendors. Their high purchase volumes naturally lead to higher absolute unsold inventory even with reasonable turnover ratios. The vendors with the *lowest turnover ratios* (Alisa Carr, Highland Wine) are the ones with structural demand problems — these should be reviewed for SKU rationalization or purchase quantity reduction.

### 5. Profit Margin: Top vs. Low-Performing Vendors

![Confidence Intervals](outputs/06_confidence_intervals.png)

| Group | 95% CI | Mean Margin |
|---|---|---|
| Top vendors (≥ 75th percentile sales) | 30.74% – 31.61% | **31.17%** |
| Low vendors (≤ 25th percentile sales) | 40.48% – 42.62% | **41.55%** |

**Welch's t-test result:** H₀ rejected (p < 0.05) — the difference is statistically significant.

This is a counterintuitive but important finding: low-volume vendors carry **~10 percentage points higher margins** than top sellers. This suggests two distinct operating models — high-volume vendors compete on scale and accept thinner margins, while niche vendors price at a premium but lack distribution reach. The business opportunity is to selectively invest in marketing and distribution for the highest-margin niche vendors to grow their volume without eroding their pricing power.

---

## Key Findings Summary

1. **Top 10 vendors drive 65.7% of procurement** — high dependency risk if any key vendor is disrupted
2. **Bulk purchasing reduces unit costs by ~72%** — large orders are significantly more cost-efficient, with diminishing returns above medium volume
3. **Low-performing vendors carry higher margins** (~41% vs ~31%) despite lower sales volume — untapped pricing and distribution opportunity
4. **$2.71M locked in slow-moving inventory** — vendors with turnover < 1 represent holding cost risk and cash flow drag
5. **Purchase-to-sales correlation of 0.999** confirms strong demand forecasting across the business
6. **198 brands flagged for promotional attention** — high margins but low visibility to buyers

---

## Project Structure

```
vendor-performance-analysis/
│
├── data/                            # Raw CSV files (not included — ~1.5 GB)
├── logs/                            # Ingestion and processing logs
│
├── 01_data_ingestion.py             # Loads CSVs into SQLite
├── 02_get_vendor_summary.py         # CTE joins, cleaning, feature engineering
├── 03_vendor_analysis.py            # Full analysis, stats, and chart generation
│
├── outputs/                         # All generated charts
│   ├── 00_dashboard.png
│   ├── 01_distributions.png
│   ├── 02_correlation_heatmap.png
│   ├── 03_promotional_brands.png
│   ├── 04_promotional_brands_scatter.png
│   ├── 05_donut_vendor_scatter.png
│   └── 06_confidence_intervals.png
│
├── vendor_sales_summary.csv         # Final aggregated summary table
├── vendor_performance.pbix          # Power BI dashboard
├── Vendor_Performance_Report.pdf    # Full written report
└── README.md
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.12 | Data processing and analysis |
| pandas | Data manipulation and aggregation |
| SQLite + SQLAlchemy | Database storage and CTE-based querying |
| matplotlib + seaborn | Statistical visualizations |
| scipy.stats | Welch's t-test and confidence intervals |
| Power BI | Interactive executive dashboard |

---

## Setup & Usage

> **Note:** The raw dataset (~1.5 GB) is not included due to file size constraints.

```bash
# Clone and install
git clone https://github.com/shababtahsin/vendor-performance-analysis-Portfolio-4.git
cd vendor-performance-analysis-Portfolio-4
pip install pandas sqlalchemy scipy matplotlib seaborn numpy

# Run the pipeline in order
python 01_data_ingestion.py       # Ingest CSVs → SQLite
python 02_get_vendor_summary.py   # Build vendor_sales_summary
python 03_vendor_analysis.py      # Generate all charts + stats
```

Open `vendor_performance.pbix` in Power BI Desktop for the interactive dashboard.

---

## Author

**Shah Tahsin**  
Business Data Analyst | SQL · Python · Power BI
