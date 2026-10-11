# -*- coding: utf-8 -*-
"""Publication figures for the C-line merged paper. All numbers from ALIGNMENT_TABLE_MASTER."""
import io, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

plt.rcParams.update({
    "font.size": 9, "axes.linewidth": 0.8, "axes.spines.top": False,
    "axes.spines.right": False, "figure.dpi": 300, "savefig.bbox": "tight",
    "font.family": "DejaVu Sans",
})
C_NATIVE = "#8DA0CB"   # muted blue
C_GUARD  = "#33A02C"   # green
C_MAJ    = "#B25900"   # dark orange for baseline
OUT = r"C:\Users\admin\.zcode\workspace\default\paper-audit\cline_submission"

# ---------------- Fig 1: main results ----------------
fig, ax = plt.subplots(figsize=(4.6, 3.2))
models = ["Gemini 3.1 Pro\n(frontier)", "Gemini 2.5 Pro", "GLM-4-Flash\n(open, lightweight)"]
native = [6.0, 33.0, 42.0]
guard  = [24.0, 45.0, 57.0]
x = np.arange(3); w = 0.36
b1 = ax.bar(x - w/2, native, w, label="Native (zero-shot)", color=C_NATIVE, edgecolor="black", linewidth=0.5)
b2 = ax.bar(x + w/2, guard,  w, label="+ HoloAuditor guardrail", color=C_GUARD, edgecolor="black", linewidth=0.5)
ax.axhline(53.0, color=C_MAJ, linestyle="--", linewidth=1.1)
ax.text(-0.42, 54.5, "Majority-class\nbaseline (53.0%)", ha="left", va="bottom", fontsize=7.5, color=C_MAJ)
for b in list(b1) + list(b2):
    ax.text(b.get_x() + b.get_width()/2, b.get_height() + 1.2, "%.0f%%" % b.get_height(),
            ha="center", fontsize=8)
for i in range(3):
    ax.annotate("", xy=(x[i] + w/2, guard[i] - 1.2), xytext=(x[i] - w/2, native[i] + 1.2),
                arrowprops=dict(arrowstyle="->", color="0.25", lw=1.0, connectionstyle="arc3,rad=-0.25"))
ax.set_xticks(x); ax.set_xticklabels(models, fontsize=8)
ax.set_ylabel("Hit@1 accuracy (%)")
ax.set_ylim(0, 72)
ax.legend(frameon=False, fontsize=8, loc="upper right")
ax.set_title("A  David-vs-Goliath exam (100 cases, exact match)", fontsize=9, loc="left", fontweight="bold")
fig.savefig(OUT + r"\fig1_main_results.png")
plt.close(fig)

# ---------------- Fig 2: popularity bias ----------------
import matplotlib.font_manager as fm
_cjk = None
for fname in ["msyh.ttc", "msyh.ttf", "simsun.ttc", "simhei.ttf"]:
    try:
        _cjk = fm.FontProperties(fname="C:\\Windows\\Fonts\\" + fname)
        break
    except Exception:
        continue
fig, ax = plt.subplots(figsize=(4.6, 3.0))
cands = ["气血两虚 (Qi-Blood dual deficiency)", "气阴两虚 (Qi-Yin dual deficiency)", "心气虚 (Heart-Qi deficiency)",
         "心脾两虚 (Heart-Spleen deficiency)", "气虚血瘀 (Qi def.-blood stasis)", "脾气虚 (Spleen-Qi deficiency)",
         "气滞血瘀 (Qi stag.-blood stasis)", "心阳虚 (Heart-Yang deficiency)", "肺气虚 (Lung-Qi deficiency)",
         "心肺气虚 (Heart-Lung-Qi deficiency)"]
vals = [64, 54, 51, 49, 49, 48, 45, 40, 39, 31]
colors = ["#D95F02"] * 2 + ["#7570B3"] * 8
ypos = np.arange(len(cands))[::-1]
ax.barh(ypos, vals, color=colors, edgecolor="black", linewidth=0.4, height=0.68)
ax.set_yticks(ypos)
if _cjk is not None:
    ax.set_yticklabels(cands, fontproperties=_cjk, fontsize=6.8)
else:
    ax.set_yticklabels(cands, fontsize=6.8)
