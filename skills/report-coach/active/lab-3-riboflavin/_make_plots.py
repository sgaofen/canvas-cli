"""Generate all Lab 3 worksheet figures from Untitled2.cmbl.

All plots are titleless per TA rule (2026-04-18): no plt.title(), no figure
suptitle, no chart title baked in. Captions go in the worksheet as separate
paragraphs in 'Figure N. ...' format.
"""
import gzip
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
CMBL = HERE / "Untitled2.cmbl"

# -----------------------------------------------------------------------------
# Parse the cmbl file (gzipped XML)
# -----------------------------------------------------------------------------
def parse_cmbl(path):
    with gzip.open(path, "rt", encoding="utf-8-sig") as f:
        content = f.read()
    blocks = re.findall(r"<DataSet>(.*?)</DataSet>", content, re.DOTALL)

    def _col(cb):
        vals = []
        for line in cb.strip().split("\n"):
            line = line.strip()
            if line and re.match(r"^-?[\d.]+$", line):
                try:
                    vals.append(float(line))
                except ValueError:
                    pass
        return np.array(vals)

    runs = {}
    for b in blocks:
        name = re.search(r"<DataSetName>([^<]+)</DataSetName>", b).group(1)
        cells = re.findall(r"<ColumnCells>(.*?)</ColumnCells>", b, re.DOTALL)
        col_types = re.findall(r"<DataObjectName>([^<]+)</DataObjectName>", b)
        if len(cells) < 2 or not col_types:
            continue
        wl = _col(cells[0])
        y = _col(cells[1])
        # Some scans (Run 2, 5, 6, 7, 8) have fewer y values than wl; truncate to match.
        n = min(len(wl), len(y))
        runs[name] = {"type": col_types[1], "wl": wl[:n], "y": y[:n]}
    return runs


runs = parse_cmbl(CMBL)

# -----------------------------------------------------------------------------
# Assign physical meaning to each Run. Based on analysis session:
# -----------------------------------------------------------------------------
# Absorbance:
#   Run 1..7 : 2, 4, 6, 8, 10, 12, 20 ppm standards (ascending)
#   Run 8    : unknown multivitamin absorbance
# Fluorescence:
#   Run 9    : 20 ppm std (measured first per manual)
#   Run 10-15: 2, 4, 6, 8, 10, 12 ppm stds (ascending)
#   Run 16   : spurious blank (ignore)
#   Run 17-19: unknown trials 1, 2, 3
#   Run 20-24: SA-0..SA-4 (but we have 5 SA measurements, so 20..23 + Latest)
# Actual Latest is Run 24 = SA-4.

ABS_STDS = {
    2: runs["Run 1"],
    4: runs["Run 2"],
    6: runs["Run 3"],
    8: runs["Run 4"],
    10: runs["Run 5"],
    12: runs["Run 6"],
    20: runs["Run 7"],
}
ABS_UNK = runs["Run 8"]

FL_STDS = {
    2: runs["Run 10"],
    4: runs["Run 11"],
    6: runs["Run 12"],
    8: runs["Run 13"],
    10: runs["Run 14"],
    12: runs["Run 15"],
    20: runs["Run 9"],
}
FL_UNK_TRIALS = [runs["Run 17"], runs["Run 18"], runs["Run 19"]]

# Standard additions — five scans in order SA-0..SA-4
# In the file they are stored as Run 20..23 + (Run 24/Latest)
SA_NAMES = ["Run 20", "Run 21", "Run 22", "Run 23"]
SA_LAST = [k for k in runs if k not in SA_NAMES and k not in {
    "Run 1", "Run 2", "Run 3", "Run 4", "Run 5", "Run 6", "Run 7", "Run 8",
    "Run 9", "Run 10", "Run 11", "Run 12", "Run 13", "Run 14", "Run 15",
    "Run 16", "Run 17", "Run 18", "Run 19"
}]
# Probably "Latest" is SA-4
SA_NAMES.append("Latest")
SA_SCANS = {i: runs[n] for i, n in enumerate(SA_NAMES)}  # i = mL stock added

