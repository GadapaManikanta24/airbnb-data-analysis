import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
import os

os.makedirs("/home/claude/graphs", exist_ok=True)

# ── Colour palette (professional blue theme) ──────────────────────────
BLUES = ["#1F4E79", "#2E75B6", "#4A90C4", "#6AAED6", "#9DCAE1", "#C6DBEF"]
BG    = "#F7FAFC"
GRID  = "#E0EAF4"

def style_ax(ax, title, xlabel, ylabel):
    ax.set_facecolor(BG)
    ax.figure.patch.set_facecolor("white")
    ax.set_title(title, fontsize=14, fontweight="bold", color="#1F4E79", pad=14)
    ax.set_xlabel(xlabel, fontsize=10, color="#444444")
    ax.set_ylabel(ylabel, fontsize=10, color="#444444")
    ax.tick_params(colors="#444444", labelsize=9)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8, linestyle="--")
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)

# ── Sample data (mirrors a real cleaned Airbnb dataset) ───────────────
np.random.seed(42)
n = 800

room_types  = ["Private room", "Entire home/apt", "Shared room", "Hotel room"]
room_weights = [0.42, 0.44, 0.08, 0.06]
neighbourhoods = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
neigh_weights  = [0.35, 0.32, 0.20, 0.09, 0.04]

room_price_means = {"Private room": 95, "Entire home/apt": 195, "Shared room": 55, "Hotel room": 145}
neigh_price_means = {"Manhattan": 210, "Brooklyn": 120, "Queens": 90, "Bronx": 70, "Staten Island": 65}

data = pd.DataFrame({
    "room_type":      np.random.choice(room_types, n, p=room_weights),
    "neighbourhood_group": np.random.choice(neighbourhoods, n, p=neigh_weights),
    "host_identity_verified": np.random.choice(["verified", "unverified"], n, p=[0.63, 0.37]),
    "number_of_reviews": np.random.randint(1, 600, n),
    "NAME": [f"Listing {i}" for i in range(n)],
})

data["price"] = data.apply(
    lambda r: max(20, np.random.normal(room_price_means[r["room_type"]], 30)), axis=1
).round(0)

# ─────────────────────────────────────────────────────────────────────
# GRAPH 1 — Listing count by room type
# ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
counts = data["room_type"].value_counts()
bars = ax.bar(counts.index, counts.values, color=BLUES[:len(counts)], width=0.55, zorder=3)
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 6,
            f"{int(bar.get_height())}", ha="center", va="bottom", fontsize=10, color="#1F4E79", fontweight="bold")
style_ax(ax, "Listing Count by Room Type", "Room Type", "Number of Listings")
plt.tight_layout()
plt.savefig("/home/claude/graphs/graph1_listing_count.png", dpi=150, bbox_inches="tight")
plt.close()
print("Graph 1 done")

# ─────────────────────────────────────────────────────────────────────
# GRAPH 2 — Average price by room type
# ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
avg_price = data.groupby("room_type")["price"].mean().sort_values(ascending=False)
bars = ax.bar(avg_price.index, avg_price.values, color=BLUES[:len(avg_price)], width=0.55, zorder=3)
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f"${bar.get_height():.0f}", ha="center", va="bottom", fontsize=10, color="#1F4E79", fontweight="bold")
style_ax(ax, "Average Price by Room Type (USD)", "Room Type", "Average Price ($)")
plt.tight_layout()
plt.savefig("/home/claude/graphs/graph2_avg_price_room.png", dpi=150, bbox_inches="tight")
plt.close()
print("Graph 2 done")

# ─────────────────────────────────────────────────────────────────────
# GRAPH 3 — Average price by neighbourhood group (horizontal)
# ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
avg_neigh = data.groupby("neighbourhood_group")["price"].mean().sort_values()
bars = ax.barh(avg_neigh.index, avg_neigh.values, color=BLUES[:len(avg_neigh)], height=0.55, zorder=3)
for bar in bars:
    ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
            f"${bar.get_width():.0f}", va="center", fontsize=10, color="#1F4E79", fontweight="bold")
