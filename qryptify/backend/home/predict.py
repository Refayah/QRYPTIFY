import os
import sys
import warnings
import numpy as np
import pandas as pd
import joblib

warnings.filterwarnings("ignore")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # This is backend/home/
MODEL_DIR = os.path.join(os.path.dirname(BASE_DIR), "qryptify_models")  # This is backend/qryptify_models/
print(os.path.join(MODEL_DIR, "scaler_v2.joblib"))
print("Loading models...")
scaler          = joblib.load(os.path.join(MODEL_DIR, "scaler_v2.joblib"))
top_k_idx       = joblib.load(os.path.join(MODEL_DIR, "top_k_feature_idx.joblib"))
selected_names  = joblib.load(os.path.join(MODEL_DIR, "selected_feature_names.joblib"))
le_cat          = joblib.load(os.path.join(MODEL_DIR, "le_cat_v2.joblib"))
le_type         = joblib.load(os.path.join(MODEL_DIR, "le_type_v2.joblib"))
le_algo         = joblib.load(os.path.join(MODEL_DIR, "le_algo_v2.joblib"))
cat_xgb         = joblib.load(os.path.join(MODEL_DIR, "cat_xgb_v2.joblib"))
type_xgb        = joblib.load(os.path.join(MODEL_DIR, "type_xgb_v2.joblib"))
global_xgb      = joblib.load(os.path.join(MODEL_DIR, "global_xgb_v2.joblib"))
cat_sub_models  = joblib.load(os.path.join(MODEL_DIR, "cat_sub_models_v2.joblib"))
best_alpha      = joblib.load(os.path.join(MODEL_DIR, "best_alpha.joblib"))
N_ALGO          = len(le_algo.classes_)

print(f"  ✓ Models loaded")
print(f"  Algorithms : {list(le_algo.classes_)}")
print(f"  Best alpha : {best_alpha}")
print(f"  Scaler expects {scaler.n_features_in_} features")

CNN_AVAILABLE = False
cnn_model = cnn_device = None

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset

    class CryptoCNN(nn.Module):
        def __init__(self, in_features, n_classes, emb_dim=64):
            super().__init__()
            self.conv1 = nn.Sequential(
                nn.Conv1d(1, 64, kernel_size=3, padding=1),
                nn.BatchNorm1d(64), nn.GELU(), nn.Dropout(0.2))
            self.conv2 = nn.Sequential(
                nn.Conv1d(64, 128, kernel_size=5, padding=2),
                nn.BatchNorm1d(128), nn.GELU(), nn.Dropout(0.2))
            self.conv3 = nn.Sequential(
                nn.Conv1d(128, 256, kernel_size=7, padding=3),
                nn.BatchNorm1d(256), nn.GELU())
            self.pool       = nn.AdaptiveAvgPool1d(1)
            self.embed      = nn.Sequential(nn.Linear(256, emb_dim), nn.GELU())
            self.classifier = nn.Linear(emb_dim, n_classes)

        def forward(self, x):
            x = x.unsqueeze(1)
            x = self.conv1(x); x = self.conv2(x); x = self.conv3(x)
            x = self.pool(x).squeeze(-1)
            emb = self.embed(x)
            return self.classifier(emb), emb

    cnn_path = os.path.join(MODEL_DIR, "cnn_model_v2.pt")
    if os.path.exists(cnn_path):
        cnn_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        cnn_model  = CryptoCNN(len(top_k_idx), N_ALGO, 64).to(cnn_device)
        cnn_model.load_state_dict(
            torch.load(cnn_path, map_location=cnn_device))
        cnn_model.eval()
        CNN_AVAILABLE = True
        print(f"  ✓ CNN loaded on {cnn_device}")
    else:
        print("  ⚠ CNN weights not found — running without CNN")
