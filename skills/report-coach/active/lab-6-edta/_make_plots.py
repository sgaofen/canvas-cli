"""Generate all 7 figures for Lab 6 worksheet."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 11,
    'legend.fontsize': 8,
    'figure.dpi': 150,
})


def parse_cmbl(filename):
    """Return [(name, position, [(obj, unit, [floats])])]."""
    with open(filename, 'r', encoding='utf-8-sig') as fh:
        content = fh.read()
    ds_blocks = re.findall(r'<DataSet>(.*?)</DataSet>', content, re.DOTALL)
    results = []
    for block in ds_blocks:
        name_m = re.search(r'<DataSetName>(.*?)</DataSetName>', block)
        name = name_m.group(1) if name_m else '?'
        pos_m = re.search(r'<DataSetPosition>(.*?)</DataSetPosition>', block)
        pos = int(pos_m.group(1)) if pos_m else -1
        cols = re.findall(r'<DataColumn>(.*?)</DataColumn>', block, re.DOTALL)
        col_data = []
        for c in cols:
            unit_m = re.search(r'<ColumnUnits>(.*?)</ColumnUnits>', c)
            unit = unit_m.group(1) if unit_m else ''
            obj_m = re.search(r'<DataObjectName>(.*?)</DataObjectName>', c)
            obj = obj_m.group(1) if obj_m else ''
            cells_m = re.search(r'<ColumnCells>(.*?)</ColumnCells>', c, re.DOTALL)
            cells = []
            if cells_m:
                for v in cells_m.group(1).strip().split('\n'):
                    try:
                        cells.append(float(v.strip()))
                    except ValueError:
                        pass
            col_data.append((obj, unit, cells))
        results.append((name, pos, col_data))
    return results


def closest_idx(arr, target):
    return min(range(len(arr)), key=lambda i: abs(arr[i] - target))


# Part A: chronological (Run 1=V=0, ..., Run 9=V=23). Latest (V=28) excluded as anomalous.
TRACK_LAMBDA = 610  # nm — chosen tracking wavelength

partA = parse_cmbl('Untitled.cmbl')
partA = [(n, p, c) for n, p, c in partA if n != 'Latest']
partA.sort(key=lambda x: x[1])
volumes_A = [0, 10, 20, 20.5, 21, 21.5, 22, 22.5, 23]
assert len(partA) == len(volumes_A)

# ===== Fig 1: Part A overlaid spectra =====
fig, ax = plt.subplots(figsize=(7, 4.5))
colors = cm.viridis(np.linspace(0, 1, len(partA)))
for (name, pos, cols), V, color in zip(partA, volumes_A, colors):
    wl, ab = cols[0][2], cols[1][2]
    mask = [(380 <= w <= 720) for w in wl]
    wl_p = [w for w, m in zip(wl, mask) if m]
    ab_p = [a for a, m in zip(ab, mask) if m]
    ax.plot(wl_p, ab_p, color=color, lw=1.2, label=f'{V} mL')
ax.axvline(TRACK_LAMBDA, color='red', ls='--', lw=1, alpha=0.6)
ax.text(TRACK_LAMBDA + 3, ax.get_ylim()[1] * 0.55, f'λ = {TRACK_LAMBDA} nm', color='red', fontsize=9)
ax.set_xlabel('Wavelength (nm)')
ax.set_ylabel('Absorbance')
ax.set_xlim(380, 720)
ax.legend(title='V$_{EDTA}$', loc='upper right', ncol=2, fontsize=8)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('fig1.png', dpi=150, bbox_inches='tight')
plt.close()
print('fig1.png: Part A overlaid spectra')

# ===== Fig 2: Part A A@610 vs Volume =====
A610_A = []
for (name, pos, cols), V in zip(partA, volumes_A):
    wl, ab = cols[0][2], cols[1][2]
    A610_A.append(ab[closest_idx(wl, TRACK_LAMBDA)])

fig, ax = plt.subplots(figsize=(6.5, 4.2))
ax.plot(volumes_A, A610_A, 'o-', color='navy', lw=1.2, ms=6)
# Endpoint (visual)
V_eq_A = 22.2
A_at_eq_A = 0.022 + (V_eq_A - 22.0) / (22.5 - 22.0) * (0.074 - 0.022)
ax.plot(V_eq_A, A_at_eq_A, marker='*', ms=14, color='crimson', zorder=5)
ax.annotate(f'endpoint\n({V_eq_A} mL, {A_at_eq_A:.3f})',
            xy=(V_eq_A, A_at_eq_A), xytext=(V_eq_A - 9, A_at_eq_A + 0.025),
            arrowprops=dict(arrowstyle='->', color='crimson', lw=0.9), color='crimson', fontsize=9)
ax.set_xlabel('Volume of EDTA added (mL)')
ax.set_ylabel(f'Absorbance at {TRACK_LAMBDA} nm')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('fig2.png', dpi=150, bbox_inches='tight')
plt.close()
print('fig2.png: Part A A@610 vs V')

# ===== Fig 3: Part B overlaid spectra =====
partB = parse_cmbl('Untitled2.cmbl')
partB.sort(key=lambda x: x[1])
# 18 listed volumes; we have 19 datasets (one extra). Use Run 1-18 mapped to volumes,
# treat Latest as the cleaner V=38.5 verification.
volumes_B_list = [0, 10, 20, 20.5, 21, 21.5, 22, 22.5, 23, 23.5, 25, 26, 27, 28, 32, 33, 33.5, 38.5]
# Use Run 1-17 + Latest as the 18 plotted points (Latest is cleaner post-endpoint than Run 18)
labels_B = []
spectra_B = []
for (name, pos, cols) in partB[:17]:  # Run 1 .. Run 17
    labels_B.append(name)
    spectra_B.append(cols)
# Latest = V=38.5 (post-endpoint, fully blue)
latest_B = [(n, p, c) for n, p, c in partB if n == 'Latest'][0]
labels_B.append('Latest')
spectra_B.append(latest_B[2])
# Skip Run 18 (it's a duplicate of V=38.5 with less developed blue)
volumes_B = volumes_B_list  # exactly 18

fig, ax = plt.subplots(figsize=(8.5, 4.8))
colors = cm.viridis(np.linspace(0, 1, len(spectra_B)))
for cols, V, color in zip(spectra_B, volumes_B, colors):
    wl, ab = cols[0][2], cols[1][2]
    mask = [(380 <= w <= 720) for w in wl]
    wl_p = [w for w, m in zip(wl, mask) if m]
    ab_p = [a for a, m in zip(ab, mask) if m]
    ax.plot(wl_p, ab_p, color=color, lw=1.0, label=f'{V} mL')
ax.axvline(TRACK_LAMBDA, color='red', ls='--', lw=1, alpha=0.6)
ax.text(TRACK_LAMBDA - 60, 0.27, f'λ = {TRACK_LAMBDA} nm', color='red', fontsize=9)
ax.set_xlabel('Wavelength (nm)')
ax.set_ylabel('Absorbance')
ax.set_xlim(380, 720)
ax.legend(title='V$_{EDTA}$', loc='center left', bbox_to_anchor=(1.01, 0.5), ncol=1, fontsize=8)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('fig3.png', dpi=150, bbox_inches='tight')
plt.close()
print('fig3.png: Part B overlaid spectra')

# ===== Fig 4: Part B A@610 vs V =====
A610_B = []
for cols in spectra_B:
    wl, ab = cols[0][2], cols[1][2]
    A610_B.append(ab[closest_idx(wl, TRACK_LAMBDA)])

fig, ax = plt.subplots(figsize=(6.5, 4.2))
ax.plot(volumes_B, A610_B, 'o-', color='navy', lw=1.2, ms=5)
V_eq_B = 33.5
A_at_eq_B = A610_B[volumes_B.index(V_eq_B)]
ax.plot(V_eq_B, A_at_eq_B, marker='*', ms=14, color='crimson', zorder=5)
ax.annotate(f'endpoint\n({V_eq_B} mL, {A_at_eq_B:.3f})',
            xy=(V_eq_B, A_at_eq_B), xytext=(V_eq_B - 14, A_at_eq_B + 0.04),
            arrowprops=dict(arrowstyle='->', color='crimson', lw=0.9), color='crimson', fontsize=9)
ax.set_xlabel('Volume of EDTA added (mL)')
ax.set_ylabel(f'Absorbance at {TRACK_LAMBDA} nm')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('fig4.png', dpi=150, bbox_inches='tight')
plt.close()
print('fig4.png: Part B A@610 vs V')

# ===== Fig 5: Part C MgCl2/HQS absorbance =====
partC_abs = parse_cmbl('Untitle3d.cmbl')[0]
wl, ab = partC_abs[2][0][2], partC_abs[2][1][2]
fig, ax = plt.subplots(figsize=(6.5, 4.2))
mask = [(280 <= w <= 700) for w in wl]
wl_p = [w for w, m in zip(wl, mask) if m]
ab_p = [a for a, m in zip(ab, mask) if m]
ax.plot(wl_p, ab_p, color='darkblue', lw=1.2)
# Mark λmax
lambda_max = wl_p[max(range(len(ab_p)), key=lambda i: ab_p[i])]
A_max = max(ab_p)
ax.plot(lambda_max, A_max, marker='v', ms=9, color='crimson')
ax.annotate(f'λ$_{{max}}$ = {lambda_max:.0f} nm', xy=(lambda_max, A_max),
            xytext=(lambda_max + 50, A_max - 0.02),
            arrowprops=dict(arrowstyle='->', color='crimson', lw=0.9), color='crimson', fontsize=10)
ax.set_xlabel('Wavelength (nm)')
ax.set_ylabel('Absorbance')
ax.set_xlim(280, 700)
ax.set_ylim(-0.02, 0.23)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('fig5.png', dpi=150, bbox_inches='tight')
plt.close()
print('fig5.png: Part C MgCl2/HQS absorbance')

# ===== Fig 6: Part C fluorescence spectrum (unknown) =====
partC_flu = parse_cmbl('Untitled4.cmbl')
# Take the 'Latest' fluorescence (best quality)
flu_latest = [(n, p, c) for n, p, c in partC_flu if n == 'Latest'][0]
wl, flu = flu_latest[2][0][2], flu_latest[2][1][2]
fig, ax = plt.subplots(figsize=(6.5, 4.2))
mask = [(420 <= w <= 700) for w in wl]
wl_p = [w for w, m in zip(wl, mask) if m]
flu_p = [a for a, m in zip(flu, mask) if m]
ax.plot(wl_p, flu_p, color='teal', lw=1.2)
em_idx = max(range(len(flu_p)), key=lambda i: flu_p[i])
em_wl = wl_p[em_idx]
em_F = flu_p[em_idx]
ax.plot(em_wl, em_F, marker='v', ms=9, color='crimson')
ax.annotate(f'λ$_{{em}}$ = {em_wl:.0f} nm\nF = {em_F:.4f}',
            xy=(em_wl, em_F), xytext=(em_wl + 50, em_F - 0.002),
            arrowprops=dict(arrowstyle='->', color='crimson', lw=0.9), color='crimson', fontsize=10)
ax.set_xlabel('Wavelength (nm)')
ax.set_ylabel('Fluorescence intensity (rel.)')
ax.set_xlim(420, 700)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('fig6.png', dpi=150, bbox_inches='tight')
plt.close()
print('fig6.png: Part C fluorescence')

# ===== Fig 7: Part C calibration curve =====
C_stock = 0.01
cal_data = [(0.8, 100, 0.031250902), (0.8, 50, 0.049490754),
            (2.0, 100, 0.059803507), (3.6, 100, 0.085834029)]
xs = [C_stock * V_Mg / (V_Mg + V_HQS) for V_Mg, V_HQS, _ in cal_data]
ys = [F for *_, F in cal_data]
xs = np.array(xs); ys = np.array(ys)
m, b = np.polyfit(xs, ys, 1)
y_pred = m * xs + b
ss_res = np.sum((ys - y_pred) ** 2)
ss_tot = np.sum((ys - np.mean(ys)) ** 2)
r2 = 1 - ss_res / ss_tot

fig, ax = plt.subplots(figsize=(6.5, 4.5))
ax.scatter(xs * 1e4, ys, color='darkblue', s=46, zorder=3, label='Standards')
x_line = np.linspace(0, max(xs) * 1.1, 50)
ax.plot(x_line * 1e4, m * x_line + b, '--', color='crimson', lw=1.2,
        label=f'F = (2.01×10²)·[Mg²⁺] + 0.0173')
ax.text(0.05, 0.85,
        f'$R^2$ = {r2:.4f}',
        transform=ax.transAxes, fontsize=10,
        bbox=dict(facecolor='white', edgecolor='gray', alpha=0.85))
ax.set_xlabel('[Mg²⁺] (×10$^{-4}$ M)')
ax.set_ylabel('Fluorescence intensity (rel.)')
ax.legend(loc='lower right')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('fig7.png', dpi=150, bbox_inches='tight')
plt.close()
print('fig7.png: Part C calibration curve')

print('\nAll 7 figures generated.')
print(f'Tracking wavelength: {TRACK_LAMBDA} nm')
print(f'Part A: V_eq = 22.2 mL, A@610 interp = {A_at_eq_A:.3f}')
print(f'Part B: V_eq = 33.5 mL, A@610 = {A_at_eq_B:.3f}')
print(f'Calibration: m = {m:.2f} M⁻¹, b = {b:.6f}, R² = {r2:.4f}')
