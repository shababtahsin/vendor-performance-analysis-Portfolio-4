# 📦 Vendor Performance & Inventory Analysis

![Python](https://img.shields.io/badge/Python-Analysis-blue)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

## Project Overview

This project analyses vendor, purchasing, sales and inventory behaviour using a large retail dataset originally containing approximately **1.5 GB of raw data across four source tables**.

The workflow combines:

- **Python** for data processing and analysis
- **SQLite + SQLAlchemy** for data storage and aggregation
- **pandas** for feature engineering
- **scipy** for statistical testing
- **Power BI** for reporting

The main goal was to understand vendor performance from several angles:

- procurement concentration
- purchase volume and unit cost
- sales and purchase relationships
- inventory movement
- margin behaviour
- products with low sales but relatively high margins

> The project focuses on analytical relationships and portfolio screening rather than accounting-grade inventory or profitability reporting.

---

## Dashboard Preview

![Vendor Performance Dashboard](screenshots/00.dashboard.png)

---

# 🎯 Business Questions

The project explored five main questions:

1. Which products combine relatively high margins with low sales?
2. How concentrated is procurement across major vendors?
3. Are higher purchase volumes associated with lower average unit prices?
4. Which vendors show weaker sales-to-purchase quantity ratios?
5. Do high-sales and low-sales records show different margin behaviour?

---

# 🧱 Data Pipeline

```text
Raw CSV Files
     ↓
Python Ingestion
     ↓
SQLite Database
     ↓
SQL CTE Aggregation
     ↓
Vendor-Product Summary
     ↓
Python Analysis
     ↓
Power BI
```

---

# 1️⃣ Data Ingestion

**Script**

```text
python/01_data_ingestion.py
```

The ingestion script reads CSV files and loads each source into a SQLite database called:

```text
inventory.db
```

The original project used four main source tables:

| Table | Purpose |
|---|---|
| `purchases` | Purchase quantity and purchase-value records |
| `purchase_prices` | Product and vendor price information |
| `vendor_invoice` | Vendor-level freight information |
| `sales` | Sales quantity, sales value and excise tax |

The raw source files are not included in this repository because of their size.

---

# 2️⃣ Vendor Summary Creation

**Script**

```text
python/02_get_vendor_summary.py
```

The second stage builds an analytical vendor-product summary using SQL CTEs:

```text
FreightSummary
PurchaseSummary
SalesSummary
```

The resulting table contains one analytical row per vendor-product combination in the exported summary.

The processed summary contains:

**10,692 rows**

and is included in the repository as:

```text
data/vendor_sales_summary.csv
```

---

## Derived Metrics

Several analytical fields were created.

| Code Field | Formula | Interpretation |
|---|---|---|
| `GrossProfit` | Sales Dollars − Purchase Dollars | **Sales–Purchase Value Difference / Gross Profit Proxy** |
| `ProfitMargin` | GrossProfit ÷ Sales Dollars × 100 | **Margin Proxy** |
| `StockTurnover` | Sales Quantity ÷ Purchase Quantity | **Sales-to-Purchase Quantity Ratio** |
| `SalesToPurchaseRatio` | Sales Dollars ÷ Purchase Dollars | Sales value relative to purchase value |

### Important Metric Note

The source data does not provide accounting COGS or average inventory.

For that reason:

- `GrossProfit` should be treated as a **gross-profit proxy**
- `ProfitMargin` should be treated as a **margin proxy**
- `StockTurnover` should be interpreted as a **sales-to-purchase quantity ratio**, not standard accounting inventory turnover

These measures are still useful for comparative analysis, but their definitions matter.

---

# 3️⃣ Analytical Dataset

**Script**

```text
python/03_vendor_analysis.py
```

The raw analytical summary contains:

**10,692 vendor-product records**

For the profitability-focused analysis, the script keeps records where:

```text
GrossProfit > 0
ProfitMargin > 0
TotalSalesQuantity > 0
```

This produces an analytical subset of:

**8,565 records across 119 vendors**

The filtered subset contains approximately:

| Metric | Value |
|---|---:|
| Sales | **$441.41M** |
| Purchases | **$307.34M** |
| Sales–Purchase Value Difference | **$134.07M** |
| Vendors | **119** |

> These headline figures describe the filtered analytical subset rather than the complete 10,692-row summary.

For reference, the full processed summary contains approximately:

- **$451.62M sales**
- **$321.90M purchases**

---

# 📊 Exploratory Analysis

## Distribution Analysis

![Distributions](screenshots/01.distributions.png)

The analysis shows strongly right-skewed distributions across many financial variables.

This means that most vendor-product combinations sit toward the lower end of the distribution while a smaller number account for much larger purchase and sales values.

The original summary also contains:

- loss-making records
- records with no sales
- highly variable freight values
- unusually large sales-to-purchase quantity ratios

These characteristics motivated the use of a filtered subset for the profitability-focused analysis.

---

# 🔗 Correlation Analysis

![Correlation Heatmap](screenshots/02.correlation_heatmap.png)

The filtered analytical dataset produced the following relationships:

| Relationship | Correlation | Interpretation |
|---|---:|---|
| Purchase Quantity ↔ Sales Quantity | **0.999** | Extremely strong positive relationship |
| Purchase Price ↔ Gross Profit Proxy | **−0.016** | Almost no linear relationship |
| Margin Proxy ↔ Total Sales Price | **−0.180** | Weak negative relationship |
| Sales-to-Purchase Quantity Ratio ↔ Gross Profit Proxy | **−0.038** | Almost no linear relationship |

The strongest relationship is between purchase quantity and sales quantity.

This indicates that purchasing and realised sales volumes move very closely together in the aggregated vendor-product data.

However:

> **Correlation does not prove forecasting quality or causation.**

The result should therefore be treated as a descriptive relationship.

---

# 🔎 Research Question 1  
## Which Products May Need Promotional Attention?

The analysis searched for product descriptions that were:

- in the **bottom 15% of sales**
- and in the **top 15% of margin proxy**

This identified:

**198 product-description groups**

![Promotional Products](screenshots/03.promotional_brands.png)

![Promotional Scatter](screenshots/04.promotional_brands_scatter.png)

These products combine:

```text
Relatively Low Sales
        +
Relatively High Margin Proxy
```

They may therefore be useful candidates for further investigation.

Possible actions could include testing:

- targeted promotions
- bundle offers
- improved placement
- broader distribution
- additional marketing

The analysis does **not** automatically recommend discounting these products.

Their relatively strong margins mean that reducing price without further analysis could weaken profitability.

---

# 🏢 Research Question 2  
## How Concentrated Is Procurement?

Procurement is concentrated among a relatively small number of vendors.

Within the filtered analytical subset:

**Top 10 vendors account for approximately 65.69% of purchase value.**

![Vendor Concentration](screenshots/05.donut_vendor_scatter.png)

### Largest Vendors by Purchase Contribution

| Rank | Vendor | Approx. Contribution |
|---|---|---:|
| 1 | Diageo North America Inc | **16.3%** |
| 2 | Martignetti Companies | **8.3%** |
| 3 | Pernod Ricard USA | **7.8%** |
| 4 | Jim Beam Brands Company | **7.6%** |
| 5 | Bacardi USA Inc | **5.7%** |

The top three vendors together account for more than:

**32% of purchase value**

This does not automatically indicate excessive supplier risk.

However, it highlights relationships that may be worth monitoring for:

- supplier dependency
- negotiation leverage
- pricing exposure
- supply availability
- alternative sourcing options

---

# 📦 Research Question 3  
## How Does Purchase Volume Relate to Unit Price?

The analytical records were divided into three groups according to total purchase quantity.

| Purchase Volume Group | Avg Unit Purchase Price |
|---|---:|
| Low Volume | **$39.06** |
| Medium Volume | **$15.49** |
| High Volume | **$10.78** |

The high-volume group has an average unit price approximately:

**72% lower than the low-volume group**

The strongest difference occurs between the low- and medium-volume groups.

The difference between medium and high volume is smaller.

### Interpretation

Higher purchase volumes are associated with lower unit prices in this dataset.

However, the groups contain different products and vendors.

Therefore:

> The result does **not prove that increasing purchase quantity directly causes lower prices**.

Product mix, vendor mix and product category may also explain part of the difference.

---

# 📉 Research Question 4  
## Which Vendors Show Lower Sales-to-Purchase Ratios?

The project originally labelled this metric `StockTurnover`.

Its actual calculation is:

```text
Total Sales Quantity
÷
Total Purchase Quantity
```

For portfolio interpretation, it is better described as:

> **Sales-to-Purchase Quantity Ratio**

A ratio below `1.0` means that recorded sales quantity was lower than recorded purchase quantity during the observed data.

Some of the lowest average vendor ratios were:

| Vendor | Sales-to-Purchase Qty Ratio |
|---|---:|
| Alisa Carr Beverages | **0.615** |
| Highland Wine Merchants LLC | **0.708** |
| Park Street Imports LLC | **0.751** |
| Circa Wines | **0.756** |
| Dunn Wine Brokers | **0.766** |

These vendors may be worth further investigation.

Possible questions include:

- Were purchase quantities unusually high?
- Was demand weaker than expected?
- Were products purchased late in the observation period?
- Was there beginning inventory that affects the comparison?
- Are specific SKUs responsible for the result?

---

# 💰 Purchase-Minus-Sales Inventory Proxy

The project also calculates:

```text
(Purchase Quantity − Sales Quantity)
× Purchase Price
```

The net result across the filtered analytical subset is approximately:

**$2.71M**

This should **not** be interpreted as verified ending inventory.

Why?

Because the dataset does not provide complete information about:

- beginning inventory
- timing of purchases
- timing of sales
- physical ending inventory
- inventory adjustments

Some product records also have:

```text
Sales Quantity > Purchase Quantity
```

which creates negative implied inventory positions.

Therefore the $2.71M result is best treated as a:

> **Net purchase-minus-sales inventory value proxy**

rather than actual capital confirmed to be tied up in inventory.

---

## Vendors With Large Positive Inventory Proxies

Some of the largest positive vendor-level values were:

| Vendor | Approx. Inventory Proxy |
|---|---:|
| Diageo North America Inc | **$722.21K** |
| Jim Beam Brands Company | **$554.67K** |
| Pernod Ricard USA | **$470.63K** |
| William Grant & Sons Inc | **$401.96K** |
| E & J Gallo Winery | **$228.28K** |

These vendors are also large procurement partners.

Their absolute inventory proxy therefore needs to be interpreted alongside their overall purchasing scale.

---

# 📐 Research Question 5  
## Do High-Sales and Low-Sales Records Show Different Margins?

![Confidence Intervals](screenshots/06.confidence_intervals.png)

The current Python analysis divides **vendor-product records** into sales quartiles.

It compares:

```text
Top 25% of vendor-product records by sales
vs
Bottom 25% of vendor-product records by sales
```

The results were:

| Group | 95% CI | Mean Margin Proxy |
|---|---|---:|
| High-Sales Records | 30.74% – 31.61% | **31.17%** |
| Low-Sales Records | 40.48% – 42.62% | **41.55%** |

A Welch's t-test produced:

**p < 0.05**

This indicates a statistically significant difference in margin proxy between the two **record-level sales groups** in the current analytical dataset.

The difference is approximately:

**10.38 percentage points**

### Important Statistical Interpretation

This test operates at the **vendor-product record level**.

It should therefore not be interpreted as proving that entire high-sales vendors have lower margins than entire low-sales vendors.

The result instead shows that:

> Higher-sales vendor-product records in the analytical subset have lower average margin proxies than lower-sales records.

A separate vendor-level aggregation would be required to make a statistical statement specifically about high-sales versus low-sales vendors.

---

# 🚚 Freight Grain

Freight is calculated in the SQL pipeline at:

```text
Vendor Level
```

That vendor-level freight amount is then attached to each vendor-product record belonging to the same vendor.

Therefore:

> `FreightCost` must not be summed directly across vendor-product rows.

Doing so would count the same vendor-level freight amount multiple times.

Freight should be analysed either:

- once per vendor
- or after allocating freight across products using a defined allocation rule

This is an important grain consideration in the model.

---

# 📌 Key Findings

## 🟢 1. Procurement Is Concentrated

The top 10 vendors account for approximately:

**65.7% of purchase value**

This makes supplier concentration an important area to monitor.

---

## 📦 2. Higher Purchase Volume Is Associated With Lower Unit Cost

Average unit purchase price falls from:

**$39.06 → $15.49 → $10.78**

across low-, medium- and high-volume groups.

The pattern is strong, but it should not be interpreted as causal without controlling for vendor and product mix.

---

## 💰 3. Lower-Sales Records Show Higher Margin Proxies

Low-sales vendor-product records average approximately:

**41.55% margin proxy**

compared with:

**31.17%**

for high-sales records.

This difference was statistically significant in the current record-level comparison.

---

## 🎯 4. 198 Product Groups Combine Low Sales With High Margins

These products may be useful candidates for:

- marketing tests
- distribution review
- bundle strategies
- promotional experiments

before considering price reductions.

---

## 🔗 5. Purchase and Sales Quantities Move Closely Together

The correlation between aggregated purchase quantity and sales quantity is approximately:

**0.999**

This shows a very strong relationship but does not establish forecasting accuracy.

---

## 📉 6. Inventory Movement Varies Substantially

Some vendors show much lower sales-to-purchase quantity ratios than others.

These vendors may warrant deeper review of:

- purchase planning
- product demand
- SKU mix
- timing
- replenishment behaviour

---

# 🎯 Main Business Takeaway

The main lesson from this project is that **vendor performance cannot be judged using sales alone**.

A vendor may simultaneously:

- generate high sales
- account for a large share of procurement
- operate at a lower margin proxy
- and show a large purchase-minus-sales inventory position

At the same time, some lower-sales products show much stronger margin behaviour.

The most useful approach is therefore to consider:

> **Sales + Purchase Value + Margin + Procurement Concentration + Inventory Movement**

together before deciding where action is required.

---

# 🖥️ Power BI

The Power BI report provides an interactive view of vendor performance and the main analytical findings.

**File**

```text
powerbi/vendor_performance.pbix
```

The dashboard helps explore:

- vendor performance
- procurement concentration
- sales and purchase values
- margin proxies
- inventory movement
- product-level performance

![Dashboard](screenshots/00.dashboard.png)

---

# 📁 Repository Structure

```text
vendor-performance-analysis-Portfolio-4/
│
├── README.md
├── LICENSE
├── .gitignore.txt
│
├── data/
│   └── vendor_sales_summary.csv
│
├── python/
│   ├── 01_data_ingestion.py
│   ├── 02_get_vendor_summary.py
│   └── 03_vendor_analysis.py
│
├── powerbi/
│   └── vendor_performance.pbix
│
└── screenshots/
    ├── 00.dashboard.png
    ├── 01.distributions.png
    ├── 02.correlation_heatmap.png
    ├── 03.promotional_brands.png
    ├── 04.promotional_brands_scatter.png
    ├── 05.donut_vendor_scatter.png
    └── 06.confidence_intervals.png
```

---

# ▶️ Running the Project

## Using the Included Processed Dataset

The repository includes:

```text
data/vendor_sales_summary.csv
```

This allows the processed analytical dataset to be inspected without downloading the original ~1.5 GB raw files.

---

## Full Raw-Data Pipeline

The full ingestion pipeline requires the original source CSV files used to create:

```text
purchases
purchase_prices
vendor_invoice
sales
```

Those files are not included in this repository because of their size.

The source scripts documenting the original workflow are available in:

```text
python/
```

---

# 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Data processing and analysis |
| pandas | Cleaning, transformation and aggregation |
| SQLite | Local analytical database |
| SQLAlchemy | Database ingestion |
| SQL / CTEs | Vendor, purchase, sales and freight aggregation |
| scipy.stats | Welch's t-test and confidence intervals |
| matplotlib | Visualisation |
| seaborn | Statistical visualisation |
| Power BI | Interactive reporting |

---

# 🧠 Skills Demonstrated

### Python

```text
pandas
groupby
feature engineering
quantiles
correlation
statistical testing
visualisation
```

### SQL

```text
CTEs
aggregation
joins
grain management
vendor-product modelling
```

### Statistics

```text
Correlation
Confidence Intervals
Welch's T-Test
Quartile Segmentation
```

### Business Analysis

```text
Vendor Performance
Procurement Concentration
Purchase-Volume Analysis
Margin Analysis
Inventory Screening
Product Opportunity Analysis
```

---

# 📌 Overall Conclusion

The project found substantial variation in vendor and product performance.

Within the main analytical subset:

- approximately **$441.41M in sales** was analysed
- approximately **$307.34M in purchases** was analysed
- the top 10 vendors represented around **65.7% of purchase value**
- high purchase-volume groups had lower average unit prices
- lower-sales vendor-product records had higher average margin proxies
- **198 product-description groups** combined relatively high margins with low sales
- purchase and sales quantities were extremely closely related

The main conclusion is that vendor decisions should not be based on one measure alone.

**Sales, purchasing, margin behaviour, supplier concentration and inventory movement need to be analysed together to understand where opportunities and risks actually exist.**

---

## 👤 Author

**Shah Tahsin**  
Business Data Analyst | SQL · Python · Power BI

[GitHub](https://github.com/shababtahsin)
