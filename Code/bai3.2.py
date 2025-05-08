import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Load the dataset
data = pd.read_csv('result.csv')

# Select features for clustering
features = [
    'Gls per 90', 'Ast per 90', 'xG per 90', 'xAG per 90', 'SCA90', 'GCA90',
    'Cmp%', 'TotDist', 'KP', 'PPA', 'Tkl', 'Blocks', 'Int',
    'Touches', 'PrgC', 'PrgP', 'PrgR', 'Carries'
]

# Extract the feature data
X = data[features].copy()

# Handle missing values (replace 'N/A' with 0, fill NaN with 0)
X = X.replace('N/A', 0)
X = X.fillna(0)

# Standardize the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Apply PCA to reduce to 2 dimensions
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# Apply K-means clustering with k=4
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
cluster_labels = kmeans.fit_predict(X_pca)

# Create the 2D cluster plot
plt.figure(figsize=(8, 6))
scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=cluster_labels, cmap='viridis', s=50)
plt.title('2D Cluster Plot of Players (PCA, k=4)')
plt.xlabel('Forward and Attacking Midfielder Ability')
plt.ylabel('Defender and Defensive Midfielder Ability')
plt.colorbar(scatter, label='Cluster')
plt.grid(True)

# Save the plot as PNG
plt.savefig('cluster_plot.png', format='png', dpi=300, bbox_inches='tight')
plt.close()

print("2D cluster plot has been saved as 'cluster_plot.png'.")