# HoloAuditor-Demo
# 🚨 Scaling Laws Hit a Wall: Evidence of SFT Dataset Contamination

This repository provides the empirical dataset audit logs supporting our preprint: **"Scaling Laws Hit a Wall: Mitigating Semantic Sorting Collapse in Medical LLMs via the HoloAuditor Topological Guardrail."**

We hypothesize that the 6.0% "Semantic Sorting Collapse" observed in next-generation LLMs is fundamentally driven by severe generic noise in Supervised Fine-Tuning (SFT) datasets. 

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
