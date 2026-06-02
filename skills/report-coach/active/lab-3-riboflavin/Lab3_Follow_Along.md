# Lab 3: Riboflavin Fluorescence — 实验 Follow-Along 步骤表

> 跟着这份做就能跑完实验 + 拿到 worksheet 需要的所有数据。
> 凡是标 ⭐ 的地方就是**必须记下来**的数据（worksheet 会用到）。
> 所有"dilute"操作一律用 **0.02 M acetic acid**（不是水！）。

---

## 📋 开工前 Checklist — 在实验台摆好的东西

- [ ] SpectroVis Plus 光谱仪 + cuvette + KimWipes（从 stockroom 领）
- [ ] 笔记本 / 电脑（记 ⭐ 数据 + 拷 Vernier 数据进 Excel）
- [ ] 从 stockroom 领 1 L beaker
- [ ] 4.0 M acetic acid、riboflavin 粉、multivitamin unknown 粉、nanopure water
- [ ] 1 L beaker、500 mL & 250 mL & 25 mL & 50 mL volumetric flasks、Erlenmeyer flask、搅拌子、加热搅拌盘、分析天平（0.1 mg）

---

## Part A — 配溶液

### A.1  配 1 L 的 0.02 M acetic acid（当 solvent 用）

公式：C1V1 = C2V2 → V1 = (0.02 × 1000) / 4.0 = **5.0 mL** of 4.0 M acetic acid

- [ ] 量 5.0 mL 的 4.0 M 乙酸 → 倒进 1 L beaker → 加 nanopure water 到 ~1 L 刻度
- [ ] 标记清楚 "0.02 M HOAc, solvent"

> 不用很精确，approximate volume 就行。

---

### A.2  配 500 mL 的 50.0 ppm riboflavin stock（TA 可能叫你或另一组做）

50 ppm = 50 mg/L → 500 mL 需要 **25.0 mg riboflavin**

- [ ] 分析天平称 riboflavin，**精确到 0.1 mg**，目标约 25.0 mg
- ⭐ **记下实际称到的质量**（e.g. 25.2 mg）→ 用于后面算真实 stock 浓度
- [ ] 倒进 Erlenmeyer flask（**不能用容量瓶加热！**）+ ~450 mL 0.02 M HOAc + 搅拌子
- [ ] 搅拌盘上加热到 50–70 °C，搅拌直到**看不到悬浮颗粒**（约 1 h）
- [ ] 冷却到室温 → 转移到 500 mL 容量瓶 → 定容到刻度线
- ⭐ **记实际 stock 浓度** = (实际 mg / 500 mL) × 1000 = ? ppm

---

### A.3  配 unknown multivitamin 溶液（TA 可能叫你或另一组做）

- [ ] 称 ~50 mg multivitamin powder，**精确到 0.1 mg**
- ⭐ **记下实际称到的质量 m_vitamin**（worksheet 算 mass% 要用！）
- [ ] 倒进 Erlenmeyer flask + ~200 mL 0.02 M HOAc + 搅拌子，搅拌溶解
- [ ] 转移到 250 mL 容量瓶 → 定容

**⭐⭐⭐ 同时抄下老师在课上给的 multivitamin 信息（非常重要，worksheet discussion 要用）：**
- ⭐ 一片 tablet 的质量 = ______ mg
- ⭐ Nutrition label 上每片含 riboflavin (B2) 的量 = ______ mg
- ⭐ Multivitamin 牌子 / 批号（如果有）

---

### A.4  配 7–10 个标准溶液（每对一组）

每个都是 **25 mL 容量瓶**。C1V1 = C2V2，V1 = C2 × 25 / 50 = **C2 × 0.5 mL**。

| 目标浓度 | 取 50 ppm stock 体积 | 定容 |
|---|---|---|
| 0 ppm (blank) | 0 mL | 25 mL 用 0.02 M HOAc |
| 2 ppm  | **1.0 mL** | 25 mL |
| 4 ppm  | **2.0 mL** | 25 mL |
| 6 ppm  | **3.0 mL** | 25 mL |
| 8 ppm  | **4.0 mL** | 25 mL |
| 10 ppm | **5.0 mL** | 25 mL |
| 12 ppm | **6.0 mL** | 25 mL |
| 14 ppm | **7.0 mL** | 25 mL |
| 20 ppm | **10.0 mL** | 25 mL |

