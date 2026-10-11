# HoloAuditor-Demo
# 🚨 Scaling Laws Hit a Wall: Evidence of SFT Dataset Contamination

This repository provides the empirical dataset audit logs supporting our preprint: **"Scaling Laws Hit a Wall: Mitigating Semantic Sorting Collapse in Medical LLMs via the HoloAuditor Topological Guardrail."**

We hypothesize that the 6.0% "Semantic Sorting Collapse" observed in next-generation LLMs is fundamentally driven by severe generic noise in Supervised Fine-Tuning (SFT) datasets. 

[![SSRN](https://img.shields.io/badge/SSRN-Preprint_Published-blue.svg)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6368538)
Read our foundational paper on mitigating LLM collapse via topological manifolds.



## 📊 The Proof: HoloTSH Dataset Distiller (V3.1)
Using our `HoloAuditor` topological guardrail (V6.5) against a baseline semantic text guardrail (V6.0), we scanned massive TCM polypharmacy datasets. The results provide concrete evidence of structural contamination:

### SFT Dataset Audit Results (Total: 39,635 cases):
- 🛑 **12,245 cases (Topologically Fouled):** Passed the baseline semantic check (V6.0) but were flagged as structurally unreliable (low topological score) by our V6.5 HoloAuditor. *This is the generic noise causing LLM collapse.*
- 🟢 **4,354 cases (Rescued):** Failed the baseline text check but were verified as topologically robust prescriptions by HoloAuditor.

*(See the `/data` folder for the comparison CSVs and specific clinical examples, such as Case 13 and Case 5959, demonstrating the topological scoring).*

## ⚠️ Note on Intellectual Property
The full underlying code for the topological manifold embedding (Dimension: 64) and Tensor-Laplacian decomposition used in `HoloAuditor_SFT_Audit_Demo.ipynb` is currently under peer review at a primary journal. The code has been redacted in this repository. We will release the full open-source framework upon publication.

## 📊 Data Evidence (For Non-Coders & Reviewers)

To ensure full transparency and accessibility for researchers without Python/Colab environments, we have exported the raw execution logs of our 5 core experiments. You can directly view the unedited outputs in the `/data_evidence` directory:

* 📄 **`01_Gemini_3.1Pro_ZeroShot_Collapse.txt`**
    * **What it proves:** The explicit "Semantic Sorting Collapse". Watch as the latest Gemini 3.1 Pro fails catastrophicly (6.0% Hit@1 accuracy) on 100 strict zero-shot TCM cases.
* 📄 **`02_Ablation_GLM4_vs_Gemini2.5Pro.txt`**
    * **What it proves:** The ablation leaderboard. It demonstrates that earlier models (Gemini 2.5 Pro at 33.0%) and open-weight models (GLM-4 Flash) maintain better topological integrity before the "Alignment Tax" destroys the reasoning paths in V3.1.
* 📄 **`03_SFT_Audit_Summary_Overview.txt`**
    * **What it proves:** The root cause of the LLM collapse. This log summarizes our full-scale scan, revealing the massive volume of "Generic Noise" contaminating the SFT datasets.
* 📄 **`04 & 05_SFT_Audit_Detailed_Analysis_Part1/2.txt`**
    * **What it proves:** Deep-dive empirical evidence. Contains specific case-by-case proof (e.g., 12,245 cases) where traditional semantic guardrails (V6.0) failed, but our topological guardrail (V6.5) successfully flagged the hidden ontological fouls.

## 📚 Data Availability & Acknowledgements

The empirical audits and topological manifold embeddings in this study rely on several publicly available databases. We deeply acknowledge the original creators for advancing open science and medical informatics in Traditional Chinese Medicine (TCM). 

The raw data sources audited in our research include:

* **SymMap Database**: Used as the foundational relational knowledge graph for constructing our pre-computational topological manifold.
  > **Citation**: Wu, Y., et al. (2019). SymMap: an integrative database of traditional Chinese medicine enhanced by symptom mapping. *Nucleic Acids Research*, 47(D1), D1110-D1117.
* **ShenNong & TCM-SFT Datasets**: The massive instruction-tuning datasets evaluated in our contamination audit (the 39k+ cases) are derived from publicly available TCM Large Language Model initiatives (e.g., ShenNong-TCM / open-source instruction tuning datasets). 
* **Zero-Shot Evaluation Benchmark**: The 100 high-quality, expert-verified cases used to demonstrate the 6.0% "Semantic Sorting Collapse" are extracted and strictly isolated from the aforementioned knowledge graphs to prevent data leakage. 

**Academic License Note**: The exported audit logs provided in the `/data_evidence` directory of this repository are intended strictly for academic peer-review, algorithmic auditing, and reproducibility purposes. They do not contain executable topological code, ensuring compliance with the original licenses of the respective datasets while protecting the intellectual property of the `HoloAuditor` framework currently under peer review.

🔗 **Preprint Paper:** [Scaling Laws Hit a Wall (SSRN 6368538 - Under Review)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6368538)


---

## Reproducibility (added 2026-10)

Every headline number is independently recomputable from the artefacts in this repository:

| Claim | Recompute script | Input artefact | Agreement |
|---|---|---|---|
| Run-1 native Hit@1/3 (Gemini 2.5 Pro 33/36; GLM-4-Flash 42/46) | `scripts/recompute_run1.py` | `data_evidence/02_Ablation_GLM4_vs_Gemini2.5Pro.txt` | exact |
| Run-1 guarded Hit@1 = 45 (33 preserved + 12 rescued, 0 broken) | `scripts/recompute_run1.py` | same (100 logged reranks) | exact |
| Run-2 collapse Hit@1 = 6.0 -> 24.0 (n=100, empty returns = miss) | `scripts/recompute_run2.py` | `data_evidence/01_Gemini_3.1Pro_ZeroShot_Collapse.txt` | exact |
| Popularity bias: 64% / 54% for the two generic dual-deficiency labels | `scripts/recompute_run2.py` | same (100 output lists) | exact |
| Dataset audit cross-tab (39,635 + 209,684 pairs, four categories) | `scripts/recompute_dataset_audit.py` | `data/sft_comparison_full.csv`, `data/shennong_comparison_full.zip` | exact |
| Audit scoring latency 0.163 ms/query (desktop CPU) | `scripts/benchmark_audit_latency.py` | manifold size 1,851 x 64 as logged | measured |

Notes: run-1 logs truncate candidate printing at 4 items, so engine-side Hit@5 is authoritative;
run-2 Hit@3/Hit@5 are computed over the 98 questions with non-empty returns. Per-class breakdown
and the majority-class baseline (53.0%) are reported in the manuscript under submission and in
`figures/`. The core manifold-construction code remains redacted pending intellectual-property
review; it is available to reviewers on request and does not affect any recomputation above.