except ImportError:
    print("  ⚠ PyTorch not available — running without CNN")

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for split in [256, 512, 768, 1024, 2048]:
        f = f"entropy_split_{split}"
        if f"{f}_first" in df.columns and f"{f}_second" in df.columns:
            df[f"{f}_diff"] = df[f"{f}_first"] - df[f"{f}_second"]
            df[f"{f}_max"]  = df[[f"{f}_first", f"{f}_second"]].max(axis=1)
    if "length_mod_16" in df.columns and "padding_consistency" in df.columns:
        df["cbc_score"] = (
            (df["length_mod_16"] == 0).astype(float) * 0.5 +
            df["padding_consistency"] * 0.5)
    if "compression_ratio_y" in df.columns and "transition_rate" in df.columns:
        df["stream_score"] = df["compression_ratio_y"] * df["transition_rate"]
    if "ciphertext_length" in df.columns:
        df["length_log"] = np.log1p(df["ciphertext_length"])
        df["length_sq"]  = np.sqrt(df["ciphertext_length"].clip(0))
        for mod in [128, 256, 512]:
            df[f"len_mod_{mod}"] = df["ciphertext_length"] % mod
    if "entropy_bits" in df.columns and "entropy_bytes" in df.columns:
        df["entropy_ratio_bits_bytes"] = df["entropy_bits"] / (df["entropy_bytes"] + 1e-9)
    if "spectral_entropy" in df.columns and "dominant_freq_ratio" in df.columns:
        df["spectral_signature"] = df["spectral_entropy"] * df["dominant_freq_ratio"]
    if all(c in df.columns for c in ["acf_lag1","acf_lag2","acf_lag4","acf_lag8"]):
        df["acf_sum"]   = df["acf_lag1"] + df["acf_lag2"] + df["acf_lag4"] + df["acf_lag8"]
        df["acf_decay"] = df["acf_lag1"] - df["acf_lag8"]
    if "run_mean" in df.columns and "run_std" in df.columns:
        df["run_dispersion"] = df["run_std"] / (df["run_mean"] + 1e-9)
    if "max_byte_freq" in df.columns and "min_byte_freq" in df.columns:
        df["byte_freq_imbalance"] = df["max_byte_freq"] - df["min_byte_freq"]
    if "chunk64_entropy_mean" in df.columns and "chunk64_entropy_std" in df.columns:
        df["chunk_entropy_cv"] = df["chunk64_entropy_std"] / (df["chunk64_entropy_mean"] + 1e-9)
    if "kl_divergence_first_second" in df.columns and "chi_square_first_second" in df.columns:
        df["dist_score"] = (
            np.log1p(df["kl_divergence_first_second"]) +
            np.log1p(df["chi_square_first_second"]))
    if "win_entropy_mean" in df.columns and "win_entropy_var" in df.columns:
        df["win_entropy_cv"] = (
            np.sqrt(df["win_entropy_var"].clip(0)) / (df["win_entropy_mean"] + 1e-9))
    if "hamming_mean" in df.columns and "hamming_var" in df.columns:
        df["hamming_cv"] = (
            np.sqrt(df["hamming_var"].clip(0)) / (df["hamming_mean"] + 1e-9))
    return df

def align_to_scaler(df: pd.DataFrame, scaler) -> np.ndarray:
    
    META = ["Category", "Algorithm_Type", "Algorithm", "sample_id"]
    df   = df.drop(columns=[c for c in META if c in df.columns], errors="ignore")
    df   = engineer_features(df)
    df   = df.fillna(0.0).replace([np.inf, -np.inf], 0.0)

    n_scaler = scaler.n_features_in_   # 185
    pos_to_name = {}
    for name, pos in zip(selected_names, top_k_idx):
        pos_to_name[int(pos)] = name

    rows_out = np.zeros((len(df), n_scaler), dtype=np.float32)
    for pos, name in pos_to_name.items():
        if name in df.columns:
            rows_out[:, pos] = df[name].values.astype(np.float32)

    return rows_out

def get_cnn_embeddings(model, X, device, batch=512):
    from torch.utils.data import DataLoader, TensorDataset
    import torch
    model.eval()
    dl = DataLoader(
        TensorDataset(torch.tensor(X, dtype=torch.float32)),
        batch_size=batch, shuffle=False)
    embs, probs = [], []
    with torch.no_grad():
        for (xb,) in dl:
            xb = xb.to(device)
            o, emb = model(xb)
            embs.append(emb.cpu().numpy())
            probs.append(o.softmax(1).cpu().numpy())
    return np.vstack(embs), np.vstack(probs)

