import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import math
import os

df = pd.read_csv('../data/vectors/vector.csv')

feature_cols = df.columns[4:].tolist()
features = df[feature_cols]

scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

pca = PCA()
pca_result = pca.fit_transform(features_scaled)

explained_variance = pca.explained_variance_ratio_
cumulative_variance = np.cumsum(explained_variance)
loadings = pca.components_.T

loadings_df = pd.DataFrame(loadings, index=feature_cols, columns=[f'PC{i+1}' for i in range(len(feature_cols))])

loadings_df.to_csv("output/pca_loadings.csv")
np.savetxt("output/pca_explained_variance.csv", explained_variance, delimiter=",")
np.savetxt("output/pca_transformed.csv", pca_result, delimiter=",")

if not os.path.exists('output'):
    os.makedirs('output')
if not os.path.exists('result'):
    os.makedirs('result')

plt.figure(figsize=(10, 6))
plt.plot(range(1, len(explained_variance) + 1), explained_variance, marker='o')
plt.xlabel("Number of Principal Components")
plt.ylabel("Explained Variance Ratio")
plt.title("Explained Variance Ratio by Principal Components")
plt.grid(True)
plt.tight_layout()
plt.savefig('output/explained_variance_ratio.png')

plt.figure(figsize=(10, 6))
plt.plot(range(1, len(explained_variance) + 1), cumulative_variance, marker='o')
plt.xlabel("Number of Principal Components")
plt.ylabel("Cumulative Explained Variance")
plt.title("Cumulative Explained Variance by Principal Components")
plt.grid(True)
plt.tight_layout()
plt.savefig('output/cumulative_explained_variance.png')

labels = df[['source', 'generator']]

pca_df = pd.DataFrame(pca_result, columns=[f'PC{i+1}' for i in range(pca_result.shape[1])])

combined_df = pd.concat([labels, pca_df[['PC1', 'PC2']]], axis=1)

plt.figure(figsize=(10, 6))
for source in combined_df['source'].unique():
    subset = combined_df[combined_df['source'] == source]
    plt.scatter(subset['PC1'], subset['PC2'], label=source, alpha=0.6)
plt.title("PCA of Features by Source")
plt.xlabel("PC1 (32.89% variance)")
plt.ylabel("PC2 (12.15% variance)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('result/pca_features_by_source.png')

plt.figure(figsize=(10, 6))
for generator in combined_df['generator'].unique():
    subset = combined_df[combined_df['generator'] == generator]
    plt.scatter(subset['PC1'], subset['PC2'], label=generator, alpha=0.6)
plt.title("PCA of Features by Generator")
plt.xlabel("PC1 (32.89% variance)")
plt.ylabel("PC2 (12.15% variance)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('result/pca_features_by_generator.png')

test_categories = {
    'Chi-Squared': ['chisqr_p', 'chisqr_X2.X-squared', 'chisqr_df.df'],
    'KS': ['ks_p', 'ks_D.D'],
    'Frequency': ['freq_p', 'freq_X2.X-squared', 'freq_df.df'],
    'Equidistribution': ['eqdist_empiricalMean', 'eqdist_diff'],
    'Gap': ['gap_p', 'gap_X2.X-squared', 'gap_df.df'],
    'Serial': ['serial_autocorrelation'],
    'Permutation': ['perm_observed_stat', 'perm_p'],
    'Entropy': ['entropy_val'],
    'FFT': ['fft_dominant_frequency', 'fft_dominant_period', 'fft_max_magnitude']
}

def plot_spider_chart(pcs, title, filename):
    category_scores = {}
    for test, features in test_categories.items():
        score = np.mean(np.abs(loadings_df.loc[features, pcs].values))
        category_scores[test] = score

    categories = list(category_scores.keys())
    values = list(category_scores.values())
    values += values[:1]

    N = len(categories)
    angles = [n / float(N) * 2 * math.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='tab:blue', alpha=0.25)
    ax.plot(angles, values, color='tab:blue', linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10)
    plt.title(title, size=14, pad=20)
    plt.savefig(f'result/{filename}.png')

plot_spider_chart([f'PC{i+1}' for i in range(20)], "Average Absolute Loadings per Test (PC1-PC20)", "perTest_(PC1-PC20)")

plot_spider_chart(['PC1', 'PC2', 'PC3'], "Average Absolute Loadings per Test (PC1-PC3)", "perTest_(PC1-PC3)")