# -----------------------------------------------------------------------------
# Common matplotlib style: legible fonts, no titles
# -----------------------------------------------------------------------------
plt.rcParams.update({
    "font.size": 12,
    "axes.labelsize": 13,
    "legend.fontsize": 10,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "axes.titlesize": 0,  # ensures any stray title renders at 0
})

OUT = HERE  # write PNGs next to the script


def peak_in(run, lo, hi):
    mask = (run["wl"] >= lo) & (run["wl"] <= hi)
    if not mask.any():
        return None, None
    i = np.argmax(run["y"][mask])
    return run["wl"][mask][i], run["y"][mask][i]


# -----------------------------------------------------------------------------
# Fig 1 — Absorbance overlay: 7 stds + unknown
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
cmap = plt.get_cmap("viridis")
conc_list = sorted(ABS_STDS.keys())
for i, c in enumerate(conc_list):
    r = ABS_STDS[c]
    ax.plot(r["wl"], r["y"], label=f"{c} ppm", color=cmap(i / len(conc_list)), lw=1.1)
ax.plot(ABS_UNK["wl"], ABS_UNK["y"], label="Unknown (multivitamin)",
        color="red", lw=1.5, ls="--")

# λmax indicator at 440.6 nm (unknown's peak, matches literature)
unk_peak_wl, unk_peak_y = peak_in(ABS_UNK, 380, 520)
ax.axvline(unk_peak_wl, color="gray", lw=0.8, ls=":")
ax.annotate(f"λmax = {unk_peak_wl:.1f} nm",
            xy=(unk_peak_wl, unk_peak_y),
            xytext=(unk_peak_wl + 40, unk_peak_y + 0.05),
            fontsize=10, arrowprops=dict(arrowstyle="->", lw=0.7))

ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Absorbance")
ax.set_xlim(380, 700)
ax.grid(alpha=0.3)
ax.legend(loc="upper right", ncol=2, framealpha=0.9)
plt.tight_layout()
plt.savefig(OUT / "fig1_absorbance_overlay.png", dpi=160, bbox_inches="tight")
plt.close()

# -----------------------------------------------------------------------------
# Fig 2 — Fluorescence overlay: 7 stds + 3 unknown trials
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
for i, c in enumerate(conc_list):
    r = FL_STDS[c]
    ax.plot(r["wl"], r["y"], label=f"{c} ppm", color=cmap(i / len(conc_list)), lw=1.1)
for i, r in enumerate(FL_UNK_TRIALS, 1):
    ax.plot(r["wl"], r["y"], label=f"Unknown trial {i}",
            lw=1.5, ls="--", color=["red", "orange", "brown"][i-1])

# λmax: use mean of standards at ~517 nm
std_peak_wl, _ = peak_in(FL_STDS[20], 480, 600)
ax.axvline(std_peak_wl, color="gray", lw=0.8, ls=":")
ax.annotate(f"λmax ≈ {std_peak_wl:.0f} nm",
            xy=(std_peak_wl, 0.18),
            xytext=(std_peak_wl + 35, 0.18),
            fontsize=10, arrowprops=dict(arrowstyle="->", lw=0.7))

ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Fluorescence intensity (405 nm excitation)")
ax.set_xlim(440, 700)
ax.grid(alpha=0.3)
ax.legend(loc="upper right", ncol=2, framealpha=0.9, fontsize=9)
plt.tight_layout()
plt.savefig(OUT / "fig2_fluorescence_overlay.png", dpi=160, bbox_inches="tight")
plt.close()

# -----------------------------------------------------------------------------
# Fig 3 & 4 — Calibration curve (all 7 and linear subset 2–12 ppm)
# -----------------------------------------------------------------------------

