# -*- coding: utf-8 -*-
"""Dataset-level V6.0 vs V6.5 audit cross-tab from the two released CSVs.
Mirrors scripts/sft_contamination_auditor.py logic (semantic=V6.0, topological=V6.5)."""
import io, sys, zipfile, tempfile, os
import pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
out = []

BASE = r"C:\Users\admin\Documents\ShenNongAIAcademic\NatureMI4\HoloAuditor-demo\data"

def audit(df, label):
    n = len(df)
    both_pass = int(((df["可靠"] == True) & (df["是否可疑"] == False)).sum())
    rescued   = int(((df["可靠"] == False) & (df["是否可疑"] == False)).sum())
    fouled    = int(((df["可靠"] == True) & (df["是否可疑"] == True)).sum())
    both_fail = int(((df["可靠"] == False) & (df["是否可疑"] == True)).sum())
    out.append("%s: n=%d" % (label, n))
    out.append("  可靠(V6.5) pass rate: %.1f%%" % (100.0 * (df["可靠"] == True).sum() / n))
    out.append("  是否可疑(V6.0 flag) rate: %.1f%%" % (100.0 * (df["是否可疑"] == True).sum() / n))
    out.append("  both-pass %.1f%% | rescued(V6.5 only pass) %.1f%% | fouled(V6.0 pass, V6.5 flag) %.1f%% | both-fail %.1f%%" % (
        100.0*both_pass/n, 100.0*rescued/n, 100.0*fouled/n, 100.0*both_fail/n))
    out.append("  差异类别 value counts: %s" % df["差异类别"].value_counts(dropna=False).to_dict())

df_sft = pd.read_csv(os.path.join(BASE, "sft_comparison_full.csv"))
audit(df_sft, "SFT comparison")
z = zipfile.ZipFile(os.path.join(BASE, "shennong_comparison_full.zip"))
d = tempfile.mkdtemp()
z.extractall(d)
df_sn = pd.read_csv(os.path.join(d, "shennong_comparison_full.csv"))
audit(df_sn, "ShenNong comparison")

open(r"C:\Users\admin\.zcode\workspace\default\paper-audit\cline_workspace\dataset_audit_out.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