style_ax(ax, "Average Price by Neighbourhood Group (USD)", "Average Price ($)", "Neighbourhood Group")
ax.xaxis.grid(True, color=GRID, linewidth=0.8, linestyle="--")
ax.yaxis.grid(False)
plt.tight_layout()
plt.savefig("/home/claude/graphs/graph3_avg_price_neighbourhood.png", dpi=150, bbox_inches="tight")
plt.close()
print("Graph 3 done")

# ─────────────────────────────────────────────────────────────────────
# GRAPH 4 — Top 10 listings by number of reviews
# ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
top10 = data.nlargest(10, "number_of_reviews")[["NAME", "number_of_reviews"]].reset_index(drop=True)
top10["short_name"] = [f"Listing {i+1}" for i in range(10)]
bars = ax.barh(top10["short_name"][::-1], top10["number_of_reviews"][::-1],
               color=BLUES[1], height=0.6, zorder=3)
for bar in bars:
    ax.text(bar.get_width() + 4, bar.get_y() + bar.get_height()/2,
            f"{int(bar.get_width())}", va="center", fontsize=10, color="#1F4E79", fontweight="bold")
style_ax(ax, "Top 10 Listings by Number of Reviews", "Number of Reviews", "Listing")
ax.xaxis.grid(True, color=GRID, linewidth=0.8, linestyle="--")
ax.yaxis.grid(False)
plt.tight_layout()
plt.savefig("/home/claude/graphs/graph4_top10_reviews.png", dpi=150, bbox_inches="tight")
plt.close()
print("Graph 4 done")

# ─────────────────────────────────────────────────────────────────────
# GRAPH 5 — Verified vs Unverified hosts (donut)
# ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
v_counts = data["host_identity_verified"].value_counts()
colors = [BLUES[0], BLUES[2]]
wedges, texts, autotexts = ax.pie(
    v_counts.values,
    labels=None,
    autopct="%1.1f%%",
    colors=colors,
    startangle=90,
    pctdistance=0.75,
    wedgeprops={"width": 0.55, "edgecolor": "white", "linewidth": 2}
)
for at in autotexts:
    at.set_fontsize(12)
    at.set_fontweight("bold")
    at.set_color("white")
legend_patches = [mpatches.Patch(color=colors[i], label=v_counts.index[i].title()) for i in range(len(v_counts))]
ax.legend(handles=legend_patches, loc="lower center", bbox_to_anchor=(0.5, -0.08),
          ncol=2, fontsize=11, frameon=False)
ax.set_title("Verified vs Unverified Hosts", fontsize=14, fontweight="bold", color="#1F4E79", pad=14)
fig.patch.set_facecolor("white")
plt.tight_layout()
plt.savefig("/home/claude/graphs/graph5_verified_hosts.png", dpi=150, bbox_inches="tight")
plt.close()
print("Graph 5 done")

# ─────────────────────────────────────────────────────────────────────
# GRAPH 6 — Price vs Number of Reviews (scatter)
# ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
room_color_map = {rt: BLUES[i] for i, rt in enumerate(room_types)}
for rt in room_types:
    subset = data[data["room_type"] == rt]
    ax.scatter(subset["price"], subset["number_of_reviews"],
               alpha=0.45, s=30, color=room_color_map[rt], label=rt, zorder=3)
# trend line
z = np.polyfit(data["price"], data["number_of_reviews"], 1)
p = np.poly1d(z)
x_line = np.linspace(data["price"].min(), data["price"].max(), 200)
ax.plot(x_line, p(x_line), color="#C0392B", linewidth=1.8, linestyle="--", label="Trend line")
style_ax(ax, "Price vs Number of Reviews", "Price (USD)", "Number of Reviews")
ax.legend(fontsize=9, frameon=False)
plt.tight_layout()
plt.savefig("/home/claude/graphs/graph6_price_vs_reviews.png", dpi=150, bbox_inches="tight")
plt.close()
print("Graph 6 done")

print("\nAll graphs saved to /home/claude/graphs/")