def lsq(xs, ys):
    n = len(xs)
    mx, my = xs.mean(), ys.mean()
    m = ((xs - mx) * (ys - my)).sum() / ((xs - mx) ** 2).sum()
    b = my - m * mx
    resid = ys - (m * xs + b)
    ss_res = (resid ** 2).sum()
    ss_tot = ((ys - my) ** 2).sum()
    r2 = 1 - ss_res / ss_tot
    s_yx = np.sqrt(ss_res / (n - 2))
    sxx = ((xs - mx) ** 2).sum()
    s_m = s_yx / np.sqrt(sxx)
    s_b = s_yx * np.sqrt(1 / n + mx ** 2 / sxx)
    t_table = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365}
    t = t_table[n - 2]
    return m, b, r2, t * s_m, t * s_b, s_yx, sxx, mx


# Gather calibration points from the cmbl data (peak intensity in 480–600)
cal_pts = []
for c in sorted(FL_STDS.keys()):
    wl_p, y_p = peak_in(FL_STDS[c], 480, 600)
    cal_pts.append((c, y_p))
cal_pts.sort()
c_arr = np.array([p[0] for p in cal_pts], float)
I_arr = np.array([p[1] for p in cal_pts], float)

# Fit all 7
m7, b7, r2_7, ci_m7, ci_b7, s_yx7, sxx7, mx7 = lsq(c_arr, I_arr)
# Fit 2–12 (exclude 20)
mask = c_arr <= 12
m6, b6, r2_6, ci_m6, ci_b6, s_yx6, sxx6, mx6 = lsq(c_arr[mask], I_arr[mask])

fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(c_arr, I_arr, s=70, color="steelblue", zorder=3)
xfit = np.linspace(0, 22, 200)
ax.plot(xfit, m7 * xfit + b7, color="red", lw=1.3,
        label=f"y = {m7:.5f}x + {b7:+.5f}\nR² = {r2_7:.4f}")
ax.set_xlabel("Riboflavin concentration (ppm)")
ax.set_ylabel("Fluorescence intensity (405 nm excitation)")
ax.grid(alpha=0.3)
ax.legend(loc="upper left", framealpha=0.9)
plt.tight_layout()
plt.savefig(OUT / "fig3_cal_all7.png", dpi=160, bbox_inches="tight")
plt.close()

fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(c_arr[mask], I_arr[mask], s=70, color="steelblue", zorder=3,
           label="Included (2–12 ppm)")
ax.scatter(c_arr[~mask], I_arr[~mask], s=100, facecolors="none",
           edgecolors="red", linewidth=1.8, zorder=3, label="Excluded (20 ppm, inner filter)")
xfit = np.linspace(0, 22, 200)
ax.plot(xfit, m6 * xfit + b6, color="red", lw=1.3,
        label=f"y = {m6:.5f}x + {b6:+.5f}\nR² = {r2_6:.4f}")
ax.set_xlabel("Riboflavin concentration (ppm)")
ax.set_ylabel("Fluorescence intensity (405 nm excitation)")
ax.grid(alpha=0.3)
ax.legend(loc="upper left", framealpha=0.9)
plt.tight_layout()
plt.savefig(OUT / "fig4_cal_linear.png", dpi=160, bbox_inches="tight")
plt.close()

# -----------------------------------------------------------------------------
# Fig 5 — Standard-addition fluorescence spectra overlay
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
cmap2 = plt.get_cmap("plasma")
for V in sorted(SA_SCANS.keys()):
    r = SA_SCANS[V]
    ax.plot(r["wl"], r["y"], label=f"SA-{V} ({V} mL stock)",
            color=cmap2(V / 4), lw=1.2)

