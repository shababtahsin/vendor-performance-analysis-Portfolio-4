# =============================================================================
# 03_vendor_analysis.py
# Performs full vendor performance analysis including:
#   - Distribution and outlier analysis
#   - Correlation heatmap
#   - Top vendors and brands by sales
#   - Pareto / procurement concentration
#   - Bulk purchasing impact on unit cost
#   - Slow-moving inventory and locked capital
#   - Brands needing promotional attention
#   - Statistical T-test: top vs low-performing vendors
# All charts are saved to the /outputs folder.
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import warnings
import os
from scipy.stats import ttest_ind
import scipy.stats as stats

warnings.filterwarnings('ignore')
os.makedirs('outputs', exist_ok=True)


# =============================================================================
# HELPERS
# =============================================================================

def format_dollars(value):
    """Format large numbers as readable dollar strings (e.g. 1.23M, 456.78K)."""
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.2f}K"
    else:
        return str(round(value, 2))


def confidence_interval(data, confidence=0.95):
    """Compute mean and confidence interval bounds for a data series."""
    mean_val = np.mean(data)
    std_err = np.std(data, ddof=1) / np.sqrt(len(data))
    t_critical = stats.t.ppf((1 + confidence) / 2, df=len(data) - 1)
    margin_of_error = t_critical * std_err
    return mean_val, mean_val - margin_of_error, mean_val + margin_of_error


# =============================================================================
# LOAD DATA
# =============================================================================

conn = sqlite3.connect('inventory.db')
df_raw = pd.read_sql_query("SELECT * FROM vendor_sales_summary", conn)
conn.close()

# Filter out negative/zero profit and zero sales for clean analysis
df = df_raw[
    (df_raw['GrossProfit'] > 0) &
    (df_raw['ProfitMargin'] > 0) &
    (df_raw['TotalSalesQuantity'] > 0)
].copy()

numerical_cols = df.select_dtypes(include=np.number).columns
print(f'Records loaded: {len(df_raw)} raw → {len(df)} after filtering')


# =============================================================================
# 1. DISTRIBUTION PLOTS
# =============================================================================

plt.figure(figsize=(15, 10))
for i, col in enumerate(numerical_cols):
    plt.subplot(4, 4, i + 1)
    sns.histplot(df[col], kde=True, bins=30)
    plt.title(col)
plt.tight_layout()
plt.savefig('outputs/01_distributions.png', dpi=150)
plt.close()
print('Saved: outputs/01_distributions.png')


# =============================================================================
# 2. BOXPLOTS (OUTLIER DETECTION)
# =============================================================================

plt.figure(figsize=(15, 10))
for i, col in enumerate(numerical_cols):
    plt.subplot(4, 4, i + 1)
    sns.boxplot(y=df[col])
    plt.title(col)
plt.tight_layout()
plt.savefig('outputs/02_boxplots.png', dpi=150)
plt.close()
print('Saved: outputs/02_boxplots.png')


# =============================================================================
# 3. CORRELATION HEATMAP
# =============================================================================

plt.figure(figsize=(12, 8))
corr_matrix = df[numerical_cols].corr()
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
plt.title("Correlation Heatmap")
plt.tight_layout()
plt.savefig('outputs/03_correlation_heatmap.png', dpi=150)
plt.close()
print('Saved: outputs/03_correlation_heatmap.png')


# =============================================================================
# 4. TOP VENDORS & BRANDS BY SALES
# =============================================================================

top_vendors = df.groupby("VendorName")["TotalSalesDollars"].sum().nlargest(10)
top_brands  = df.groupby("Description")["TotalSalesDollars"].sum().nlargest(10)

plt.figure(figsize=(15, 5))

plt.subplot(1, 2, 1)
ax1 = sns.barplot(y=top_vendors.index, x=top_vendors.values, palette="Blues_r")
for bar in ax1.patches:
    ax1.text(bar.get_width() + (bar.get_width() * 0.02),
             bar.get_y() + bar.get_height() / 2,
             format_dollars(bar.get_width()),
             ha='left', va='center', fontsize=10)
plt.title("Top 10 Vendors by Sales")

plt.subplot(1, 2, 2)
ax2 = sns.barplot(y=top_brands.index.astype(str), x=top_brands.values, palette="Reds_r")
for bar in ax2.patches:
    ax2.text(bar.get_width() + (bar.get_width() * 0.02),
             bar.get_y() + bar.get_height() / 2,
             format_dollars(bar.get_width()),
             ha='left', va='center', fontsize=10)
plt.title("Top 10 Brands by Sales")

plt.tight_layout()
plt.savefig('outputs/04_top_vendors_brands.png', dpi=150)
plt.close()
print('Saved: outputs/04_top_vendors_brands.png')


# =============================================================================
# 5. PARETO CHART — VENDOR PROCUREMENT CONCENTRATION
# =============================================================================

