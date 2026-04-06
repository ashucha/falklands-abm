import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import f_oneway
import seaborn as sns
import os




# LOAD CSV
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "..", "analysis", "output_results 2.csv")
df = pd.read_csv(file_path)

# COLUMNS TO IMPORT
cols = [
    "spawn_zone",
    "naval_amphibs_landed",
    "naval_destroyers_remaining",
    "naval_frigates_remaining",
    "naval_conflict_days",
    "ground_conflict_days",
    "error_message"
]

# SUBSET DATA, remove outlier (visually identified)
df = df[cols].copy()
df = df.drop(index=8) # removing trial 9 which is an outlier
df = df.drop(index=16) # removing trial 17 which is an outlier

# Identify numeric columns
numeric_cols = [
    "naval_destroyers_remaining",
    "naval_frigates_remaining",
    "naval_conflict_days",
    "ground_conflict_days"
]

# Clean and convert columns to numeric by stripping whitespace and coercing invalid values to NaN
for col in numeric_cols:
    df[col] = pd.to_numeric(
        df[col].astype(str).str.strip(),
        errors="coerce"
    )

# CLEAN STRING COLUMNS
df["spawn_zone"] = df["spawn_zone"].astype(str).str.strip()
df["error_message"] = df["error_message"].astype(str).str.strip()


# DERIVED METRICS
df["naval_conflict_days"] = df["naval_conflict_days"]
df["ground_conflict_days"] = df["ground_conflict_days"]
df["amphibs_landed"] = df["naval_amphibs_landed"]
df["boats_left"] = df["naval_destroyers_remaining"] + df["naval_frigates_remaining"]
df["total_days"] = df["naval_conflict_days"] + df["ground_conflict_days"]
df["exocet_hit"] = df["error_message"].str.contains("carrier", case=False, na=False).astype(int)

# --- understand data with summary stats ---
summary_stats = df.groupby("spawn_zone")["total_days"].agg([
    "count",
    "mean",
    "std",
    "var",
    "min",
    "max"
])

print("\nVariance by zone:")
print(summary_stats)


# --- anova test ---
# choose metric
metrics = ["amphibs_landed", "boats_left", "total_days"]

for metric in metrics:
    groups = [
        df[df["spawn_zone"] == "zone-1"][metric].dropna(),
        df[df["spawn_zone"] == "zone-2"][metric].dropna(),
        df[df["spawn_zone"] == "zone-3"][metric].dropna(),
        df[df["spawn_zone"] == "zone-4"][metric].dropna(),
        df[df["spawn_zone"] == "zone-5"][metric].dropna()
    ]

    f_stat, p_val = f_oneway(*groups)

    print(f"\nANOVA results for {metric}:")
    print(f"F = {f_stat:.3f}, p = {p_val:.6f}")


# --- bar chart ---
# GROUP BY ZONE AND AVERAGE
summary = df.groupby("spawn_zone").agg({
    "amphibs_landed": "mean",
    "boats_left": "mean",
    "total_days": "mean",
    "exocet_hit": "sum"   
})

# OPTIONAL: enforce zone order 1–5
summary = summary.reindex(["zone-5", "zone-4", "zone-3", "zone-2", "zone-1"])
# MAKE BAR CHART
ax = summary.plot(kind="bar", figsize=(10,6))

plt.xlabel("Spawn Zone")
plt.ylabel("Average Value")
plt.title("Average Outcomes by Spawn Zone")

plt.legend([
    "Amphibs Landed",
    "Boats Left",
    "Total Days",
    "Exocet Hits"
])

# ADD VALUE LABELS ON BARS
for container in ax.containers:
    ax.bar_label(container, fmt="%.2f", padding=2, fontsize=6)

plt.tight_layout()
plt.show(block=False)

# --- cross correlation matrix? ---
# choose the columns you want in the matrix
plot_cols = [
    "amphibs_landed",
    "boats_left",
    "naval_conflict_days",
    "exocet_hit"
]

print(df[plot_cols + ["spawn_zone"]].dtypes)
print(df[plot_cols + ["spawn_zone"]].shape)
print(df[plot_cols].isna().sum())

# make the pair plot
sns.pairplot(
    df,
    vars=plot_cols,
    hue="spawn_zone",      # colors points by zone
    diag_kind="hist"       # histograms on diagonal
)

plt.show()

# --- create pdf output ---
# =========================
# EXPORT EVERYTHING TO PDF
# =========================
from matplotlib.backends.backend_pdf import PdfPages

pdf_path = os.path.join(base_dir, "..", "analysis", "analysis_report.pdf")

with PdfPages(pdf_path) as pdf:

    # --- PAGE 1: Summary Statistics (as text) ---
    fig, ax = plt.subplots(figsize=(8.5, 11))
    ax.axis('off')

    text = "Variance by Zone:\n\n"
    text += summary_stats.to_string()

    ax.text(0, 1, text, va='top', fontsize=10, family='monospace')
    pdf.savefig(fig)
    plt.close()


    # --- PAGE 2: ANOVA Results ---
    fig, ax = plt.subplots(figsize=(8.5, 11))
    ax.axis('off')

    anova_text = "ANOVA Results:\n\n"

    for metric in metrics:
        groups = [
            df[df["spawn_zone"] == "zone-1"][metric].dropna(),
            df[df["spawn_zone"] == "zone-2"][metric].dropna(),
            df[df["spawn_zone"] == "zone-3"][metric].dropna(),
            df[df["spawn_zone"] == "zone-4"][metric].dropna(),
            df[df["spawn_zone"] == "zone-5"][metric].dropna()
        ]

        f_stat, p_val = f_oneway(*groups)

        anova_text += f"{metric}:\n"
        anova_text += f"F = {f_stat:.3f}, p = {p_val:.6f}\n\n"

    ax.text(0, 1, anova_text, va='top', fontsize=10, family='monospace')
    pdf.savefig(fig)
    plt.close()


    # --- PAGE 3: Bar Chart ---
    fig, ax = plt.subplots(figsize=(10, 6))

    summary.plot(kind="bar", ax=ax)

    ax.set_xlabel("Spawn Zone")
    ax.set_ylabel("Average Value")
    ax.set_title("Average Outcomes by Spawn Zone")

    ax.legend([
        "Amphibs Landed",
        "Boats Left",
        "Total Days",
        "Exocet Hits"
    ])

    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", padding=2, fontsize=6)

    fig.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


    # --- PAGE 4+: Pairplot (multiple pages automatically handled) ---
    pairplot = sns.pairplot(
        df,
        vars=plot_cols,
        hue="spawn_zone",
        diag_kind="hist"
    )

    pdf.savefig(pairplot.fig)
    plt.close()

print(f"\nPDF saved to: {pdf_path}")