sa_peak_wl, _ = peak_in(SA_SCANS[4], 480, 600)
ax.axvline(sa_peak_wl, color="gray", lw=0.8, ls=":")
ax.annotate(f"λmax ≈ {sa_peak_wl:.0f} nm",
            xy=(sa_peak_wl, 0.10),
            xytext=(sa_peak_wl + 30, 0.10),
            fontsize=10, arrowprops=dict(arrowstyle="->", lw=0.7))

ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Fluorescence intensity (405 nm excitation)")
ax.set_xlim(440, 700)
ax.grid(alpha=0.3)
ax.legend(loc="upper right", framealpha=0.9)
plt.tight_layout()
plt.savefig(OUT / "fig5_sa_spectra.png", dpi=160, bbox_inches="tight")
plt.close()

# -----------------------------------------------------------------------------
# Fig 6 — Standard-addition linear curve
# -----------------------------------------------------------------------------
sa_pts = []
for V in sorted(SA_SCANS.keys()):
    _, y_p = peak_in(SA_SCANS[V], 480, 600)
    sa_pts.append((V, y_p))
V_arr = np.array([p[0] for p in sa_pts], float)
I_sa = np.array([p[1] for p in sa_pts], float)

mSA, bSA, r2_SA, ci_mSA, ci_bSA, s_yx_SA, sxx_SA, mx_SA = lsq(V_arr, I_sa)
x_int_SA = -bSA / mSA

fig, ax = plt.subplots(figsize=(7, 5))
ax.axhline(0, color="k", lw=0.4)
ax.axvline(0, color="k", lw=0.4)
ax.scatter(V_arr, I_sa, s=80, color="steelblue", zorder=3)
xfit = np.linspace(x_int_SA - 0.3, 4.5, 200)
ax.plot(xfit, mSA * xfit + bSA, color="red", lw=1.3,
        label=f"y = {mSA:.5f}x + {bSA:+.5f}\nR² = {r2_SA:.4f}")
ax.scatter([x_int_SA], [0], marker="x", s=120, color="purple", zorder=4,
           label=f"x-intercept = {x_int_SA:.3f} mL")
for V, I in zip(V_arr, I_sa):
    ax.annotate(f"SA-{int(V)}", (V, I), textcoords="offset points",
                xytext=(7, -4), fontsize=9)
ax.set_xlabel("Volume of 50.0 ppm riboflavin stock added (mL)")
ax.set_ylabel("Fluorescence intensity (405 nm excitation)")
ax.grid(alpha=0.3)
ax.legend(loc="upper left", framealpha=0.9)
plt.tight_layout()
plt.savefig(OUT / "fig6_sa_linear.png", dpi=160, bbox_inches="tight")
plt.close()

# -----------------------------------------------------------------------------
# Summary print: numbers the worksheet will need
# -----------------------------------------------------------------------------
print("== Calibration (ALL 7) ==")
print(f"  m = {m7:.6f}, b = {b7:+.6f}, R2 = {r2_7:.4f}")
print(f"  95% CI m = ±{ci_m7:.5f}, CI b = ±{ci_b7:.5f}")
print("\n== Calibration (2-12 ppm, linear) ==")
print(f"  m = {m6:.6f}, b = {b6:+.6f}, R2 = {r2_6:.4f}")
print(f"  95% CI m = ±{ci_m6:.5f}, CI b = ±{ci_b6:.5f}")
print(f"  s_yx = {s_yx6:.5f}, Sxx = {sxx6:.3f}, x_bar = {mx6:.3f}, n={mask.sum()}")
print("\n== Unknown (3 trials) ==")
I_unk = np.array([r["y"][(r["wl"] >= 480) & (r["wl"] <= 600)].max()
                  for r in FL_UNK_TRIALS])
print(f"  I peaks: {I_unk}")
print(f"  mean = {I_unk.mean():.6f}, std = {I_unk.std(ddof=1):.6f}")
# Conc from calibration
c_unk_cuv = (I_unk.mean() - b6) / m6
print(f"  c_cuvette from cal = {c_unk_cuv:.4f} ppm")
print(f"  c_A3 from cal (no dilution) = {c_unk_cuv:.4f} ppm")