vendor_perf = df.groupby("VendorName").agg({
    "TotalPurchaseDollars": "sum",
    "GrossProfit": "sum",
    "TotalSalesDollars": "sum"
}).reset_index()

vendor_perf["Purchase_Contribution%"] = (
    vendor_perf["TotalPurchaseDollars"] / vendor_perf["TotalPurchaseDollars"].sum()
) * 100

vendor_perf = round(vendor_perf.sort_values("TotalPurchaseDollars", ascending=False), 2)
top10 = vendor_perf.head(10).copy()
top10["Cumulative_Contribution%"] = top10["Purchase_Contribution%"].cumsum()

fig, ax1 = plt.subplots(figsize=(10, 6))
sns.barplot(x=top10['VendorName'], y=top10['Purchase_Contribution%'], palette="mako", ax=ax1)
for i, value in enumerate(top10['Purchase_Contribution%']):
    ax1.text(i, value - 1, f'{value}%', ha='center', fontsize=10, color='white')

ax2 = ax1.twinx()
ax2.plot(top10['VendorName'], top10['Cumulative_Contribution%'],
         color='red', marker='o', linestyle='dashed', label='Cumulative %')
ax2.axhline(y=100, color='gray', linestyle='dashed', alpha=0.7)
ax2.legend(loc='upper right')

ax1.set_xticklabels(top10['VendorName'], rotation=90)
ax1.set_ylabel('Purchase Contribution %', color='blue')
ax2.set_ylabel('Cumulative Contribution %', color='red')
ax1.set_title('Pareto Chart: Vendor Contribution to Total Purchases')
plt.tight_layout()
plt.savefig('outputs/05_pareto_vendor_concentration.png', dpi=150)
plt.close()
print('Saved: outputs/05_pareto_vendor_concentration.png')

total_contrib = top10['Purchase_Contribution%'].sum()
print(f'  → Top 10 vendors account for {total_contrib:.2f}% of total procurement')


# =============================================================================
# 6. DONUT CHART — VENDOR CONCENTRATION
# =============================================================================

vendors_list = list(top10['VendorName'].values)
contributions = list(top10['Purchase_Contribution%'].values)
remaining = 100 - sum(contributions)
vendors_list.append("Other Vendors")
contributions.append(remaining)

fig, ax = plt.subplots(figsize=(8, 8))
wedges, texts, autotexts = ax.pie(
    contributions, labels=vendors_list, autopct='%1.1f%%',
    startangle=140, pctdistance=0.85, colors=plt.cm.Paired.colors
)
centre_circle = plt.Circle((0, 0), 0.70, fc='white')
fig.gca().add_artist(centre_circle)
plt.text(0, 0, f"Top 10 Total:\n{sum(contributions[:-1]):.2f}%",
         fontsize=14, fontweight='bold', ha='center', va='center')
plt.title("Top 10 Vendor Purchase Contribution (%)")
plt.tight_layout()
plt.savefig('outputs/06_donut_vendor_concentration.png', dpi=150)
plt.close()
print('Saved: outputs/06_donut_vendor_concentration.png')


# =============================================================================
# 7. BULK PURCHASING IMPACT ON UNIT PRICE
# =============================================================================

df["UnitPurchasePrice"] = df["TotalPurchaseDollars"] / df["TotalPurchaseQuantity"]
df["OrderSize"] = pd.qcut(df["TotalPurchaseQuantity"], q=3, labels=["Small", "Medium", "Large"])

bulk_analysis = df.groupby("OrderSize")["UnitPurchasePrice"].mean().reset_index()
print('\nBulk Purchase Analysis:')
print(bulk_analysis.to_string(index=False))

plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x="OrderSize", y="UnitPurchasePrice", palette="Set2")
plt.title("Impact of Bulk Purchasing on Unit Price")
plt.xlabel("Order Size")
plt.ylabel("Average Unit Purchase Price ($)")
plt.tight_layout()
plt.savefig('outputs/07_bulk_purchasing_impact.png', dpi=150)
plt.close()
print('Saved: outputs/07_bulk_purchasing_impact.png')


# =============================================================================
# 8. SLOW-MOVING INVENTORY
# =============================================================================

low_turnover = (
    df[df["StockTurnover"] < 1]
    .groupby("VendorName")["StockTurnover"]
    .mean()
    .reset_index()
    .sort_values("StockTurnover", ascending=True)
)

print(f'\nVendors with StockTurnover < 1 (top 10):')
print(low_turnover.head(10).to_string(index=False))


# =============================================================================
# 9. CAPITAL LOCKED IN UNSOLD INVENTORY
# =============================================================================

df["UnsoldInventoryValue"] = (
    (df["TotalPurchaseQuantity"] - df["TotalSalesQuantity"]) * df["PurchasePrice"]
)

total_locked = df["UnsoldInventoryValue"].sum()
print(f'\nTotal capital locked in unsold inventory: {format_dollars(total_locked)}')

