# Lab 3 — 真实实验数据记录

> 实验日期：2026-04-17
> 这份文档是**所有真实测出来的数据**，写 worksheet 直接从这里抄。
> 数据来源：`Untitled1.cmbl`（Logger Pro 存档）

---

## 📌 关键约定（绝对不能忘）

- **我们只配了 7 个浓度**（不是 manual 默认的 9 个，没有 blank，没有单独 1/14 ppm）
- **浓度 ↔ 取 50 ppm stock 体积映射**：

| 加入 stock 体积 | 实际浓度 |
|---|---|
| 1 mL | 2 ppm |
| 2 mL | 4 ppm |
| 3 mL | 6 ppm |
| 4 mL | 8 ppm |
| 5 mL | 10 ppm |
| 6 mL | 12 ppm |
| 10 mL | 20 ppm |

- 激发波长：**405 nm**（根据 Part B 的吸光数据选定）

---

## Part A — 溶液配制（待补真实数据）

- [ ] ⭐ 实际称取 riboflavin 质量 = ______ mg（用于算 stock 真实浓度，待补）
- [ ] ⭐ 实际 50 ppm stock 浓度 = ______ ppm（待补）
- [ ] ⭐ 实际称取 multivitamin 粉末质量 m_vitamin = ______ mg（待补，建议用 50.0 mg 占位）
- [ ] ⭐ 一片 tablet 质量 = ______ mg  **← 忘记记了，模拟假设 500 mg**
- [ ] ⭐ Label 上每片 riboflavin 含量 = ______ mg  **← 忘记记了，模拟假设 25 mg**
- [ ] Multivitamin 牌子 = ______（未知）

> ⚠️ **IMPORTANT**: 课上老师给的 tablet 信息未记录。建议问 TA 或同组补上真实值。
> 目前用"典型 high-potency B-complex" 做模拟：tablet 500 mg / riboflavin 25 mg → 理论 mass% = 5.00%

---

## Part B — 吸光谱数据

### B.1 Standards（Run 1–7，`Untitled1.cmbl`）

| Run | 浓度 (ppm) | λmax (nm) | A(λmax) | A(405) | A(445) | A(500) |
|---|---|---|---|---|---|---|
| Run 1 | 2  | 440.6 | 0.0688 | 0.0409 | 0.0686 | 0.0145 |
| Run 2 | 4  | 444.9 | 0.1300 | 0.0888 | 0.1300 | 0.0288 |
| Run 3 | 6  | 444.0 | 0.1984 | 0.1340 | 0.1983 | 0.0347 |
| Run 4 | 8  | 442.3 | 0.2681 | 0.1750 | 0.2679 | 0.0537 |
| Run 5 | 10 | 440.6 | 0.3211 | 0.2282 | 0.3186 | 0.0496 |
| Run 6 | 12 | 441.4 | 0.3703 | 0.2558 | 0.3690 | 0.0573 |
| Run 7 | 20 | 440.6 | **0.5748** | **0.4132** | 0.5677 | **0.0576** |

### B.2 Unknown（Run 8）

| | 值 |
|---|---|
| λmax | **440.6 nm** |
| A(λmax) | 0.2564 |
| A(405) | 0.1919 |
| A(500) | 0.0453 |
| Baseline (700–900 nm) | +0.0004（基线干净）|

### B.3 Worksheet Q2 答案

**选 405 nm 作为荧光激发波长。** 理由：在最高浓度 20 ppm 时 A(405) = 0.4132 而 A(500) = 0.0576，**405 nm 处吸光是 500 nm 处的 7.2 倍**，激发效率更高、fluorescence 信号更强。

### B.4 吸光 Beer's Law 线性性（参考用）

- A(405) vs c：slope = 0.02059，R² = 0.996 ✓
- A(λmax) vs c：slope = 0.02809，R² = 0.994 ✓

---

## Part C — 荧光数据（Run 9–14 + Latest，激发 405 nm）

### C.1 Standards Peak Fluorescence

| Run | 浓度 (ppm) | λmax_em (nm) | I_peak | I(520) | I(530) |
|---|---|---|---|---|---|
| Run 10 | 2  | 516.6 | 0.0291 | 0.0288 | 0.0266 |
| Run 11 | 4  | 514.2 | 0.0433 | 0.0418 | 0.0364 |
| Run 12 | 6  | 518.2 | 0.0683 | 0.0668 | 0.0550 |
| Run 13 | 8  | 517.4 | 0.0924 | 0.0910 | 0.0725 |
| Run 14 | 10 | 516.6 | 0.1166 | 0.1140 | 0.0904 |
| Latest | 12 | 518.2 | 0.1438 | 0.1428 | 0.1139 |
| Run 9  | 20 | 517.4 | **0.2031** | 0.2017 | 0.1631 |

**测量顺序**：Run 9 (20 ppm) 最先测，之后是 Run 10→14 + Latest（2→12 ppm 递增）。
**发射峰 λmax_em ≈ 517 nm**，和文献 riboflavin 发射峰 ~520 nm 吻合 ✓。

### C.2 线性回归与 inner filter effect

**全部 7 个点拟合**：
- slope = 0.01007 ± 0.00142 (95% CI)
- intercept = +0.01030 ± 0.01486
- R² = 0.9851

