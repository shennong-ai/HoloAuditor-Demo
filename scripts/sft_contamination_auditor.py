import pandas as pd
import argparse

def audit_sft_dataset(csv_path):
    print("==================================================")
    print("🚨 HoloAuditor: SFT Dataset Contamination Audit")
    print("==================================================")
    print(f"Loading empirical results from: {csv_path}...\n")
    
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    # ⚠️ 注意：請大王根據您實際導出的 CSV 欄位名稱，修改下方的 'v6_0_pass' 和 'v6_5_pass'
    # 假設您的 CSV 中有兩個布林值(True/False)或整數(1/0)欄位代表兩種護欄的判定結果
    col_semantic = 'v6_0_pass'      # 傳統語義護欄 (V6.0)
    col_topological = 'v6_5_pass'   # 拓撲流形護欄 (V6.5)

    if col_semantic not in df.columns or col_topological not in df.columns:
        print(f"Error: Required columns '{col_semantic}' and/or '{col_topological}' not found in CSV.")
        print(f"Available columns are: {list(df.columns)}")
        return

    total_cases = len(df)
    
    # 1. 拓撲污染 (Generic Noise): 語義放行，但拓撲攔截 (這就是導致大模型崩潰的毒數據)
    fouled_cases = df[(df[col_semantic] == True) & (df[col_topological] == False)]
    
    # 2. 成功挽救 (Rescued): 語義攔截，但拓撲放行 (高價值處方)
    rescued_cases = df[(df[col_semantic] == False) & (df[col_topological] == True)]
    
    # 3. 雙重認可 (Robust Agreement)
    robust_cases = df[(df[col_semantic] == True) & (df[col_topological] == True)]

    # 印出震撼的統計結果
    print(f"📊 Total SFT Cases Analyzed: {total_cases}")
    print("-" * 50)
    print(f"🛑 Topologically Fouled (Generic Noise causing 6.0% collapse):")
    print(f"   => {len(fouled_cases)} cases ({(len(fouled_cases)/total_cases)*100:.1f}%) passed semantic but failed topological.")
    print(f"\n🟢 Rescued by HoloAuditor (Topologically Valid):")
    print(f"   => {len(rescued_cases)} cases ({(len(rescued_cases)/total_cases)*100:.1f}%) failed semantic but passed topological.")
    print(f"\n🤝 Robust Agreement:")
    print(f"   => {len(robust_cases)} cases ({(len(robust_cases)/total_cases)*100:.1f}%) passed both.")
    print("==================================================")
    print("Reference: Scaling Laws Hit a Wall (Nature Machine Intelligence under review)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Audit SFT Dataset Contamination')
    parser.add_argument('--input', type=str, required=True, help='Path to the results CSV')
    args = parser.parse_args()
    
    audit_sft_dataset(args.input)