def run_ensemble(X_l3, cat_prob, global_prob, cat_sub_models, alpha):
    n_algo     = global_prob.shape[1]
    n_samples  = X_l3.shape[0]
    final_prob = np.zeros((n_samples, n_algo))
    cat_pred   = np.argmax(cat_prob, axis=1)

    for i in range(n_samples):
        c_idx    = cat_pred[i]
        global_p = global_prob[i]
        if c_idx in cat_sub_models:
            info = cat_sub_models[c_idx]
            if info[0] == "trivial":
                local_full = np.zeros(n_algo)
                local_full[info[2]] = 1.0
            else:
                _, local_le, sub_xgb = info
                sub_p      = sub_xgb.predict_proba(X_l3[i:i+1])[0]
                local_full = np.zeros(n_algo)
                for li, gi in enumerate(local_le.classes_):
                    local_full[gi] = sub_p[li]
            final_prob[i] = (1 - alpha) * global_p + alpha * local_full
        else:
            final_prob[i] = global_p

    return np.argmax(final_prob, axis=1), final_prob

def predict(df_input: pd.DataFrame) -> list[dict]:

    # ── Step A: align columns → scale → select top-K ─────────────────────────
    X_full = align_to_scaler(df_input, scaler)          # (n, 185)
    X_sc   = scaler.transform(X_full)                   # (n, 185)
    X_sel  = X_sc[:, top_k_idx]                         # (n, 120)

    # ── Step B: CNN augmentation (if available) ───────────────────────────────
    if CNN_AVAILABLE:
        emb, prob_cnn = get_cnn_embeddings(cnn_model, X_sel, cnn_device)
        X_aug = np.hstack([X_sel, emb, prob_cnn])       # (n, 208)
    else:
        X_aug = X_sel                                    # (n, 120)

    # ── Step C: Hierarchical cascade ─────────────────────────────────────────
    cat_prob  = cat_xgb.predict_proba(X_aug)             # (n, 5)
    X_l2      = np.hstack([X_aug, cat_prob])
    type_prob = type_xgb.predict_proba(X_l2)             # (n, 8)
    X_l3      = np.hstack([X_l2, type_prob])
    glob_prob = global_xgb.predict_proba(X_l3)           # (n, 24)

    _, final_prob = run_ensemble(X_l3, cat_prob, glob_prob,
                                 cat_sub_models, best_alpha)

    # ── Step D: Build results ─────────────────────────────────────────────────
    cat_idx_arr  = np.argmax(cat_prob,  axis=1)
    type_idx_arr = np.argmax(type_prob, axis=1)

    results = []
    for i in range(len(df_input)):
        probs_pct = final_prob[i] / final_prob[i].sum() * 100
        top5_idx  = np.argsort(probs_pct)[::-1][:5]

        top5 = [
            {
                "rank":        r + 1,
                "algorithm":   le_algo.classes_[idx],
                "probability": round(float(probs_pct[idx]), 4),
            }
            for r, idx in enumerate(top5_idx)
        ]

        results.append({
            "predicted_category":   le_cat.classes_[cat_idx_arr[i]],
            "category_confidence":  round(float(cat_prob[i].max() * 100), 4),
            "predicted_type":       le_type.classes_[type_idx_arr[i]],
            "type_confidence":      round(float(type_prob[i].max() * 100), 4),
            "predicted_algorithm":  top5[0]["algorithm"],
            "algorithm_confidence": top5[0]["probability"],
            "top5":                 top5,
        })
    for i, r in enumerate(results):
        print_result(r, idx=i)
    return results

def print_result(r: dict, idx: int = 0):
    sep = "=" * 64
    print(sep)
    print(f"  Sample #{idx}")
    print(sep)
    print(f"  📂  Category : {r['predicted_category']:<24} "
          f"confidence = {r['category_confidence']:.2f}%")
    print(f"  🔧  Type     : {r['predicted_type']:<24} "
          f"confidence = {r['type_confidence']:.2f}%")
    print(f"\n  🏆  Top-5 Algorithm Predictions")
    print(f"  {'Rank':<5} {'Algorithm':<26} {'Probability':>12}   Bar")
    print(f"  {'-'*62}")
    for t in r["top5"]:
        bar    = "█" * max(1, int(t["probability"] / 2))
        marker = "  ◀ PREDICTED" if t["rank"] == 1 else ""
        print(f"  #{t['rank']:<4} {t['algorithm']:<26} "
              f"{t['probability']:>10.4f}%   {bar}{marker}")
    others = 100.0 - sum(t["probability"] for t in r["top5"])
    print(f"\n  (other {N_ALGO - 5} algorithms)               "
          f"{others:>10.4f}%")
    print()