- [ ] 全部标好浓度标签
- [ ] 对比 unknown 颜色 vs standards，⭐ **目测估计 unknown 浓度** ≈ ______ ppm

---

## Part B — 吸收光谱（Absorbance）

### B.1  校准光谱仪

- [ ] 打开 Logger Pro（仪器没识别就拔插 USB）
- [ ] **Experiment → Calibrate**，灯预热 ≥ 90 s
- [ ] cuvette 装 0.02 M HOAc 当 blank，KimWipe 擦干净外壁（**注意 cuvette 方向要一致**，用记号笔标一面）
- [ ] 放进去 → 按 **Finish Calibration**

### B.2  扫谱（最低浓度、最高浓度、unknown 这三个必须扫）

对每个样品：先用它 prerinse cuvette → 装满 → 擦干 → 放进去 → **Collect** → **Stop** → 需要对比就 **Store Latest Run** → Save。

- [ ] 扫 **最低浓度**（非 0 的，即 2 ppm）→ Save spectrum
- [ ] 扫 **最高浓度**（20 ppm）→ Store Latest Run → Save
- [ ] 扫 **unknown 溶液** → Save spectrum
- [ ] （可选 / 建议）中间浓度挑一两个也扫，worksheet Q1 要画 overlay 图

### B.3  记录

- ⭐ 把 Vernier 数据表**全部复制进 Excel**（保存.xlsx，等会儿做 overlay plot）
- ⭐ 记下 **20 ppm 在 405 nm 的吸光度** A(405) = ______
- ⭐ 记下 **20 ppm 在 500 nm 的吸光度** A(500) = ______
- ⭐ 记下每个 spectrum 的 **λ_max**

→ **决定激发波长**：比较 A(405) vs A(500)，**选吸收大的那个**作为 fluorescence 激发波长。
⭐ 我选的激发波长 = ______ nm（worksheet Q2 的答案）

---

## Part C — 荧光测量（Fluorescence Calibration）

⚠️ 动态范围窄：< 1 ppm 没信号，> 10 ppm 可能饱和。浓度高的若比浓度低的信号还低 → 饱和了，从 calibration 里扔掉。

### C.1  切换到 fluorescence 模式

- [ ] **Experiment → Change Units → Fluorescence**，选上面决定好的激发波长（405 或 500 nm）

### C.2  按浓度从高到低测 standards

对 20, 14, 12, 10, 8, 6, 4, 2, 0 ppm 每个：
- [ ] cuvette prerinse → 装样 → 擦干 → 放进去 → **Start**
- [ ] 等几秒钟读数稳定 → 记录 → Save spectrum

⭐ **数据表（边做边填）**：

| 浓度 (ppm) | λ_max (nm) | 荧光强度 (peak intensity) |
|---|---|---|
| 0  |   |   |
| 2  |   |   |
| 4  |   |   |
| 6  |   |   |
| 8  |   |   |
| 10 |   |   |
| 12 |   |   |
| 14 |   |   |
| 20 |   |   |

- ⭐ 边测边在脑子里画图：浓度 ↑ 荧光 ↑ 是正常的；哪一点开始 plateau 或下降 → **inner filter effect**，记下来（worksheet Q4b 要用）

### C.3  测 unknown 荧光

- [ ] 测 unknown → 看 signal 是否**落在 calibration 的线性区间**里
- [ ] 如果 signal 太高（超出最高线性点）→ **稀释 2× 再测**（取 X mL unknown + X mL 0.02 M HOAc）
- [ ] 信号在 range 内后 → **测 2–3 次**（每次用不同取样量 / 重新装 cuvette）

⭐ Unknown 荧光数据：
- 稀释因子 = ______（如果没稀释写 1）
- Trial 1 intensity = ______
- Trial 2 intensity = ______
- Trial 3 intensity = ______
- λ_max = ______ nm

### C.4  检查线性区间够不够

- ⭐ 在 Excel 里快速画 fluorescence vs. concentration，看哪一段 R² 接近 1
- [ ] 如果**线性区间内的点少于 3 个** → 必须**再配一些浓度在线性区间的标准液**补测

---

## Part D — 标准加入法（Standard Additions）

### D.1  确认 unknown 信号在 calibration range 内

