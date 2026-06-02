"""Generate Lab 5 figures with no in-image titles. Captions live in the worksheet text."""
import numpy as np
import matplotlib.pyplot as plt
import re

# ---------- Part A: teacher-provided data ----------
V_A = np.array([2,4,6,8,10,12,14,16,18,20])
Ag_A = np.array([0.00196078431372549, 0.003846153846153846, 0.005660377358490566,
                 0.007407407407407407, 0.00909090909090909, 0.010714285714285714,
                 0.012280701754385967, 0.013793103448275862, 0.015254237288135592,
                 0.016666666666666666])
logInvAg = np.log10(1.0 / Ag_A)
E_A = np.array([0.38512, 0.38956, 0.39348, 0.39734, 0.40194,
                0.40626, 0.41178, 0.41651, 0.41902, 0.4244])

slope, intercept = np.polyfit(logInvAg, E_A, 1)
yfit = slope*logInvAg + intercept
resid = E_A - yfit
ss_res = float(np.sum(resid**2))
ss_tot = float(np.sum((E_A - np.mean(E_A))**2))
R2 = 1 - ss_res/ss_tot

fig, ax = plt.subplots(figsize=(6.0, 4.4))
ax.scatter(logInvAg, E_A, s=42, color="#1f4e79", zorder=3, label="Measured")
xline = np.linspace(logInvAg.min(), logInvAg.max(), 100)
ax.plot(xline, slope*xline + intercept, color="#c00000", lw=1.4,
        label=f"y = {slope:.4f} x + {intercept:.3f}\n$R^2$ = {R2:.3f}")
ax.set_xlabel(r"$\log\!\left(1/[\mathrm{Ag^+}]\right)$")
ax.set_ylabel(r"$E_\mathrm{cell}$ (V)")
ax.legend(loc="upper right", frameon=False, fontsize=10)
ax.grid(True, alpha=0.25)
fig.tight_layout()
fig.savefig("fig1_partA_nernst.png", dpi=180, bbox_inches="tight")
plt.close(fig)
print(f"fig1: slope={slope:.6f}, intercept={intercept:.6f}, R2={R2:.4f}")

# ---------- Part B: my Careful titration ----------
V_B = np.array([0,5,10,15,20,20.5,21,22,22.5,23,23.5,24,24.5,25,25.5,26,26.5,27,27.5,28,28.5,29,29.5,30])
E_B = np.array([0.136,0.149,0.160,0.172,0.190,0.193,0.197,0.203,0.209,0.215,0.221,0.233,0.253,0.254,0.287,0.319,0.327,0.338,0.347,0.350,0.354,0.356,0.358,0.362])

def central_deriv(V, E):
    """Central difference for non-uniform spacing; endpoints use forward/backward."""
    d = np.empty_like(V, dtype=float)
    d[0] = (E[1]-E[0]) / (V[1]-V[0])
    d[-1] = (E[-1]-E[-2]) / (V[-1]-V[-2])
    for i in range(1, len(V)-1):
        d[i] = (E[i+1]-E[i-1]) / (V[i+1]-V[i-1])
    return d

dB = central_deriv(V_B, E_B) * 1000  # mV/mL
i_eq_B = int(np.argmax(dB))
V_eq_B, E_eq_B = float(V_B[i_eq_B]), float(E_B[i_eq_B])
print(f"Part B: V_eq={V_eq_B} mL, E_eq={E_eq_B:.3f} V (discrete max central deriv = {dB[i_eq_B]:.0f} mV/mL)")

fig, ax1 = plt.subplots(figsize=(6.4, 4.4))
ax1.plot(V_B, E_B, "o-", color="#1f4e79", ms=4.5, lw=1.2, label=r"$E_\mathrm{cell}$")
ax1.set_xlabel(r"$V_{\mathrm{AgNO_3}}$ added (mL)")
ax1.set_ylabel(r"$E_\mathrm{cell}$ (V)", color="#1f4e79")
ax1.tick_params(axis="y", labelcolor="#1f4e79")
ax1.scatter([V_eq_B], [E_eq_B], s=110, marker="o", facecolor="none",
            edgecolor="#7030a0", lw=1.8, zorder=5)
ax1.annotate(f"({V_eq_B:.1f} mL, {E_eq_B:.3f} V)",
             xy=(V_eq_B, E_eq_B), xytext=(V_eq_B-9, E_eq_B+0.01),
             fontsize=9, color="#7030a0")

ax2 = ax1.twinx()
ax2.plot(V_B, dB, "s-", color="#c00000", ms=3.5, lw=1.0, alpha=0.7, label=r"$dE_\mathrm{cell}/dV$")
ax2.set_ylabel(r"$dE_\mathrm{cell}/dV$ (mV/mL)", color="#c00000")
ax2.tick_params(axis="y", labelcolor="#c00000")

# combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1+lines2, labels1+labels2, loc="upper left", frameon=False, fontsize=10)
ax1.grid(True, alpha=0.2)
fig.tight_layout()
fig.savefig("fig2_partB_titration.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# ---------- Part C: my Careful titration (unknown) ----------
V_C = np.array([0,5,10,15,20,25,30,30.5,31,31.5,32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40])
E_C = np.array([0.112,0.122,0.129,0.137,0.148,0.161,0.183,0.191,0.197,0.191,0.253,0.211,0.262,0.276,0.300,0.298,0.296,0.301,0.309,0.320,0.326,0.331,0.333,0.337,0.339,0.343,0.344])

dC = central_deriv(V_C, E_C) * 1000
i_eq_C = int(np.argmax(dC))
V_eq_C, E_eq_C = float(V_C[i_eq_C]), float(E_C[i_eq_C])
print(f"Part C: V_eq={V_eq_C} mL, E_eq={E_eq_C:.3f} V (discrete max central deriv = {dC[i_eq_C]:.0f} mV/mL)")

fig, ax1 = plt.subplots(figsize=(6.4, 4.4))
ax1.plot(V_C, E_C, "o-", color="#1f4e79", ms=4.5, lw=1.2, label=r"$E_\mathrm{cell}$")
ax1.set_xlabel(r"$V_{\mathrm{AgNO_3}}$ added (mL)")
ax1.set_ylabel(r"$E_\mathrm{cell}$ (V)", color="#1f4e79")
ax1.tick_params(axis="y", labelcolor="#1f4e79")
ax1.scatter([V_eq_C], [E_eq_C], s=110, marker="o", facecolor="none",
            edgecolor="#7030a0", lw=1.8, zorder=5)
ax1.annotate(f"({V_eq_C:.1f} mL, {E_eq_C:.3f} V)",
             xy=(V_eq_C, E_eq_C), xytext=(V_eq_C-12, E_eq_C+0.01),
             fontsize=9, color="#7030a0")

ax2 = ax1.twinx()
ax2.plot(V_C, dC, "s-", color="#c00000", ms=3.5, lw=1.0, alpha=0.7, label=r"$dE_\mathrm{cell}/dV$")
ax2.set_ylabel(r"$dE_\mathrm{cell}/dV$ (mV/mL)", color="#c00000")
ax2.tick_params(axis="y", labelcolor="#c00000")

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1+lines2, labels1+labels2, loc="upper left", frameon=False, fontsize=10)
ax1.grid(True, alpha=0.2)
fig.tight_layout()
fig.savefig("fig3_partC_titration.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print("Plots saved: fig1_partA_nernst.png, fig2_partB_titration.png, fig3_partC_titration.png")