for yp, v in zip(ypos, vals):
    ax.text(v + 1.0, yp, "%d%%" % v, va="center", fontsize=7.5)
ax.axvline(50, color="grey", linestyle=":", linewidth=0.8)
ax.set_xlabel("Presence rate across the 100 case output lists (%)")
ax.set_xlim(0, 74)
ax.set_title("B  Popularity bias of the collapsed frontier model", fontsize=9, loc="left", fontweight="bold")
fig.savefig(OUT + r"\fig2_popularity_bias.png")
plt.close(fig)

# ---------------- Fig 3: dataset-level audit ----------------
fig, ax = plt.subplots(figsize=(4.6, 2.9))
corpora = ["SFT corpus\n(39,635 pairs)", "ShenNong corpus\n(209,684 pairs)"]
both_pass  = [5.2, 52.9]
fouled     = [30.9, 41.4]
rescued    = [11.0, 2.8]
both_fail  = [52.9, 2.9]
x = np.arange(2); w = 0.52
p1 = ax.bar(x, both_pass, w, label="Pass both audits", color="#A6D854", edgecolor="black", linewidth=0.4)
p2 = ax.bar(x, fouled, w, bottom=both_pass, label="V6.0 passes, V6.5 flags (topologically fouled)", color="#D95F02", edgecolor="black", linewidth=0.4)
bot2 = [both_pass[i] + fouled[i] for i in range(2)]
p3 = ax.bar(x, rescued, w, bottom=bot2, label="V6.5 passes, V6.0 flags (rescued)", color="#66C2A5", edgecolor="black", linewidth=0.4)
bot3 = [bot2[i] + rescued[i] for i in range(2)]
p4 = ax.bar(x, both_fail, w, bottom=bot3, label="Fail both", color="0.55", edgecolor="black", linewidth=0.4)
def seg_label(bars, vals, bottoms):
    for b, v, bo in zip(bars, vals, bottoms):
        if v >= 6:
            ax.text(b.get_x() + b.get_width()/2, bo + v/2, "%.1f%%" % v, ha="center", va="center", fontsize=7.5,
                    color="white" if b.get_facecolor()[:3] <= (0.6, 0.6, 0.6) else "black")
seg_label(p1, both_pass, [0, 0]); seg_label(p2, fouled, both_pass); seg_label(p3, rescued, bot2); seg_label(p4, both_fail, bot3)
ax.set_xticks(x); ax.set_xticklabels(corpora, fontsize=8)
ax.set_ylabel("Share of audited symptom-formula pairs (%)")
ax.legend(frameon=False, fontsize=6.6, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2)
ax.set_ylim(0, 104)
ax.set_title("C  Dataset-level contamination audit (V6.0 vs V6.5)", fontsize=9, loc="left", fontweight="bold")
fig.savefig(OUT + r"\fig3_dataset_audit.png")
plt.close(fig)

# ---------------- Fig 4: per-class generation regression + rescue ----------------
fig, ax = plt.subplots(figsize=(4.6, 2.9))
# on the dominant class 气虚 (Qi deficiency; 51-53 of exam cases)
groups = ["Gemini 2.5 Pro\n(run 1)", "Gemini 3.1 Pro\n(run 2)"]
nat_qd = [62.0, 10.0]
grd_qd = [83.0, 43.0]
x = np.arange(2); w = 0.34
b1 = ax.bar(x - w/2, nat_qd, w, label="Native", color=C_NATIVE, edgecolor="black", linewidth=0.5)
b2 = ax.bar(x + w/2, grd_qd, w, label="+ HoloAuditor", color=C_GUARD, edgecolor="black", linewidth=0.5)
for b in list(b1) + list(b2):
    ax.text(b.get_x() + b.get_width()/2, b.get_height() + 1.5, "%.0f%%" % b.get_height(), ha="center", fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(groups, fontsize=8)
ax.set_ylabel("Hit@1 on Qi-deficiency cases (%)")
ax.set_ylim(0, 100)
ax.legend(frameon=False, fontsize=8)
ax.set_title("D  Generational regression concentrates on the dominant class", fontsize=9, loc="left", fontweight="bold")
fig.savefig(OUT + r"\fig4_per_class.png")
plt.close(fig)

print("4 figures written")