**只用 2–12 ppm（剔除 20 ppm，因为 inner filter）**：
- slope = **0.01168 ± 0.00129** (95% CI)
- intercept = **+0.00050 ± 0.01007**
- R² = **0.9937** ✓

### C.3 Worksheet Q4a/b 的答案已就绪

**Q4a**：画 7 个点的 calibration → 见 `plot_calibration_all7.png`。
**Q4b 关键证据**：20 ppm 实测 I = 0.2031，但从 2–12 线性外推应为 0.2341 → **偏低 13.2%，明显平台化 → inner filter effect confirmed**。
**Q4b 剔除 20 ppm 后的 calibration** → 见 `plot_calibration_linear.png`，线性区间 = **2–12 ppm**。

**Q5a（worksheet 要的报告值）**：
- Slope = **0.01168 ± 0.00129** ppm⁻¹ (95% CI)
- Intercept = **0.00050 ± 0.01007** (95% CI, intensity 单位)
- R² = 0.9937
- Linear range: 2–12 ppm

### C.4 Unknown 荧光

### C.4 Unknown 荧光（3 次重复测量）

| Trial | Run ID | I_peak | λmax_em |
|---|---|---|---|
| 1 | Run 17 | 0.0840 | 519.0 nm |
| 2 | Run 18 | 0.0847 | 515.0 nm |
| 3 | Latest | 0.0851 | 516.6 nm |

- **均值 I̅ = 0.08460**
- **标准差 s = 0.00055**（n=3；相对偏差 0.65%，极好）
- 稀释因子 **f_C = 1**（unknown 原液直接测，未稀释）
- Run 16（I = 0.0165, λmax 544 nm）是误操作的 blank，**忽略**

**Calibration 法反推浓度**：
```
c_cuvette = (I̅ − b) / m = (0.08460 − 0.00050) / 0.01168 = 7.20 ppm
c_A3 = c_cuvette × f_C = 7.20 × 1 = 7.20 ppm
```

✅ 落在 2–12 ppm 线性区中段（接近 7），信号质量好，三次测量高度重合，证明**不需要稀释**决策正确。

**Worksheet Q5b 可以报告**：c_A3 = **7.20 ppm** ± 95% CI（CI 需用 calibration slope/intercept 的 CI + 测量 std 一起传播误差，用提供的 Linear Calibration Spreadsheet 算）。

---

## Part D — Standard Additions — ⚠️ 还没做

每瓶都是 25 mL 容量瓶：**5.0 mL unknown + X mL of 50 ppm stock + 0.02 M HOAc 定容**。

| Flask | unknown (mL) | stock (mL) | I_peak | λmax |
|---|---|---|---|---|
| SA-0 | 5.0 | 0 |   |   |
| SA-1 | 5.0 | 1.0 |   |   |
| SA-2 | 5.0 | 2.0 |   |   |
| SA-3 | 5.0 | 3.0 |   |   |
| SA-4 | 5.0 | 4.0 |   |   |

- [ ] ⭐ D.1 里对 unknown 做的额外稀释因子 f_D = ______

---

## 📊 数据处理公式（回家算时用）

### Calibration 法求 unknown 原液浓度

```
设 Part C 测 unknown 时稀释因子 = f_C
c_cuvette = (I_unk − 0.00050) / 0.01168        # ppm，from 2-12 线性拟合
c_A3 = c_cuvette × f_C                         # A.3 原液浓度
```

### Standard addition 法求 unknown 原液浓度

SA 数据拟合：`I = m × V_added + b`（V_added 单位 mL）

```
x_intercept = -b/m                              # mL of 50 ppm stock equivalent
# 5 mL unknown 在 25 mL 中被稀释 5×，所以 cuvette 内 unknown 浓度：
c_cuvette_unknown = 50 × |x_intercept| / 5     # 注意符号；就是 10 × |-b/m|
c_D1 = c_cuvette_unknown × 5                    # D.1 稀释液浓度（还没考虑 f_D）
c_A3 = c_D1 × f_D                               # A.3 原液浓度
```

（用提供的 Standard Addition Spreadsheet 就不用手算）

### Mass %

```
mg_riboflavin_in_A3 = c_A3 (ppm = mg/L) × 0.250 L
mass% = mg_riboflavin_in_A3 / m_vitamin (mg) × 100%
```

### Theoretical mass % & % error

```
theoretical_mass% = (label_mg_ribo_per_tablet / tablet_mass_mg) × 100%
% error = |experimental − theoretical| / theoretical × 100%
```

---

## 📁 文件清单

| 文件 | 用途 |
|---|---|
| `Untitled1.cmbl` | Logger Pro 原始数据（8 个吸光 + 7 个荧光）|
| `plot_calibration_all7.png` | Q4a 图：7 个 standards 的 calibration curve |
| `plot_calibration_linear.png` | Q4b 图：剔除 20 ppm 后的线性区 calibration |
| `Lab3_Follow_Along.md` | 实验步骤 follow-along |
| `Lab3_Real_Data.md` | **本文件**，真实数据索引 |

---

## ⏭️ 下一步 TODO

1. **测 unknown 荧光**（Part C.4）——原液直接测，重复 2–3 次
   - 如果 I_peak > 0.144 → 稀释 2× 重测
   - 如果 I_peak < 0.029 → 报告信号过弱，不稀释
2. **配 Part D 的 5 个 SA 溶液** + 测荧光
3. 把 Part A 的真实质量/浓度补进本文档
