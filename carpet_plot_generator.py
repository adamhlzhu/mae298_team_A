import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load your data
df = pd.read_csv("mission_sweep_results.csv")

# From bwb_mach_opt.py 
FB_star   = 2968.229605246772
FT_star   = 3167.1701888693296
ALT_star  = 39999.88009889918
MACH_star = 0.7400069283717394

# Extract columns
FB = df["fuel_burn_lb"]
FT = df["flight_time_s"]
ALT = df["cruise_alt_ft"]
MACH = df["cruise_mach"]

plt.figure(figsize=(10, 8))

# ---- Constant Cruise Altitude Lines ----
unique_alts = sorted(df["cruise_alt_ft"].unique())
for alt in unique_alts:
    subset = df[df["cruise_alt_ft"] == alt]
    plt.plot(subset["fuel_burn_lb"], subset["flight_time_s"], "-o", label=f"Alt={alt:.0f} ft")

# ---- Constant Mach Lines ----
unique_mach = sorted(df["cruise_mach"].unique())
for mach in unique_mach:
    subset = df[df["cruise_mach"] == mach]
    plt.plot(subset["fuel_burn_lb"], subset["flight_time_s"], "--o", label=f"Mach={mach:.2f}")

plt.xlabel("Fuel Burn [lbm]")
plt.ylabel("Flight Time [s]")
plt.title("Carpet Plot of Mission Trajectory Results")

# Avoid duplicate labels
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys(), fontsize=9, loc="best")

# plt.plot(FB_star, FT_star, marker="*", markersize=18, color="red", label="Optimized Trajectory")
# plt.legend()

plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("mission_carpet.png")
plt.show()


# Pivot into a 2D grid:
# rows = Mach, columns = Altitude, values = Fuel Burn
pivot = df.pivot_table(
    index="cruise_mach",
    columns="cruise_alt_ft",
    values="fuel_burn_lb",
    aggfunc="mean"     # in case duplicates exist
)


plt.figure(figsize=(10, 8))
im = plt.imshow(pivot, aspect="auto", origin="lower", cmap="viridis_r")

# Label ticks using actual alt & mach values
plt.xticks(
    ticks=np.arange(len(pivot.columns)),
    labels=[f"{int(a)}" for a in pivot.columns]
)
plt.yticks(
    ticks=np.arange(len(pivot.index)),
    labels=[f"{m:.2f}" for m in pivot.index]
)

plt.xlabel("Cruise Altitude [ft]")
plt.ylabel("Cruise Mach Number")
plt.title("Fuel Burn Heat Map")

cbar = plt.colorbar(im)
cbar.set_label("Fuel Burn [lb]")

plt.tight_layout()
plt.savefig("mission_fuel_heatmap.png")
plt.show()
