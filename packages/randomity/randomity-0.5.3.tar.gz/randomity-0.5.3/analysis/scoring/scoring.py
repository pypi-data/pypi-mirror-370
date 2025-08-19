import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

df = pd.read_csv('../data/vectors/vector.csv')

features = {
    'uniformity': ['chisqr_p', 'ks_p', 'freq_p', 'eqdist_diff'],
    'patterns': ['gap_p', 'serial_autocorrelation'],
    'periodicity': ['entropy_val', 'fft_max_magnitude']
}

def normalize_feature(series, invert=False):
    min_val, max_val = series.min(), series.max()
    if min_val == max_val:
        return np.zeros(len(series)) if invert else np.ones(len(series))
    normalized = (series - min_val) / (max_val - min_val)
    return normalized if invert else 1 - normalized

sub_scores = {}
for category, feats in features.items():
    category_scores = []
    for feat in feats:
        if feat in ['eqdist_diff', 'serial_autocorrelation', 'fft_max_magnitude']:
            normalized = normalize_feature(df[feat], invert=True)
        else:
            normalized = normalize_feature(df[feat], invert=False)
        category_scores.append(normalized)
    sub_scores[category] = np.mean(category_scores, axis=0)

randomness_score = np.mean([sub_scores['uniformity'], sub_scores['patterns'], sub_scores['periodicity']], axis=0)

fv_scored = df.copy()

fv_scored['uniformity_score'] = sub_scores['uniformity']
fv_scored['patterns_score'] = sub_scores['patterns']
fv_scored['periodicity_score'] = sub_scores['periodicity']
fv_scored['randomness_score'] = randomness_score

if not os.path.exists('results'):
    os.makedirs('results')

fv_scored.to_csv('results/feature_vector_scored.csv', index=False)

plt.figure(figsize=(10, 6))
for source in fv_scored['source'].unique():
    subset = fv_scored[fv_scored['source'] == source]
    plt.hist(subset['randomness_score'], bins=20, alpha=0.6, label=source, density=True)
plt.title("Randomness Score by Source")
plt.xlabel("Randomness Score (0-1)")
plt.ylabel("Density")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('results/randomness_score_by_source.png')

plt.figure(figsize=(10, 6))
for generator in fv_scored['generator'].unique():
    subset = fv_scored[fv_scored['generator'] == generator]
    plt.hist(subset['randomness_score'], bins=20, alpha=0.6, label=generator, density=True)
plt.title("Randomness Score by Generator")
plt.xlabel("Randomness Score (0-1)")
plt.ylabel("Density")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('results/randomness_score_by_generator.png')