locked_per_vendor = (
    df.groupby("VendorName")["UnsoldInventoryValue"]
    .sum()
    .reset_index()
    .sort_values("UnsoldInventoryValue", ascending=False)
)
locked_per_vendor['UnsoldInventoryValue_fmt'] = locked_per_vendor['UnsoldInventoryValue'].apply(format_dollars)
print('\nTop 10 vendors by locked capital:')
print(locked_per_vendor.head(10)[['VendorName', 'UnsoldInventoryValue_fmt']].to_string(index=False))


# =============================================================================
# 10. BRANDS NEEDING PROMOTIONAL ATTENTION
#     (Low sales, but high profit margin)
# =============================================================================

brand_perf = df.groupby('Description').agg({
    'TotalSalesDollars': 'sum',
    'ProfitMargin': 'mean'
}).reset_index()

low_sales_threshold  = brand_perf['TotalSalesDollars'].quantile(0.15)
high_margin_threshold = brand_perf['ProfitMargin'].quantile(0.85)

target_brands = brand_perf[
    (brand_perf['TotalSalesDollars'] <= low_sales_threshold) &
    (brand_perf['ProfitMargin'] >= high_margin_threshold)
]

print(f'\nBrands with low sales but high margins (candidates for promotion):')
print(target_brands.sort_values('TotalSalesDollars').to_string(index=False))

brand_perf_viz = brand_perf[brand_perf['TotalSalesDollars'] < 10000]

plt.figure(figsize=(10, 6))
sns.scatterplot(data=brand_perf_viz, x='TotalSalesDollars', y='ProfitMargin',
                color="blue", label="All Brands", alpha=0.2)
sns.scatterplot(data=target_brands, x='TotalSalesDollars', y='ProfitMargin',
                color="red", label="Target Brands")
plt.axhline(high_margin_threshold, linestyle='--', color='black', label="High Margin Threshold")
plt.axvline(low_sales_threshold, linestyle='--', color='black', label="Low Sales Threshold")
plt.xlabel("Total Sales ($)")
plt.ylabel("Profit Margin (%)")
plt.title("Brands for Promotional or Pricing Adjustments")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('outputs/08_promotional_brands.png', dpi=150)
plt.close()
print('Saved: outputs/08_promotional_brands.png')


# =============================================================================
# 11. STATISTICAL TEST — TOP vs LOW PERFORMING VENDORS
# =============================================================================

top_threshold = df["TotalSalesDollars"].quantile(0.75)
low_threshold = df["TotalSalesDollars"].quantile(0.25)

top_vendors_ci = df[df["TotalSalesDollars"] >= top_threshold]["ProfitMargin"].dropna()
low_vendors_ci = df[df["TotalSalesDollars"] <= low_threshold]["ProfitMargin"].dropna()

top_mean, top_lower, top_upper = confidence_interval(top_vendors_ci)
low_mean, low_lower, low_upper = confidence_interval(low_vendors_ci)

t_stat, p_value = ttest_ind(top_vendors_ci, low_vendors_ci, equal_var=False)

print(f'\n--- Statistical Test: Profit Margin (Top vs Low Vendors) ---')
print(f'Top Vendors  95% CI: ({top_lower:.2f}, {top_upper:.2f}), Mean: {top_mean:.2f}%')
print(f'Low Vendors  95% CI: ({low_lower:.2f}, {low_upper:.2f}), Mean: {low_mean:.2f}%')
print(f'T-Statistic: {t_stat:.4f} | P-Value: {p_value:.4f}')
if p_value < 0.05:
    print('Result: Reject H₀ — Significant difference in profit margins between groups.')
else:
    print('Result: Fail to reject H₀ — No significant difference found.')

plt.figure(figsize=(12, 6))
sns.histplot(top_vendors_ci, kde=True, color="blue", bins=30, alpha=0.5, label="Top Vendors")
plt.axvline(top_lower, color="blue", linestyle="--", label=f"Top Lower: {top_lower:.2f}")
plt.axvline(top_upper, color="blue", linestyle="--", label=f"Top Upper: {top_upper:.2f}")
plt.axvline(top_mean,  color="blue", linestyle="-",  label=f"Top Mean:  {top_mean:.2f}")

sns.histplot(low_vendors_ci, kde=True, color="red", bins=30, alpha=0.5, label="Low Vendors")
plt.axvline(low_lower, color="red", linestyle="--", label=f"Low Lower: {low_lower:.2f}")
plt.axvline(low_upper, color="red", linestyle="--", label=f"Low Upper: {low_upper:.2f}")
plt.axvline(low_mean,  color="red", linestyle="-",  label=f"Low Mean:  {low_mean:.2f}")

plt.title("95% Confidence Interval: Top vs Low Vendor Profit Margins")
plt.xlabel("Profit Margin (%)")
plt.ylabel("Frequency")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('outputs/09_confidence_intervals.png', dpi=150)
plt.close()
print('Saved: outputs/09_confidence_intervals.png')

print('\nAll analysis complete. Charts saved to /outputs folder.')