- [ ] 如果 unknown 原液信号过强 → 先**用 50 mL 容量瓶稀释一份 unknown**（记稀释因子），让它落在 calibration 区间里
- ⭐ **记下 standard addition 用的 unknown 稀释因子 f_D**（没稀释写 1）

### D.2  配 5 份 standard addition 溶液（全是 25.0 mL 容量瓶）

每份先加 **5.0 mL unknown** (D.1 里那个)，再加下面体积的 **50.0 ppm stock**，再用 0.02 M HOAc 定容到 25 mL：

| Flask # | unknown (mL) | 50 ppm stock (mL) | 定容 |
|---|---|---|---|
| SA-0 | 5.0 | **0** | 25.0 mL |
| SA-1 | 5.0 | **1.0** | 25.0 mL |
| SA-2 | 5.0 | **2.0** | 25.0 mL |
| SA-3 | 5.0 | **3.0** | 25.0 mL |
| SA-4 | 5.0 | **4.0** | 25.0 mL |

> 如果加了 stock 后信号饱和了 → 再稀一点 unknown，或者换更低浓度的 stock 重来。

### D.3  测这 5 份的荧光光谱

- [ ] 按顺序（从 SA-0 → SA-4）每个测一遍，Save spectrum

⭐ **数据表**：

| Flask | 加入 stock 体积 (mL) | peak intensity | λ_max |
|---|---|---|---|
| SA-0 | 0 |   |   |
| SA-1 | 1.0 |   |   |
| SA-2 | 2.0 |   |   |
| SA-3 | 3.0 |   |   |
| SA-4 | 4.0 |   |   |

→ worksheet Q6 要画 **intensity vs. added volume (mL)** 的直线

---

## Part E — 清场

- [ ] 所有溶液用 **sodium bicarbonate 中和** 再倒 drain
- [ ] 关 Logger Pro，正确地**拔 USB**（先"安全弹出"）
- [ ] 光谱仪盒 + 借的玻璃器皿还 stockroom

---

## 🧾 带回家前最后 Check（worksheet 需要的所有素材）

- [ ] ⭐ 实际 riboflavin stock 浓度（用精确质量算出的）
- [ ] ⭐ 多维元素片 tablet 质量 + label 上 riboflavin 含量 + 自己称的 m_vitamin
- [ ] ⭐ Excel 里有所有 **absorbance spectra**（blank / 低 / 高 / unknown）原始数据
- [ ] ⭐ A(405) 和 A(500) 的数值 + 选的激发波长 + 原因
- [ ] ⭐ 所有 standard 的 **fluorescence spectra** 原始数据 + peak intensity 表
- [ ] ⭐ 2–3 次 unknown 荧光 + 稀释因子
- [ ] ⭐ 5 份 standard addition 的 spectra + peak intensity
- [ ] ⭐ D.1 里对 unknown 的额外稀释因子（做 SA 前稀释了多少）
- [ ] 所有 Vernier 数据都已拷到 Excel 并保存

---

## 📐 后续数据处理提示（回家后做 worksheet 用）

1. **Calibration curve (Q4)**：fluorescence vs. ppm，扔掉 inner filter effect 的点后用 `LINEST`（或提供的 Linear Calibration Spreadsheet）拿 slope、intercept、95% CI。
2. **Unknown 浓度 (Q5b)**：`c_unknown_in_cuvette = (I_unknown − intercept) / slope`；再乘上 Part C 的稀释因子还原到 A.3 原液的浓度。
3. **Mass% (Q5c)**：`mass% = (c_A.3 (ppm) × 0.250 L × 10⁻⁶ g/µg×1000 ) / m_vitamin × 100%`
   换算：`mg_riboflavin_in_A.3 = c_A.3 (ppm=mg/L) × 0.250 L`，然后 `mass% = mg_ribo / m_vitamin(mg) × 100%`。
4. **Standard addition (Q6–Q8)**：用提供的 Standard Addition Spreadsheet；x-intercept = `−b/m` 就是 cuvette 内 unknown 贡献的等效浓度 → 乘 25/5 = 5 → 再乘 D.1 额外稀释因子 → 得到 A.3 原液浓度。
5. **Theoretical mass%**：label 里每片 riboflavin mg ÷ 一片 tablet 总 mg × 100%。
6. **% error**：|实验值 − 理论值| / 理论值 × 100%。