print("\n== Standard addition ==")
print(f"  m = {mSA:.6f}, b = {bSA:+.6f}, R2 = {r2_SA:.4f}")
print(f"  95% CI m = ±{ci_mSA:.5f}, CI b = ±{ci_bSA:.5f}")
print(f"  x-intercept = {x_int_SA:.4f} mL")
c_unk_A3_SA = 50.0 * abs(x_int_SA) / 5.0
print(f"  c_A3 from SA = {c_unk_A3_SA:.4f} ppm")

# SA excluding SA-3 for comparison
mask_SA = np.array([True, True, True, False, True])
mSA2, bSA2, r2_SA2, ci_mSA2, ci_bSA2, s_yx_SA2, sxx_SA2, mx_SA2 = lsq(V_arr[mask_SA], I_sa[mask_SA])
x_int_SA2 = -bSA2 / mSA2
c_unk_A3_SA2 = 50.0 * abs(x_int_SA2) / 5.0
print("\n== Standard addition (excl SA-3) ==")
print(f"  m = {mSA2:.6f}, b = {bSA2:+.6f}, R2 = {r2_SA2:.4f}")
print(f"  95% CI m = ±{ci_mSA2:.5f}, CI b = ±{ci_bSA2:.5f}")
print(f"  x-intercept = {x_int_SA2:.4f} mL")
print(f"  c_A3 from SA (excl) = {c_unk_A3_SA2:.4f} ppm")

# Unknown concentration CI from calibration (Miller+Miller formula)
# s_c = (s_yx / m) * sqrt(1/N + 1/n + (y0 - ybar)^2 / (m^2 * Sxx))
N_rep = 3
n_cal = mask.sum()
y0 = I_unk.mean()
y_bar = (m6 * c_arr[mask]).mean() + b6  # = mean of fitted y, but use actual mean
y_bar = I_arr[mask].mean()
s_c = (s_yx6 / m6) * np.sqrt(1/N_rep + 1/n_cal + (y0 - y_bar)**2 / (m6**2 * sxx6))
# t-multiplier for n_cal-2 dof
t_map = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447}
t_cal = t_map[n_cal - 2]
ci_c = t_cal * s_c
print(f"\n  Unknown conc 95% CI (calibration): ±{ci_c:.4f} ppm → {c_unk_cuv:.3f} ± {ci_c:.3f}")

# SA x-intercept CI (Miller formula with y0 = 0)
s_x0 = (s_yx_SA / mSA) * np.sqrt(1/len(V_arr) + (0 - I_sa.mean())**2 / (mSA**2 * sxx_SA))
t_sa = t_map[len(V_arr) - 2]
ci_x0 = t_sa * s_x0
print(f"  SA x-intercept 95% CI (all 5): ±{ci_x0:.4f} mL")
# Propagate to c_A3: c_A3 = |x_int|*50/5 = |x_int|*10
ci_c_SA = ci_x0 * 50 / 5
print(f"  SA unknown conc 95% CI (all 5): {c_unk_A3_SA:.3f} ± {ci_c_SA:.3f} ppm")

s_x0_2 = (s_yx_SA2 / mSA2) * np.sqrt(1/mask_SA.sum() + (0 - I_sa[mask_SA].mean())**2 / (mSA2**2 * sxx_SA2))
t_sa2 = t_map[mask_SA.sum() - 2]
ci_x0_2 = t_sa2 * s_x0_2
ci_c_SA2 = ci_x0_2 * 50 / 5
print(f"  SA x-intercept 95% CI (excl SA-3): ±{ci_x0_2:.4f} mL")
print(f"  SA unknown conc 95% CI (excl SA-3): {c_unk_A3_SA2:.3f} ± {ci_c_SA2:.3f} ppm")

print("\n[All figures written to:", OUT, "]")
